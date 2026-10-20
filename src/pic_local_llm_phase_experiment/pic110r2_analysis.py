"""Offline R2 reanalysis. Model outputs are read only after a panel finishes."""

from __future__ import annotations

import argparse
import time
from typing import Any

from pic_local_llm_phase_experiment.pic110_analysis import paired, total, wilson
from pic_local_llm_phase_experiment.pic110_runner import read, sha, write
from pic_local_llm_phase_experiment.pic110r2_oracle import evaluate
from pic_local_llm_phase_experiment.pic110r2_runner import (
    OUT,
    ROOT,
    file_hash,
    preservation,
    schedule,
    settings,
)


def collect(panel: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    state = OUT / panel / "panel.json"
    status = read(state) if state.exists() else {"status": "NOT_RUN"}
    if status["status"] == "RUNNING":
        raise ValueError("Do not inspect oracle outcomes while this panel is running")
    gold = read(ROOT / "tasks/pic110r2/oracles.json")
    rows = []
    for task in (t for t in schedule() if t["panel"] == panel):
        td = OUT / panel / task["task_id"]
        for condition in ("initial", "A", "B"):
            folder = td / condition
            record = (
                read(folder / "record.json")
                if (folder / "record.json").exists()
                else {"attempt_status": "NOT_RUN"}
            )
            if (td / f"planned_{condition}.json").exists() and record[
                "attempt_status"
            ] == "NOT_RUN":
                record = read(td / f"planned_{condition}.json")
            answer = (
                (folder / "answer.txt").read_text(encoding="utf-8")
                if (folder / "answer.txt").exists()
                else None
            )
            started = time.perf_counter()
            result = evaluate(answer, gold[task["task_id"]])
            if record["attempt_status"] != "OK":
                result["success"] = False
            evaluator_seconds = time.perf_counter() - started
            if answer is not None and sha(answer) != record.get("output_artifact_hash"):
                raise ValueError("answer hash mismatch")
            diag = read(folder / "diagnosis.json") if (folder / "diagnosis.json").exists() else None
            pic = None
            if diag is not None:
                pic = {
                    mode: {
                        k: diag[mode].get(k)
                        for k in (
                            "status",
                            "accepted",
                            "workflow_usable",
                            "operationally_usable",
                            "settled",
                            "acceleration_metrics_certified",
                            "missing_obligations",
                            "residuals",
                            "residual_burden",
                            "missing_obligation_count",
                            "elapsed_seconds",
                        )
                    }
                    for mode in ("check", "intake")
                }
                pic["elapsed_seconds"] = diag["elapsed_seconds"]
            row = {
                "task_id": task["task_id"],
                "panel": panel,
                "family": task["family"],
                "condition": condition,
                "order": task["order"],
                "gold_requires_abstention": not gold[task["task_id"]]["complete"],
                "oracle": result,
                "evaluator_seconds": evaluator_seconds,
                "pic": pic,
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
                "error_or_timeout": record["attempt_status"]
                if record.get("error_or_timeout")
                else None,
                "energy_joules": None,
                "monetary_cost": None,
            }
            rows.append(row)
    write(OUT / panel / "evaluated_rows.json", rows)
    return rows, status


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cfg = settings()
    result: dict[str, Any] = {"arms": {}}
    for condition in ("initial", "A", "B"):
        selected = [r for r in rows if r["condition"] == condition]
        n = len(selected)
        observable = [
            r["oracle"]["substantive_false_completion"]
            for r in selected
            if r["oracle"]["substantive_false_completion"] is not None
        ]
        success = sum(r["oracle"]["success"] for r in selected)
        result["arms"][condition] = {
            "planned": n,
            "success": success,
            "success_wilson_95_ci": wilson(success, n),
            "substantive_false_completion": sum(observable),
            "completion_flag_observed": len(observable),
            "completion_flag_unknown": n - len(observable),
            "false_completion_wilson_95_ci": wilson(sum(observable), len(observable)),
            "false_completion_planned_bounds": [
                sum(observable) / n,
                (sum(observable) + n - len(observable)) / n,
            ]
            if n
            else None,
            "states": {
                s: sum(r["attempt_status"] == s for r in selected)
                for s in sorted({r["attempt_status"] for r in selected})
            },
            **{
                metric: sum(r["oracle"][metric] is True for r in selected)
                for metric in (
                    "semantic_decision_correct",
                    "evidence_sufficient",
                    "format_conformant",
                    "evidence_incomplete_completion",
                    "correct_abstention",
                    "obligations_correct",
                    "surface_normalization_used",
                )
            },
            "abstention_denominator": sum(r["gold_requires_abstention"] for r in selected),
            "input_tokens": total([(r["token_usage"] or {}).get("input") for r in selected]),
            "output_tokens": total([(r["token_usage"] or {}).get("output") for r in selected]),
            "model_seconds": total([r["elapsed_time"] for r in selected]),
            "pic_seconds": total(
                [r["pic"]["elapsed_seconds"] if r["pic"] else None for r in selected]
            ),
            "evaluator_seconds": total([r["evaluator_seconds"] for r in selected]),
            "pic_flags": {
                key: {
                    str(value): sum(
                        r["pic"] is not None and r["pic"]["check"].get(key) is value
                        for r in selected
                    )
                    for value in (True, False, None)
                }
                for key in (
                    "accepted",
                    "workflow_usable",
                    "operationally_usable",
                    "settled",
                    "acceleration_metrics_certified",
                )
            },
            "pic_diagnosis_missing": sum(r["pic"] is None for r in selected),
        }
    aa = [r for r in rows if r["condition"] == "A"]
    bb = [r for r in rows if r["condition"] == "B"]
    result["success_paired"] = paired(
        [r["oracle"]["success"] for r in aa],
        [r["oracle"]["success"] for r in bb],
        cfg["bootstrap_seed"],
        cfg["bootstrap_replicates"],
    )
    observable_pairs = [
        (a, b)
        for a, b in zip(aa, bb, strict=True)
        if a["oracle"]["substantive_false_completion"] is not None
        and b["oracle"]["substantive_false_completion"] is not None
    ]
    result["false_completion_paired"] = paired(
        [a["oracle"]["substantive_false_completion"] for a, _ in observable_pairs],
        [b["oracle"]["substantive_false_completion"] for _, b in observable_pairs],
        cfg["bootstrap_seed"],
        cfg["bootstrap_replicates"],
    )
    costs = []
    persistence = []
    for a, b in zip(aa, bb, strict=True):
        initial = next(
            r for r in rows if r["task_id"] == a["task_id"] and r["condition"] == "initial"
        )
        common = initial["elapsed_time"]
        c_a = total(
            [common / 2 if common is not None else None, a["elapsed_time"], a["evaluator_seconds"]]
        )
        c_b = total(
            [
                common / 2 if common is not None else None,
                b["elapsed_time"],
                b["evaluator_seconds"],
                initial["pic"]["elapsed_seconds"] if initial["pic"] else None,
                b["pic"]["elapsed_seconds"] if b["pic"] else None,
            ]
        )
        costs.append(
            {
                "task_id": a["task_id"],
                "A_seconds": c_a,
                "B_seconds": c_b,
                "both_success": a["oracle"]["success"] and b["oracle"]["success"],
            }
        )
        for final in (a, b):
            before = initial["pic"]["intake"]["missing_obligations"] if initial["pic"] else None
            after = final["pic"]["intake"]["missing_obligations"] if final["pic"] else None
            persistence.append(
                {
                    "task_id": a["task_id"],
                    "condition": final["condition"],
                    "disappeared_without_verifier_evidence": sorted(set(before) - set(after))
                    if before is not None and after is not None
                    else None,
                }
            )
    result["costs"] = {
        "per_task": costs,
        "A_seconds": total([r["A_seconds"] for r in costs]),
        "B_seconds": total([r["B_seconds"] for r in costs]),
        "joint_success_tasks": sum(r["both_success"] for r in costs),
        "joint_success_A_seconds": total([r["A_seconds"] for r in costs if r["both_success"]]),
        "joint_success_B_seconds": total([r["B_seconds"] for r in costs if r["both_success"]]),
    }
    result["pic_persistence"] = persistence
    result["families"] = {
        family: {
            arm: {
                "n": sum(r["family"] == family and r["condition"] == arm for r in rows),
                "success": sum(
                    r["family"] == family and r["condition"] == arm and r["oracle"]["success"]
                    for r in rows
                ),
                "false_completion": sum(
                    r["family"] == family
                    and r["condition"] == arm
                    and r["oracle"]["substantive_false_completion"] is True
                    for r in rows
                ),
            }
            for arm in ("A", "B")
        }
        for family in sorted({r["family"] for r in rows})
    }
    return result


def analyze(export: bool) -> dict[str, Any]:
    rows, panels = [], {}
    for panel in ("pilot", "confirmatory"):
        selected, status = collect(panel)
        rows.extend(selected)
        panels[panel] = {**status, **summarize(selected)}
    env = read(OUT / "setup/environment_private.json")
    environment = {k: v for k, v in env.items() if k != "pic_import"}
    data = {
        "experiment": "PIC_1_1_0_R2",
        "status": "COMPLETED"
        if all(p["status"] == "COMPLETED" for p in panels.values())
        else "INCOMPLETE",
        "environment": environment,
        "panels": panels,
        "rows": rows,
        "campaign": read(OUT / "campaign.json"),
        "prior_preservation": preservation(),
        "preregistration_hashes": {
            phase: file_hash(OUT / f"prereg_{phase}.json")
            for phase in ("pilot", "main")
            if (OUT / f"prereg_{phase}.json").exists()
        },
        "energy_joules": None,
        "monetary_cost": None,
        "acceleration_metrics_certified": None,
        "certification_status": "NOT_APPLICABLE_MISSING_RUNTIME_MEASUREMENT_CONTRACT",
    }
    write(OUT / "analysis.json", data)
    if export:
        write(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R2.json", data)
    print(
        {
            p: {
                "status": d["status"],
                "A_success": d["arms"]["A"]["success"],
                "B_success": d["arms"]["B"]["success"],
                "A_false_completion": d["arms"]["A"]["substantive_false_completion"],
                "B_false_completion": d["arms"]["B"]["substantive_false_completion"],
            }
            for p, d in panels.items()
        },
        flush=True,
    )
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true")
    args = parser.parse_args()
    analyze(args.export)


if __name__ == "__main__":
    main()
