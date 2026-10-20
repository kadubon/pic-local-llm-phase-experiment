"""Recompute all estimates from preserved files; no model/PIC calls or outcome selection."""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from typing import Any

from pic_local_llm_phase_experiment.pic110_oracle import evaluate
from pic_local_llm_phase_experiment.pic110_runner import OUT, ROOT, read, settings, sha, write


def wilson(k: int, n: int) -> list[float] | None:
    if not n:
        return None
    z = 1.959963984540054
    p, d = k / n, 1 + z * z / n
    center = (p + z * z / (2 * n)) / d
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, center - radius), min(1.0, center + radius)]


def _binomial_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


def cp_interval(k: int, n: int, alpha: float = 0.025) -> list[float]:
    """Exact binomial interval. 97.5% for Bonferroni difference construction."""
    lower, upper = 0.0, 1.0
    if k:
        lo, hi = 0.0, 1.0
        for _ in range(64):
            mid = (lo + hi) / 2
            if 1 - _binomial_cdf(k - 1, n, mid) < alpha / 2:
                lo = mid
            else:
                hi = mid
        lower = (lo + hi) / 2
    if k < n:
        lo, hi = 0.0, 1.0
        for _ in range(64):
            mid = (lo + hi) / 2
            if _binomial_cdf(k, n, mid) > alpha / 2:
                lo = mid
            else:
                hi = mid
        upper = (lo + hi) / 2
    return [lower, upper]


def paired(a: list[bool], b: list[bool], seed: int, replicates: int) -> dict[str, Any]:
    n = len(a)
    if n != len(b) or not n:
        return {"n": n, "difference_B_minus_A": None, "conservative_exact_95_ci": None}
    differences = [int(y) - int(x) for x, y in zip(a, b, strict=True)]
    wins, losses = differences.count(1), differences.count(-1)
    wl, wu = cp_interval(wins, n)
    ll, lu = cp_interval(losses, n)
    rng = random.Random(seed)
    samples = sorted(sum(rng.choices(differences, k=n)) / n for _ in range(replicates))
    d = wins + losses
    return {
        "n": n,
        "A_count": sum(a),
        "B_count": sum(b),
        "difference_B_minus_A": sum(differences) / n,
        "B_higher": wins,
        "ties": n - wins - losses,
        "B_lower": losses,
        "conservative_exact_95_ci": [max(-1.0, wl - lu), min(1.0, wu - ll)],
        "paired_bootstrap_percentile_95_ci": [
            samples[int(0.025 * replicates)],
            samples[int(0.975 * replicates) - 1],
        ],
        "bootstrap_degenerate": samples[0] == samples[-1],
        "exact_mcnemar_two_sided_p": min(1.0, 2 * _binomial_cdf(min(wins, losses), d, 0.5))
        if d
        else 1.0,
    }


def total(values: list[Any]) -> float | int | None:
    return sum(values) if values and all(type(v) in (int, float) for v in values) else None


def collect(panel: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    gold = read(ROOT / "tasks" / "pic110" / "oracles.json")
    prereg = OUT / ("prereg_pilot.json" if panel == "pilot" else "prereg_main.json")
    schedule = read(prereg)["schedule"] if prereg.exists() else []
    rows = []
    evaluations = []
    for task in (t for t in schedule if t["panel"] == panel):
        td = OUT / panel / task["task_id"]
        for arm in ("initial", "A", "B"):
            folder = td / arm
            recfile = folder / "record.json"
            record = (
                read(recfile)
                if recfile.exists()
                else read(td / f"planned_{arm}.json")
                if (td / f"planned_{arm}.json").exists()
                else {"attempt_status": "NOT_RUN"}
            )
            textfile = folder / "answer.txt"
            text = textfile.read_text(encoding="utf-8") if textfile.exists() else None
            started = time.perf_counter()
            oracle = evaluate(text, gold[task["task_id"]]) if panel != "historical" else None
            oracle_seconds = time.perf_counter() - started if oracle is not None else None
            diagfile = folder / "diagnosis.json"
            diag = read(diagfile) if diagfile.exists() else None
            row = {
                "task_id": task["task_id"],
                "panel": panel,
                "family": task["family"],
                "condition": arm,
                "order": task["order"],
                **{
                    k: record.get(k)
                    for k in (
                        "attempt_status",
                        "model_name",
                        "model_digest",
                        "pic_version",
                        "pic_distribution_hash",
                        "seed",
                        "prompt_hash",
                        "input_artifact_hash",
                        "shared_initial_hash",
                        "output_artifact_hash",
                        "token_usage",
                        "elapsed_time",
                        "cached_input_tokens",
                        "ollama_timing_ns",
                        "resource_before",
                        "resource_after",
                    )
                },
                "error_or_timeout": record.get("attempt_status")
                if record.get("error_or_timeout")
                else None,
                "independent_oracle_result": oracle,
                "evaluator_seconds": oracle_seconds,
                "pic_status": diag["check"] if diag else None,
                "intake_status": diag["intake"] if diag else None,
                "pic_seconds": diag["elapsed_seconds"] if diag else None,
                "missing_obligations": diag["intake"]["missing_obligations"] if diag else None,
                "residuals": diag["intake"]["residuals"] if diag else None,
                "task_prompt_bytes": len(task["prompt"].encode("utf-8")),
                "energy_joules": None,
                "monetary_cost": None,
            }
            if text is not None and row["output_artifact_hash"] != sha(text):
                raise ValueError("answer hash mismatch")
            if arm == "initial" and diag:
                # Initial records predate diagnosis; preserve rather than rewrite them.
                row["pic_status"] = diag["check"]
            rows.append(row)
            evaluations.append(
                {
                    "task_id": task["task_id"],
                    "condition": arm,
                    "result": oracle,
                    "evaluator_seconds": oracle_seconds,
                }
            )
    write(OUT / panel / "oracle_results.json", evaluations)
    panel_file = OUT / panel / "panel.json"
    return rows, read(panel_file) if panel_file.exists() else {"status": "NOT_RUN"}


def summarize(rows: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {"planned_tasks": len(rows) // 3, "arms": {}}
    for arm in ("initial", "A", "B"):
        selected = [r for r in rows if r["condition"] == arm]
        known = [
            r["independent_oracle_result"]
            for r in selected
            if r["independent_oracle_result"] is not None
        ]
        n = len(selected)
        successes = sum(o["success"] for o in known) if known else None
        fc_known = [o["false_completion"] for o in known if o["false_completion"] is not None]
        fc = sum(fc_known) if fc_known else (0 if known else None)
        pic_known = [r for r in selected if r["pic_status"] is not None]
        result["arms"][arm] = {
            "planned": n,
            "attempts": sum(r["attempt_status"] != "NOT_RUN" for r in selected),
            "statuses": {
                s: sum(r["attempt_status"] == s for r in selected)
                for s in sorted({r["attempt_status"] for r in selected})
            },
            "success_count": successes,
            "success_denominator": n if known else None,
            "success_wilson_95_ci": wilson(successes, n) if successes is not None else None,
            "false_completion_count": fc,
            "false_completion_observed_denominator": len(fc_known),
            "false_completion_planned_denominator": n if known else None,
            "false_completion_unknown": n - len(fc_known) if known else None,
            "false_completion_wilson_95_ci": wilson(fc, len(fc_known)) if fc is not None else None,
            "false_completion_planned_bounds": [fc / n, (fc + n - len(fc_known)) / n]
            if known and n and fc is not None
            else None,
            "valid_evidence_count": sum(o["valid_evidence"] is True for o in known),
            "correct_abstention_count": sum(o["correct_abstention"] is True for o in known),
            "abstention_denominator": sum(o["correct_abstention"] is not None for o in known),
            "unresolved_preserved_count": sum(o["unresolved_preserved"] is True for o in known),
            "input_tokens": total([(r.get("token_usage") or {}).get("input") for r in selected]),
            "output_tokens": total([(r.get("token_usage") or {}).get("output") for r in selected]),
            "model_wall_seconds": total([r["elapsed_time"] for r in selected]),
            "pic_wall_seconds": total([r["pic_seconds"] for r in selected]),
            "evaluator_seconds": total([r["evaluator_seconds"] for r in selected]),
            "pic_status_denominator": len(pic_known),
            "pic_flags": {
                k: {
                    "true": sum(r["pic_status"].get(k) is True for r in pic_known),
                    "false": sum(r["pic_status"].get(k) is False for r in pic_known),
                    "unknown": sum(r["pic_status"].get(k) is None for r in pic_known),
                }
                for k in (
                    "accepted",
                    "workflow_usable",
                    "operationally_usable",
                    "settled",
                    "acceleration_metrics_certified",
                )
            },
            "missing_obligation_counts": [
                r["intake_status"]["missing_obligation_count"] if r["intake_status"] else None
                for r in selected
            ],
            "residual_burdens": [
                r["intake_status"]["residual_burden"] if r["intake_status"] else None
                for r in selected
            ],
        }
    if rows and rows[0]["panel"] != "historical":
        aa = [r for r in rows if r["condition"] == "A"]
        bb = [r for r in rows if r["condition"] == "B"]
        result["success_paired"] = paired(
            [r["independent_oracle_result"]["success"] for r in aa],
            [r["independent_oracle_result"]["success"] for r in bb],
            cfg["bootstrap_seed"],
            cfg["bootstrap_replicates"],
        )
        pairs = [
            (a, b)
            for a, b in zip(aa, bb, strict=True)
            if a["independent_oracle_result"]["false_completion"] is not None
            and b["independent_oracle_result"]["false_completion"] is not None
        ]
        result["false_completion_paired"] = paired(
            [a["independent_oracle_result"]["false_completion"] for a, _ in pairs],
            [b["independent_oracle_result"]["false_completion"] for _, b in pairs],
            cfg["bootstrap_seed"],
            cfg["bootstrap_replicates"],
        )
        both_success = [
            (a, b)
            for a, b in zip(aa, bb, strict=True)
            if a["independent_oracle_result"]["success"]
            and b["independent_oracle_result"]["success"]
        ]
        result["both_success_costs"] = [
            {
                "task_id": a["task_id"],
                "A_revision_model_seconds": a["elapsed_time"],
                "B_revision_model_seconds": b["elapsed_time"],
                "B_intervention_and_post_pic_seconds": b["pic_seconds"]
                + next(
                    r["pic_seconds"]
                    for r in rows
                    if r["task_id"] == a["task_id"] and r["condition"] == "initial"
                ),
            }
            for a, b in both_success
            if a["pic_seconds"] is not None and b["pic_seconds"] is not None
        ]
        result["families"] = {}
        for family in sorted({r["family"] for r in rows}):
            grouped = [r for r in rows if r["family"] == family]
            result["families"][family] = {
                arm: {
                    "success": sum(
                        r["independent_oracle_result"]["success"]
                        for r in grouped
                        if r["condition"] == arm
                    ),
                    "false_completion": sum(
                        r["independent_oracle_result"]["false_completion"] is True
                        for r in grouped
                        if r["condition"] == arm
                    ),
                    "n": sum(r["condition"] == arm for r in grouped),
                }
                for arm in ("A", "B")
            }
    # Persistence of generic PIC obligations is distinct from task obligations.
    persistence = []
    for initial in (r for r in rows if r["condition"] == "initial"):
        for final in (
            r for r in rows if r["task_id"] == initial["task_id"] and r["condition"] in ("A", "B")
        ):
            before, after = initial["missing_obligations"], final["missing_obligations"]
            persistence.append(
                {
                    "task_id": initial["task_id"],
                    "condition": final["condition"],
                    "disappeared": sorted(set(before) - set(after))
                    if before is not None and after is not None
                    else None,
                }
            )
    result["pic_obligation_persistence"] = persistence
    return result


def analyze() -> dict[str, Any]:
    cfg = settings()
    all_rows, panels = [], {}
    for panel in ("pilot", "confirmatory", "historical"):
        rows, status = collect(panel)
        all_rows.extend(rows)
        panels[panel] = {**status, **summarize(rows, cfg)}
    environment = read(OUT / "setup" / "environment_private.json")
    model = next(m for m in environment["tags"]["models"] if m["name"] == cfg["model"])
    result = {
        "schema_version": 1,
        "status": "COMPLETED"
        if all(panels[p]["status"] == "COMPLETED" for p in panels)
        else "INCOMPLETE",
        "confirmatory_status": panels["confirmatory"]["status"],
        "model": model,
        "pic_version": cfg["pic_version"],
        "pic_distribution_hash": cfg["pic_distribution_hash"],
        "python": environment["python"],
        "uv": environment["uv"],
        "ollama": environment["ollama"],
        "platform": environment["platform"],
        "base_commit": environment["base_commit"],
        "campaign": read(OUT / "campaign.json") if (OUT / "campaign.json").exists() else None,
        "panels": panels,
        "rows": all_rows,
        "energy_joules": None,
        "monetary_cost": None,
        "acceleration_metrics_certified": None,
        "certification_status": "NOT_APPLICABLE_MISSING_RUNTIME_MEASUREMENT_CONTRACT",
        "preregistration_hashes": {
            phase: sha((OUT / f"prereg_{phase}.json").read_bytes())
            for phase in ("pilot", "main")
            if (OUT / f"prereg_{phase}.json").exists()
        },
    }
    write(OUT / "analysis.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--export",
        action="store_true",
        help="Write sanitized aggregate and per-task metrics under docs",
    )
    args = parser.parse_args()
    result = analyze()
    if args.export:
        write(ROOT / "docs" / "EXPERIMENT_SUMMARY_PIC_1_1_0.json", result)
    compact = {
        p: {
            "status": d["status"],
            "A": d["arms"]["A"]["success_count"],
            "B": d["arms"]["B"]["success_count"],
            "A_false": d["arms"]["A"]["false_completion_count"],
            "B_false": d["arms"]["B"]["false_completion_count"],
        }
        for p, d in result["panels"].items()
    }
    print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main()
