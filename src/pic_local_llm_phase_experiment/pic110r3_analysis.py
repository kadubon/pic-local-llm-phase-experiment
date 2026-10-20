"""Offline independent R3 grading, paired inference and complete attempt accounting."""

from __future__ import annotations

import argparse
import random
import time
from collections import Counter
from datetime import datetime
from typing import Any

from pic_local_llm_phase_experiment.pic110_analysis import paired, wilson
from pic_local_llm_phase_experiment.pic110r3_common import (
    DATA,
    OUT,
    ROOT,
    preservation,
    read,
    sha,
    write,
)
from pic_local_llm_phase_experiment.pic110r3_oracle import evaluate, gold


def collect() -> tuple[list[dict], dict]:
    tasks = read(OUT / "setup/schedule.json")
    delivered, trust = read(DATA / "delivery.json"), read(DATA / "trusted_manifest.json")
    expected = read(OUT / "setup/gold.json")
    rows = []
    states = {}
    for panel in ("pilot", "confirmatory"):
        status_file = OUT / panel / "panel.json"
        states[panel] = read(status_file) if status_file.exists() else {"status": "NOT_RUN"}
        if states[panel]["status"] == "RUNNING":
            raise ValueError("Refuse grading while inference is running")
    for task in tasks:
        tid, panel = task["task_id"], task["panel"]
        truth = gold(task, delivered[task["source_id"]], trust)
        if truth != expected[tid]:
            raise ValueError("private gold changed")
        td = OUT / panel / tid
        for arm in ("initial", "A", "B", "C"):
            folder = td / arm
            record = (
                read(folder / "record.json")
                if (folder / "record.json").exists()
                else {"attempt_status": "NOT_RUN"}
            )
            text = (
                (folder / "answer.txt").read_text(encoding="utf-8")
                if (folder / "answer.txt").exists()
                else None
            )
            if text is not None and sha(text.encode()) != record["output_artifact_hash"]:
                raise ValueError("raw answer hash differs")
            start = time.perf_counter()
            grade = evaluate(text, truth, evidence_access=arm in {"B", "C"})
            grade_seconds = time.perf_counter() - start
            if record["attempt_status"] != "OK":
                grade["success"] = grade["supported_completion"] = False
            gate = (
                read(folder / "final_gate.json")
                if (folder / "final_gate.json").exists()
                else {"admitted_complete": False, "evidence_supported": False}
            )
            gate_wrong = bool(
                gate["admitted_complete"]
                and (
                    grade["unsupported_completion"] is not False
                    or grade["citation_only_failure"] is True
                    or not grade["format_conformant"]
                )
            )
            rows.append(
                {
                    "task_id": tid,
                    "panel": panel,
                    "family": task["family"],
                    "dependency_group": task["dependency_group"],
                    "order": task["order"],
                    "condition": arm,
                    "determinable": truth["complete"],
                    "oracle": grade,
                    "gate": gate,
                    "gate_unsupported_completion": gate_wrong,
                    "supported_completion_yield": bool(
                        grade["supported_completion"] and gate["admitted_complete"]
                    ),
                    "evaluator_seconds": grade_seconds,
                    **{
                        k: record.get(k)
                        for k in (
                            "attempt_status",
                            "model_name",
                            "model_digest",
                            "seed",
                            "prompt_hash",
                            "input_artifact_hash",
                            "shared_initial_hash",
                            "output_artifact_hash",
                            "token_usage",
                            "elapsed_time",
                            "ollama_timing_ns",
                            "cached_input_tokens",
                            "resource_before",
                            "resource_after",
                        )
                    },
                    "energy_joules": None,
                    "monetary_cost": None,
                    "FLOPs": None,
                }
            )
    return rows, states


def comparison(
    rows: list[dict], left: str, right: str, endpoint: str, *, eligible: bool = False
) -> dict:
    a = {
        r["task_id"]: r
        for r in rows
        if r["condition"] == left and (r["determinable"] or not eligible)
    }
    b = {
        r["task_id"]: r
        for r in rows
        if r["condition"] == right and (r["determinable"] or not eligible)
    }

    def value(row: dict):
        return row.get(endpoint, row["oracle"].get(endpoint))

    ids = sorted(a)
    observable = [tid for tid in ids if type(value(a[tid])) is bool and type(value(b[tid])) is bool]
    p = paired(
        [value(a[t]) for t in observable], [value(b[t]) for t in observable], 11032027, 20000
    )
    p.update(
        left=left,
        right=right,
        endpoint=endpoint,
        planned_pairs=len(ids),
        unknown_pairs=len(ids) - len(observable),
        estimand=f"{right} minus {left}",
        unknown_pair_risk_difference_bounds=[
            (
                sum(int(value(b[t])) - int(value(a[t])) for t in observable)
                - len(ids)
                + len(observable)
            )
            / len(ids),
            (
                sum(int(value(b[t])) - int(value(a[t])) for t in observable)
                + len(ids)
                - len(observable)
            )
            / len(ids),
        ]
        if ids
        else None,
    )
    # Resample four whole families; this sensitivity is not a population guarantee.
    families = sorted({r["family"] for r in rows})
    groups = {f: [t for t in observable if a[t]["family"] == f] for f in families}
    rng = random.Random(11032028)
    samples = []
    for _ in range(20000):
        selected = [t for f in rng.choices(families, k=len(families)) for t in groups[f]]
        if selected:
            samples.append(
                sum(int(value(b[t])) - int(value(a[t])) for t in selected) / len(selected)
            )
    samples.sort()
    p["family_cluster_bootstrap_sensitivity_95"] = (
        [samples[int(len(samples) * 0.025)], samples[int(len(samples) * 0.975) - 1]]
        if samples
        else None
    )
    p["family_cluster_bootstrap_degenerate"] = bool(samples and samples[0] == samples[-1])
    return p


def summarize(rows: list[dict]) -> dict:
    arms = {}
    for arm in ("initial", "A", "B", "C"):
        selected = [r for r in rows if r["condition"] == arm]
        n = len(selected)
        obs = [r for r in selected if r["oracle"]["unsupported_completion"] is not None]
        determined = [r for r in selected if r["determinable"]]
        success = sum(r["oracle"]["success"] for r in selected)
        arms[arm] = {
            "planned": n,
            "success": success,
            "success_wilson_95": wilson(success, n),
            "unsupported_completion": sum(
                r["oracle"]["unsupported_completion"] is True for r in selected
            ),
            "unsupported_observed": len(obs),
            "unsupported_unknown": n - len(obs),
            "gate_unsupported_completion": sum(r["gate_unsupported_completion"] for r in selected),
            "supported_yield_count": sum(r["supported_completion_yield"] for r in determined),
            "supported_yield_denominator": len(determined),
            "format_conformant": sum(r["oracle"]["format_conformant"] for r in selected),
            "correct_abstention": sum(r["oracle"]["correct_abstention"] is True for r in selected),
            "abstention_denominator": n - len(determined),
            "obligations_correct": sum(r["oracle"]["obligations_correct"] for r in selected),
            "lost_obligations": sum(len(r["oracle"]["lost_obligations"] or []) for r in selected),
            "citation_only_failure": sum(
                r["oracle"]["citation_only_failure"] is True for r in selected
            ),
            "attempt_states": dict(Counter(r["attempt_status"] for r in selected)),
        }
    comparisons = {}
    for left, right in (("B", "C"), ("A", "B")):
        comparisons[f"{right}_minus_{left}"] = {
            key: comparison(rows, left, right, key, eligible=key == "supported_completion_yield")
            for key in (
                "success",
                "unsupported_completion",
                "gate_unsupported_completion",
                "supported_completion_yield",
            )
        }
    families = {}
    for f in sorted({r["family"] for r in rows}):
        families[f] = {
            arm: {
                "success": sum(
                    r["oracle"]["success"]
                    for r in rows
                    if r["family"] == f and r["condition"] == arm
                ),
                "planned": sum(r["family"] == f and r["condition"] == arm for r in rows),
            }
            for arm in "ABC"
        }
    return {"arms": arms, "comparisons": comparisons, "families": families}


def inspect_evidence(tasks: list[dict]) -> list[dict]:
    output = []
    for task in tasks:
        td = OUT / task["panel"] / task["task_id"]
        if not (td / "common_receipt.json").exists():
            output.append({"task_id": task["task_id"], "panel": task["panel"], "status": "NOT_RUN"})
            continue
        receipt, pic, reuse = (
            read(td / "common_receipt.json"),
            read(td / "pic_feedback/actual_pic.json"),
            read(td / "reuse.json"),
        )
        final_file = td / "C/final_runtime.json"
        final = read(final_file) if final_file.exists() else None
        row = {
            "task_id": task["task_id"],
            "panel": task["panel"],
            "family": task["family"],
            "status": "OBSERVED",
            "receipt": receipt,
            "native": pic["native"],
            "native_calls": pic["native_calls"],
            "native_reused": pic["native_reused"],
            "reused_verified_packet_id": pic["reused_verified_packet_id"],
            "raw_resolution": pic["raw_resolution"],
            "raw_discharge": pic["raw_discharge"],
            "evidence_batch": pic["evidence_batch"],
            "protected_discharge": pic["protected_discharge"],
            "raw_packet": pic["raw_packet"],
            "protected_packet": pic["protected_packet"],
            "runtime": {
                k: pic["runtime"].get(k)
                for k in (
                    "accepted",
                    "operationally_usable",
                    "settled",
                    "missing_obligations",
                    "residual_ledger",
                    "verified_packet_count",
                    "evidence_resolution_batch",
                )
            },
            "pic_ready": pic["pic_ready"],
            "pic_seconds": pic["elapsed_seconds"],
            "final_pic_seconds": final["elapsed_seconds"] if final else None,
            "final_pic_flags": {
                k: final["report"].get(k)
                for k in ("accepted", "operationally_usable", "settled", "missing_obligations")
            }
            if final
            else None,
            "reuse": {k: v for k, v in reuse.items() if k != "producer_pic"},
            "producer_pic_seconds": reuse["producer_pic"]["elapsed_seconds"]
            if reuse["producer_pic"]
            else 0,
            "producer_native_calls": reuse["producer_pic"]["native_calls"]
            if reuse["producer_pic"]
            else 0,
        }
        output.append(row)
    return output


def costs(rows: list[dict], evidence: list[dict]) -> dict:
    arms: dict[str, Any] = {}
    for arm in "ABC":
        selected = [r for r in rows if r["condition"] == arm]
        initials = [r for r in rows if r["condition"] == "initial"]
        model = (
            sum(r["elapsed_time"] or 0 for r in selected)
            + sum(r["elapsed_time"] or 0 for r in initials) / 3
        )
        verifier = (
            sum(
                e["receipt"]["elapsed_seconds"]
                + (e["reuse"]["producer"]["elapsed_seconds"] if e["reuse"]["producer"] else 0)
                for e in evidence
                if e["status"] == "OBSERVED"
            )
            / 2
            if arm in "BC"
            else 0
        )
        pic = (
            sum(
                e["pic_seconds"] + e["producer_pic_seconds"] + (e["final_pic_seconds"] or 0)
                for e in evidence
                if e["status"] == "OBSERVED"
            )
            if arm == "C"
            else 0
        )

        def tokens(group, key):
            values = [(r.get("token_usage") or {}).get(key) for r in group]
            return sum(values) if values and all(type(v) is int for v in values) else None

        usage = {}
        for key in ("input", "output", "total"):
            rev, ini = tokens(selected, key), tokens(initials, key)
            usage[key] = rev + ini / 3 if rev is not None and ini is not None else None
        arms[arm] = {
            "allocated_seconds": model + verifier + pic,
            "model_seconds": model,
            "shared_verifier_seconds": verifier,
            "pic_seconds": pic,
            "allocated_tokens": usage,
            "timing_records": sum(r["elapsed_time"] is not None for r in selected),
            "planned": len(selected),
        }
    joint = sorted(
        set(r["task_id"] for r in rows if r["condition"] == "B" and r["oracle"]["success"])
        & set(r["task_id"] for r in rows if r["condition"] == "C" and r["oracle"]["success"])
    )
    joint_rows = [r for r in rows if r["task_id"] in joint]
    joint_evidence = [e for e in evidence if e["task_id"] in joint]
    joint_costs = {}
    for arm in "BC":
        base = sum(r["elapsed_time"] or 0 for r in joint_rows if r["condition"] == arm)
        base += sum(r["elapsed_time"] or 0 for r in joint_rows if r["condition"] == "initial") / 3
        base += (
            sum(
                e["receipt"]["elapsed_seconds"]
                + (e["reuse"]["producer"]["elapsed_seconds"] if e["reuse"]["producer"] else 0)
                for e in joint_evidence
                if e["status"] == "OBSERVED"
            )
            / 2
        )
        if arm == "C":
            base += sum(
                e["pic_seconds"] + e["producer_pic_seconds"] + (e["final_pic_seconds"] or 0)
                for e in joint_evidence
                if e["status"] == "OBSERVED"
            )
        joint_costs[arm] = base
    return {
        "arms": arms,
        "joint_success_C_B": {
            "task_ids": joint,
            "count": len(joint),
            "allocated_seconds": joint_costs,
        },
        "allocation": (
            "One third shared initial per arm; half common independent verification per B/C; "
            "C includes producer/consumer and final PIC. No-cache diagnostic excluded; "
            "allocated sums omit I/O/orchestration."
        ),
        "C_over_B_seconds": arms["C"]["allocated_seconds"] / arms["B"]["allocated_seconds"]
        if arms["B"]["allocated_seconds"]
        else None,
        "energy_joules": None,
        "GPU_utilization_continuous": None,
        "FLOPs": None,
        "monetary_cost": None,
    }


def analyze() -> dict[str, Any]:
    rows, states = collect()
    evidence = inspect_evidence(read(OUT / "setup/schedule.json"))
    panels = {}
    for panel in ("pilot", "confirmatory"):
        selected = [r for r in rows if r["panel"] == panel]
        ev = [r for r in evidence if r["panel"] == panel]
        panels[panel] = {
            **summarize(selected),
            "costs": costs(selected, ev),
            "execution": states[panel],
        }
    status = (
        "COMPLETED" if all(s["status"] == "COMPLETED" for s in states.values()) else "INCOMPLETE"
    )
    result: dict[str, Any] = {
        "status": status,
        "panels": panels,
        "rows": rows,
        "evidence": evidence,
        "campaign": read(OUT / "campaign.json") if (OUT / "campaign.json").exists() else None,
        "preservation": preservation(),
        "gold_independence": (
            "Exact rational/index oracle reads frozen source delivery and trusted authority "
            "manifest, never PIC or verifier conclusions"
        ),
        "registration": (
            "Local pre-inference commits; not independently timestamped public preregistration"
        ),
    }
    if result["campaign"] and states["confirmatory"].get("finished_utc"):
        result["campaign_span_seconds"] = (
            datetime.fromisoformat(states["confirmatory"]["finished_utc"]).timestamp()
            - result["campaign"]["started_epoch"]
        )
    result["environment"] = {
        k: read(OUT / "setup/inspection.json")[k]
        for k in (
            "head",
            "pic_version",
            "wheel_sha256",
            "installed_content_sha256",
            "installed_wheel_files_verified",
            "python",
            "ollama_version",
        )
    }
    write(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R3.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-public", action="store_true")
    args = parser.parse_args()
    if args.check_public:
        saved = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R3.json")
        for panel in ("pilot", "confirmatory"):
            actual = summarize([r for r in saved["rows"] if r["panel"] == panel])
            for key in ("arms", "comparisons", "families"):
                assert actual[key] == saved["panels"][panel][key], key
        print("R3 public arithmetic PASS; no model/PIC calls or private raw files")
    else:
        data = analyze()
        print({"status": data["status"], "primary": data["panels"]["confirmatory"]["arms"]})


if __name__ == "__main__":
    main()
