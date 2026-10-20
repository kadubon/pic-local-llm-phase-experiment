"""Frozen independent scoring, episode inference and public arithmetic for R4."""

from __future__ import annotations

import argparse
import itertools
import random
import statistics
from collections import Counter

from pic_local_llm_phase_experiment.pic110_analysis import paired
from pic_local_llm_phase_experiment.pic110r4_common import (
    DATA,
    OUT,
    ROOT,
    canonical,
    environment,
    frozen,
    preservation,
    read,
    sha,
    write,
)
from pic_local_llm_phase_experiment.pic110r4_oracle import expected, score

ARMS = ("G_minimal", "P_minimal", "P_full")
FIELDS = (
    "decision_correct",
    "supported_success",
    "contract_success",
    "unsupported_completion",
    "unsafe_admission",
    "citation_valid",
    "obligations_correct",
    "format_conformant",
)


def collect() -> tuple[list[dict], list[dict], dict]:
    rows = []
    evidence = []
    panels = {}
    gold = read(OUT / "setup/gold.json")
    cases = read(DATA / "cases.json")
    for panel in ("pilot", "confirmatory"):
        file = OUT / panel / "panel.json"
        panels[panel] = read(file) if file.exists() else {"status": "NOT_RUN"}
        assert panels[panel]["status"] != "RUNNING"
    for case in cases:
        truth = expected(case)
        assert truth == gold[case["task_id"]]
        td = OUT / case["panel"] / case["task_id"]
        acqfile = td / "evidence/acquisition.json"
        acquisition = read(acqfile) if acqfile.exists() else None
        if acquisition:
            from pic_local_llm_phase_experiment.pic110r4_backend import gate, states

            probes = []
            fail = truth["negative_witnesses"]
            witness = fail[:1] if fail else truth["evidence_ids"] if truth["complete"] else []
            correct = {
                "decision": truth["decision"],
                "complete": truth["complete"],
                "evidence": witness,
                "unresolved": truth["unresolved"],
            }
            declarations = [correct]
            for decision in ("COMPLIANT", "NONCOMPLIANT"):
                for refs in ([], truth["evidence_ids"], ["draft:ready"]):
                    declarations.append(
                        {"decision": decision, "complete": True, "evidence": refs, "unresolved": []}
                    )
            for declaration in declarations:
                probe_text = canonical(declaration).decode()
                for backend in ("generic", "pic"):
                    g = gate(probe_text, acquisition, backend)
                    grading = score(probe_text, truth, admitted=g["admitted_complete"])
                    probes.append(
                        {
                            "backend": backend,
                            "declaration": declaration,
                            "admitted": g["admitted_complete"],
                            "unsafe_admission": grading["unsafe_admission"],
                        }
                    )
            evidence.append(
                {
                    "task_id": case["task_id"],
                    "panel": case["panel"],
                    "episode": case["episode"],
                    "oracle_statuses": truth["statuses"],
                    "generic_statuses": states(acquisition, "generic"),
                    "pic_statuses": states(acquisition, "pic"),
                    "domain_calls": sum(r["domain_calls"] for r in acquisition["receipts"]),
                    "cache_hits": sum(r["cache_hit"] for r in acquisition["receipts"]),
                    "native_calls": sum(p["native_calls"] for p in acquisition["pics"]),
                    "raw_route_accepts": sum(
                        p["raw_resolution"]["accepted"] for p in acquisition["pics"]
                    ),
                    "protected_ready": sum(p["pic_ready"] for p in acquisition["pics"]),
                    "probes": probes,
                }
            )
        for arm in ARMS:
            kind = "full" if arm == "P_full" else "minimal"
            backend = "generic" if arm == "G_minimal" else "pic"
            fd = td / kind
            rec = (
                read(fd / "record.json")
                if (fd / "record.json").exists()
                else {"attempt_status": "NOT_RUN"}
            )
            text = (
                (fd / "answer.txt").read_text(encoding="utf-8")
                if (fd / "answer.txt").exists()
                else None
            )
            if text is not None:
                assert acquisition is not None
                assert sha(text.encode()) == rec["output_artifact_hash"]
                request = read(fd / "request.json")
                material = acquisition["detailed" if kind == "full" else "compact"]
                exact = case["prompt"] + "\nVERIFIED MATERIAL\n" + canonical(material).decode()
                assert request["prompt"] == exact and sha(exact.encode()) == rec["prompt_hash"]
            gatefile = fd / f"gate_{backend}.json"
            g = (
                read(gatefile)
                if gatefile.exists()
                else {"admitted_complete": False, "elapsed_seconds": 0}
            )
            grade = score(text, truth, admitted=g["admitted_complete"])
            if rec["attempt_status"] != "OK":
                for key in (
                    "supported_success",
                    "contract_success",
                    "supported_yield",
                    "decision_correct",
                ):
                    grade[key] = False
            runtimefile = fd / "final_pic_runtime.json"
            runtime = read(runtimefile) if runtimefile.exists() else None
            model = rec.get("elapsed_time")
            common = acquisition["generic_seconds"] if acquisition else None
            extra = (
                acquisition["pic_seconds"] + runtime["elapsed_seconds"]
                if acquisition and runtime and backend == "pic"
                else 0
            )
            rows.append(
                {
                    "task_id": case["task_id"],
                    "panel": case["panel"],
                    "episode": case["episode"],
                    "step": case["step"],
                    "arm": arm,
                    "determinable": truth["complete"],
                    "expected_decision": truth["decision"],
                    "grade": grade,
                    "admitted": g["admitted_complete"],
                    "attempt_status": rec["attempt_status"],
                    "model_seconds": model,
                    "common_verifier_seconds": common,
                    "pic_seconds": extra,
                    "gate_seconds": g["elapsed_seconds"],
                    "standalone_workflow_seconds": model + common + extra + g["elapsed_seconds"]
                    if model is not None and common is not None
                    else None,
                    "prompt_hash": rec.get("prompt_hash"),
                    "output_hash": rec.get("output_artifact_hash"),
                    "tokens": rec.get("token_usage"),
                    "ollama_timing_ns": rec.get("ollama_timing_ns"),
                    "global_runtime_status": {
                        k: runtime["report"].get(k)
                        for k in ("accepted", "operationally_usable", "settled")
                    }
                    if runtime and backend == "pic"
                    else None,
                }
            )
    return rows, evidence, panels


def contrast(rows: list[dict], left: str, right: str, endpoint: str) -> dict:
    a = {r["task_id"]: r for r in rows if r["arm"] == left}
    b = {r["task_id"]: r for r in rows if r["arm"] == right}
    ids = sorted(a)
    differences = {
        tid: int(b[tid]["grade"][endpoint]) - int(a[tid]["grade"][endpoint]) for tid in ids
    }
    episodes = sorted({a[tid]["episode"] for tid in ids})
    grouped = {
        ep: [v for tid, v in differences.items() if a[tid]["episode"] == ep] for ep in episodes
    }
    values = [sum(grouped[ep]) / len(grouped[ep]) for ep in episodes]
    observed = statistics.mean(values)
    null = [
        statistics.mean(v * s for v, s in zip(values, signs, strict=True))
        for signs in itertools.product((-1, 1), repeat=len(values))
    ]
    rng = random.Random(11042027)
    bootstrap = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(20000))
    return {
        "left": left,
        "right": right,
        "endpoint": endpoint,
        "estimand": f"{right} minus {left}",
        "planned_pairs": len(ids),
        "episode_count": len(episodes),
        "difference": observed,
        "wins": sum(d == 1 for d in differences.values()),
        "ties": sum(d == 0 for d in differences.values()),
        "losses": sum(d == -1 for d in differences.values()),
        "episode_differences": dict(zip(episodes, values, strict=True)),
        "episode_sign_flip_two_sided_p": sum(abs(v) >= abs(observed) - 1e-12 for v in null)
        / len(null),
        "episode_bootstrap_95_descriptive": [bootstrap[500], bootstrap[19499]],
        "episode_bootstrap_degenerate": bootstrap[0] == bootstrap[-1],
        "task_independence_sensitivity_only": paired(
            [a[t]["grade"][endpoint] for t in ids],
            [b[t]["grade"][endpoint] for t in ids],
            11042028,
            20000,
        ),
    }


def summarize(rows: list[dict]) -> dict:
    arms = {}
    for arm in ARMS:
        selected = [r for r in rows if r["arm"] == arm]
        determined = [r for r in selected if r["determinable"]]
        arms[arm] = {
            "planned": len(selected),
            **{f: sum(r["grade"][f] is True for r in selected) for f in FIELDS},
            "unsupported_unknown": sum(
                r["grade"]["unsupported_completion"] is None for r in selected
            ),
            "supported_yield": sum(r["grade"]["supported_yield"] for r in determined),
            "supported_yield_denominator": len(determined),
            "attempt_states": dict(Counter(r["attempt_status"] for r in selected)),
            "model_seconds": sum(r["model_seconds"] or 0 for r in selected),
            "pic_seconds": sum(r["pic_seconds"] for r in selected),
            "standalone_workflow_seconds": sum(
                r["standalone_workflow_seconds"] or 0 for r in selected
            ),
            "timing_missing": sum(r["model_seconds"] is None for r in selected),
            "input_tokens": sum((r["tokens"] or {}).get("input") or 0 for r in selected),
            "output_tokens": sum((r["tokens"] or {}).get("output") or 0 for r in selected),
        }
    comparisons = {
        "feedback_primary": contrast(rows, "P_minimal", "P_full", "supported_success"),
        "feedback_contract_secondary": contrast(rows, "P_minimal", "P_full", "contract_success"),
        "backend_yield_secondary": contrast(rows, "G_minimal", "P_minimal", "supported_yield"),
        "backend_unsafe_secondary": contrast(rows, "G_minimal", "P_minimal", "unsafe_admission"),
    }
    return {"arms": arms, "comparisons": comparisons}


def reuse_summary(cases: list[dict]) -> list[dict]:
    rows = []
    for case in cases:
        runs = case["runs"]
        producer = runs["producer"]["parent_wall_seconds"]

        def outcomes(mode, runs=runs, case=case):
            results = runs[mode]["worker"]["results"]
            return all(
                r["decision"] == "COMPLIANT"
                and r["trusted"]
                and r["sufficient"]
                and (case["backend"] != "pic" or r["pic_ready"])
                for r in results
            )

        rows.append(
            {
                **{k: case[k] for k in ("name", "size", "fanout", "repeat", "backend")},
                "cached_total_seconds": producer + runs["cached"]["parent_wall_seconds"],
                "no_cache_total_seconds": producer + runs["no_cache"]["parent_wall_seconds"],
                "cached_consumer_seconds": runs["cached"]["parent_wall_seconds"],
                "no_cache_consumer_seconds": runs["no_cache"]["parent_wall_seconds"],
                "cached_core_seconds": runs["cached"]["worker"]["core_elapsed_seconds"],
                "no_cache_core_seconds": runs["no_cache"]["worker"]["core_elapsed_seconds"],
                "cached_correct": outcomes("cached"),
                "no_cache_correct": outcomes("no_cache"),
                "domain_calls_saved": sum(
                    r["domain_calls"] for r in runs["no_cache"]["worker"]["results"]
                )
                - sum(r["domain_calls"] for r in runs["cached"]["worker"]["results"]),
                "native_calls_saved": sum(
                    r["native_calls"] for r in runs["no_cache"]["worker"]["results"]
                )
                - sum(r["native_calls"] for r in runs["cached"]["worker"]["results"]),
                "cross_process_packet_references": sum(
                    bool(r["verified_packet_dependency"])
                    for r in runs["cached"]["worker"]["results"]
                ),
            }
        )
    return rows


def render(summary: dict) -> str:
    main = summary["confirmatory"]
    p = main["comparisons"]["feedback_primary"]
    lines = [
        "# PIC 1.1.0 R4: backend, feedback and reuse mechanisms",
        "",
        f"Execution: {summary['execution_status']}. "
        "PIC 1.1.0 and its installed 617 payload files are unchanged.",
        "",
        "## Design and interpretation",
        "",
        "G_minimal and P_minimal consume the exact same generated answer from an identical prompt. "
        "They are paired backend replays, not independent model samples. P_full adds "
        "actual PIC detail "
        "to the same receipt facts. Its effect includes representation, auxiliary runtime "
        "information "
        "and prompt length; it is not a pure token-length intervention. All finite routes "
        "are selected "
        "by the orchestrator. Trust/issuer/task/recipient/TTL policy is common and external.",
        "",
        "Thirty-two main decisions form eight four-step episodes with three sources each. "
        "Pilot is one separate four-step episode. Canonical ID adherence is a secondary endpoint; "
        "the primary is correct decision/flag with sufficient authorized evidence. "
        "Source updates, partial observations and negative witnesses are kept distinct.",
        "",
        "## Confirmatory results",
        "",
        "| Endpoint | G minimal | P minimal | P full |",
        "| --- | ---: | ---: | ---: |",
    ]
    for field in (
        "decision_correct",
        "supported_success",
        "contract_success",
        "unsupported_completion",
        "unsafe_admission",
        "supported_yield",
        "obligations_correct",
    ):
        lines.append(f"| {field} | " + " | ".join(str(main["arms"][a][field]) for a in ARMS) + " |")
    lines.extend(
        [
            "",
            f"Primary P_full minus P_minimal: {p['difference'] * 100:.2f} percentage points; "
            f"wins/ties/losses {p['wins']}/{p['ties']}/{p['losses']}. "
            f"Episode sign-flip p={p['episode_sign_flip_two_sided_p']}; "
            f"episode bootstrap descriptive interval {p['episode_bootstrap_95_descriptive']}.",
            "",
            "Only eight authored episodes are independent blocks under the working model. "
            "Sign-flip "
            "inference assumes blockwise exchangeability under the null. Bootstrap intervals are "
            "small-sample descriptions; a degenerate interval does not establish equivalence. "
            "Task independent exact estimates are explicitly sensitivity analyses, not "
            "primary inference.",
            "",
            "## Cost",
            "",
            "| Arm | Model seconds | PIC seconds | Standalone workflow seconds | Input / "
            "output tokens |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for arm in ARMS:
        a = main["arms"][arm]
        lines.append(
            f"| {arm} | {a['model_seconds']:.3f} | {a['pic_seconds']:.3f} | "
            f"{a['standalone_workflow_seconds']:.3f} | {a['input_tokens']} / {a['output_tokens']} |"
        )
    lines.extend(
        [
            "",
            "Standalone times assign a full observed minimal generation to each hypothetical "
            "backend workflow; their sum is not actual campaign compute. The compact "
            "inference is physically "
            "executed only once per case. Setup is shared between P variants. "
            "Campaign metadata records actual attempts and totals. I/O/orchestration is "
            "not included in "
            "these standalone sums. Prompt order is balanced across episodes; prefix "
            "caching and background "
            "load are not isolated. Energy, continuous GPU use, FLOPs and monetary cost "
            "remain unknown.",
            "",
            "## Reuse in separate processes",
            "",
            "Each producer persists a content-pinned cache; each consumer starts a fresh "
            "interpreter. "
            "Both backends recheck current source digest, issuer, task, recipient and TTL. Native "
            "checks may be reused; PIC resolution/promotion/runtime still execute. No "
            "artificial sleep "
            "or simulated verification cost is added. Positive end-to-end savings include producer "
            "cost, process startup and persisted I/O; core timings are separate.",
            "",
            "| Backend | Samples | Fanout | Cached / no-cache total seconds (two repeats) "
            "| Correct |",
            "| --- | ---: | ---: | --- | --- |",
        ]
    )
    for backend in ("generic", "pic"):
        for size in (16, 4096, 65536):
            for fanout in (1, 8):
                selected = [
                    r
                    for r in summary["reuse"]
                    if r["backend"] == backend and r["size"] == size and r["fanout"] == fanout
                ]
                times = ", ".join(
                    f"{r['cached_total_seconds']:.4f}/{r['no_cache_total_seconds']:.4f}"
                    for r in selected
                )
                correct = (
                    all(r["cached_correct"] and r["no_cache_correct"] for r in selected)
                    if selected
                    else None
                )
                lines.append(
                    f"| {backend} | {size} | {fanout} | {times or 'NOT_RUN'} | {correct} |"
                )
    lines.extend(
        [
            "",
            "Two repeats on a fixed local grid cannot establish a general break-even threshold. "
            "PIC versus its own no-cache path and PIC versus the generic cache are "
            "separate comparisons. "
            "Skipped calls are not themselves an efficiency benefit. This workload tests "
            "real finite "
            "array verification, not arbitrary expensive external proof systems.",
            "",
            "## Boundaries and preservation",
            "",
            "The common independent verifier supplies per-source verdicts but no aggregate "
            "task verdict. "
            "A complete negative result needs only one failing witness; missing irrelevant "
            "sources do not "
            "invalidate that proof. Schema, reference validity and obligation IDs remain "
            "separately visible. "
            "PIC raw metadata acceptance and protected final admission remain distinct. "
            "Development packet "
            "identity and production content-reference envelope policy are mixed "
            "explicitly as in R3; "
            "production cryptographic identity is not tested. Observed time is not the "
            "simulated policy "
            "clock. These are fixed pipelines and separate producer/consumer processes, "
            "not autonomous agents.",
            "",
            "Backend replay intentionally removes the model-channel difference. It "
            "measures additional "
            "backend rejection/acceptance and cost under the same trust policy. Because "
            "the generic gate "
            "already implements the task proof rule, backend parity here is a conformance "
            "observation, "
            "not a population equivalence test or proof of improved intelligence. Causal "
            "effects of "
            "individual PIC fields, general auditability, engineering effort and "
            "collective intelligence "
            "remain unmeasured. No R1/R2/R3 observations are pooled.",
            "",
            "Existing files remain byte-identical under the pre-R4 snapshot; the installed "
            "PIC payload is "
            "checked before and after execution. Local pre-inference commits are not "
            "independently public "
            "timestamped registration. Raw prompts/responses and exact runtime artifacts "
            "remain private. "
            "Public rows support arithmetic checking, not answer-level regrading without "
            "raw access.",
            "",
            "[Protocol](PROTOCOL_PIC_1_1_0_R4.md), "
            "[reproduction](REPRODUCIBILITY_PIC_1_1_0_R4.md), "
            "[summary](EXPERIMENT_SUMMARY_PIC_1_1_0_R4.json).",
        ]
    )
    return "\n".join(lines) + "\n"


def analyze() -> dict:
    frozen("main")
    preservation()
    environment()
    rows, evidence, panels = collect()
    reusefile = OUT / "reuse/cases.json"
    reuse = reuse_summary(read(reusefile) if reusefile.exists() else [])
    reusepanel = (
        read(OUT / "reuse/panel.json")
        if (OUT / "reuse/panel.json").exists()
        else {"status": "NOT_RUN"}
    )
    complete = all(s["status"] == "COMPLETED" for s in [*panels.values(), reusepanel])
    summary = {
        "schema": "pic110r4-v1",
        "execution_status": "COMPLETED" if complete else "INCOMPLETE",
        "panels": panels,
        "reuse_panel": reusepanel,
        "campaign": read(OUT / "campaign.json"),
        "pilot": summarize([r for r in rows if r["panel"] == "pilot"]),
        "confirmatory": summarize([r for r in rows if r["panel"] == "confirmatory"]),
        "rows": rows,
        "evidence": evidence,
        "reuse": reuse,
        "energy_joules": None,
        "FLOPs": None,
        "monetary_cost": None,
    }
    write(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R4.json", summary, exclusive=True)
    path = ROOT / "docs/EXPERIMENT_REPORT_PIC_1_1_0_R4.md"
    assert not path.exists()
    path.write_text(render(summary), encoding="utf-8")
    return summary


def check_public() -> None:
    saved = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R4.json")
    for panel in ("pilot", "confirmatory"):
        assert summarize([r for r in saved["rows"] if r["panel"] == panel]) == saved[panel]
    print("R4 public arithmetic PASS; no model calls or private raw reads")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-public", action="store_true")
    check_public() if parser.parse_args().check_public else analyze()
