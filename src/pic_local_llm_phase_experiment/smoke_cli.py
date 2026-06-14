from __future__ import annotations

import argparse
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pic_local_llm_phase_experiment.experiment import (
    estimate_experiment_workload,
    load_pic_setup_metadata,
)
from pic_local_llm_phase_experiment.ollama_client import OllamaClient, OllamaError
from pic_local_llm_phase_experiment.paths import ensure_dir, write_json, write_text
from pic_local_llm_phase_experiment.pic_runner import parse_pic_report
from pic_local_llm_phase_experiment.report import render_report
from pic_local_llm_phase_experiment.schemas import ExperimentConfig
from pic_local_llm_phase_experiment.task_loader import load_config, load_tasks


def _run_command(args: list[str], *, cwd: Path, timeout_seconds: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as exc:
        return {
            "args": args,
            "returncode": 127,
            "stdout": "",
            "stderr": str(exc),
            "ok": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "args": args,
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + f"\nTimed out after {timeout_seconds} seconds.",
            "ok": False,
        }
    return {
        "args": args,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
        "ok": completed.returncode == 0,
    }


def _smoke_rows(report_path: Path, root: Path) -> list[dict[str, Any]]:
    parsed = parse_pic_report(report_path, base_dir=root)
    return [
        {
            "task_id": "smoke_pic_agent_intake",
            "run_id": "smoke",
            "baseline_heuristic_obligation_coverage": 0.0,
            "pic_heuristic_obligation_coverage": 0.0,
            "pic_missing_obligation_delta": 0,
            "pic_missing_obligation_count_before": parsed.missing_obligation_count,
            "pic_missing_obligation_count_after": parsed.missing_obligation_count,
            "pic_residual_summary_length_before": len(parsed.residual_summary),
            "pic_residual_summary_key_count_before": parsed.residual_summary_key_count,
            "pic_residual_charge_total_before": parsed.residual_charge_total,
            "pic_pic_accepted_after": parsed.accepted,
            "pic_pic_operationally_usable_after": parsed.operationally_usable,
            "pic_pic_settled_after": parsed.settled,
            "pic_pic_schema_fields_usable": parsed.runtime_report_present,
            "pic_local_phase_score": 0.0,
        }
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run lightweight readiness smoke checks.")
    parser.add_argument("--config", default="configs/experiment.default.yaml")
    parser.add_argument("--model")
    parser.add_argument("--ollama-url")
    parser.add_argument("--timeout-seconds", type=int)
    args = parser.parse_args(argv)

    root = Path.cwd()
    smoke_dir = ensure_dir(root / "results" / "smoke")
    report_path = smoke_dir / "pic-agent-output-report.json"
    config: ExperimentConfig | None = None

    try:
        config = load_config(root / args.config)
        config_check: dict[str, Any] = {"ok": True, "config_path": args.config}
    except Exception as exc:  # pragma: no cover - defensive smoke path
        config_check = {"ok": False, "config_path": args.config, "error": str(exc)}

    model = args.model or (config.model if config else "qwen3.5:35b-a3b")
    ollama_url = args.ollama_url or (config.ollama_url if config else "http://localhost:11434")
    pic_profile = config.pic_profile if config else "development"
    timeout_seconds = args.timeout_seconds or (config.timeout_seconds if config else 60)

    checks: dict[str, Any] = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "model": model,
        "ollama_url": ollama_url,
        "timeout_seconds": timeout_seconds,
        "full_experiment_config": config_check,
    }

    try:
        __import__("pic_local_llm_phase_experiment")
        checks["environment_imports"] = {"ok": True}
    except Exception as exc:  # pragma: no cover - defensive smoke path
        checks["environment_imports"] = {"ok": False, "error": str(exc)}

    try:
        client = OllamaClient(
            ollama_url,
            timeout_seconds=timeout_seconds,
            generation_retries=config.generation_retries if config else 1,
            disable_thinking=config.disable_ollama_thinking if config else True,
        )
        client.ensure_model_available(model)
        checks["ollama_model"] = {"ok": True}
    except OllamaError as exc:
        checks["ollama_model"] = {"ok": False, "error": str(exc)}

    try:
        generation = OllamaClient(
            ollama_url,
            timeout_seconds=timeout_seconds,
            generation_retries=config.generation_retries if config else 1,
            disable_thinking=config.disable_ollama_thinking if config else True,
        ).generate(
            model=model,
            prompt="Local smoke check. Reply with the word ready and one short sentence.",
            temperature=0,
            top_p=1,
            seed=config.seed if config else 42,
            num_predict=32,
        )
        checks["ollama_generation"] = {
            "ok": bool(generation.text.strip()),
            "response_length": len(generation.text),
            "attempt_count": generation.raw.get("attempt_count"),
            "streamed": generation.raw.get("streamed"),
        }
    except OllamaError as exc:
        checks["ollama_generation"] = {"ok": False, "error": str(exc)}

    setup_metadata = load_pic_setup_metadata(root)
    full_readiness: dict[str, Any] = {
        "ok": False,
        "config_path": args.config,
        "pic_setup_status": setup_metadata["status"],
        "pic_commit": setup_metadata.get("pic_commit"),
        "pic_version": setup_metadata.get("pic_version"),
    }
    if config is not None:
        try:
            tasks = load_tasks(root / "tasks", max_tasks=config.max_tasks)
            workload = estimate_experiment_workload(
                task_count=len(tasks),
                repair_rounds=config.repair_rounds,
                experiment_mode=config.experiment_mode,
            )
            full_readiness.update(
                {
                    "experiment_mode": config.experiment_mode,
                    "shared_initial_answer_used": config.experiment_mode == "shared_initial",
                    "task_count": len(tasks),
                    "task_ids": [task.task_id for task in tasks],
                    "estimated_ollama_generation_count": workload["ollama_generation_count"],
                    "estimated_pic_intake_count": workload["pic_intake_count"],
                    "timeout_seconds": config.timeout_seconds,
                    "generation_retries": config.generation_retries,
                    "disable_ollama_thinking": config.disable_ollama_thinking,
                    "num_predict": config.num_predict,
                    "ok": bool(tasks) and setup_metadata["status"] == "ok",
                }
            )
        except Exception as exc:  # pragma: no cover - defensive smoke path
            full_readiness["error"] = str(exc)
    checks["full_experiment_readiness"] = full_readiness

    checks["pic_help"] = _run_command(
        ["pic", "--help"],
        cwd=root,
        timeout_seconds=timeout_seconds,
    )
    checks["pic_agent_explain"] = _run_command(
        ["pic", "agent", "explain"],
        cwd=root,
        timeout_seconds=timeout_seconds,
    )
    checks["pic_agent_intake"] = _run_command(
        [
            "pic",
            "agent",
            "intake",
            "--text",
            "Candidate packet: preserve residual ledgers and route missing verifier work.",
            "--profile",
            pic_profile,
            "--output",
            str(report_path),
        ],
        cwd=root,
        timeout_seconds=timeout_seconds,
    )

    if report_path.exists():
        try:
            rows = _smoke_rows(report_path, root)
            write_json(smoke_dir / "summary.json", rows)
            report = render_report(
                rows=rows,
                manifest={
                    "run_id": "smoke",
                    "model": model,
                    "ollama_url": ollama_url,
                    "repair_rounds": 0,
                    "pic_profile": pic_profile,
                    "experiment_mode": config.experiment_mode if config else "separate_initial",
                    "shared_initial_answer_used": (
                        config.experiment_mode == "shared_initial" if config else False
                    ),
                },
            )
            write_text(root / "reports" / "smoke_experiment_report.md", report)
            checks["report_generation"] = {"ok": True}
        except Exception as exc:  # pragma: no cover - defensive smoke path
            checks["report_generation"] = {"ok": False, "error": str(exc)}
    else:
        checks["report_generation"] = {
            "ok": False,
            "error": "PIC intake did not create the expected JSON report.",
        }

    write_json(smoke_dir / "smoke_manifest.json", checks)
    failed = [
        name for name, data in checks.items() if isinstance(data, dict) and not data.get("ok")
    ]
    if failed:
        print(f"Smoke checks failed: {', '.join(failed)}")
        print("See results/smoke/smoke_manifest.json for details.")
        return 1
    print("Smoke checks passed. See results/smoke/ and reports/smoke_experiment_report.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
