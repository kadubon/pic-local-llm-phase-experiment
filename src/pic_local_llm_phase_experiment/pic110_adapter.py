"""PIC 1.1 report adapter. Unknowns stay null; raw reports remain authoritative."""

from __future__ import annotations

import json
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def parse_report(raw: dict[str, Any], mode: str) -> dict[str, Any]:
    runtime = raw.get("runtime_report")
    runtime = runtime if isinstance(runtime, dict) else {}
    obligations = (
        raw.get("unresolved_obligations") if mode == "check" else runtime.get("missing_obligations")
    )
    if not (isinstance(obligations, list) and all(isinstance(x, str) for x in obligations)):
        obligations = None
    summary = raw.get("residual_summary")
    burden = None
    if isinstance(summary, dict) and all(
        type(v) in (int, float) and math.isfinite(v) for v in summary.values()
    ):
        burden = sum(summary.values())
    statuses = {
        k: raw.get(k) if type(raw.get(k)) is bool else None
        for k in (
            "accepted",
            "workflow_usable",
            "operationally_usable",
            "settled",
            "acceleration_metrics_certified",
        )
    }
    return {
        **statuses,
        "missing_obligations": obligations,
        "missing_obligation_count": len(obligations) if obligations is not None else None,
        "residuals": summary,
        "residual_burden": burden,
        "residual_ledger": runtime.get("residual_ledger"),
        "required_tasks": runtime.get("agent_tasks"),
        "next_safe_actions": raw.get("next_safe_actions"),
        "status": "parsed",
        "report_mode": mode,
    }


def diagnose(text_file: Path, out_dir: Path, timeout: float, profile: str) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    executable = Path(sys.executable).with_name("pic.exe" if sys.platform == "win32" else "pic")
    results: dict[str, Any] = {}
    for mode in ("check", "intake"):
        output = out_dir / f"{mode}.json"
        args = [
            str(executable),
            "agent",
            mode,
            "--text-file",
            str(text_file),
            "--profile",
            profile,
            "--no-allow-live-connectors",
            "--output",
            str(output),
        ]
        if mode == "check":
            args.append("--compact")
        started = time.perf_counter()
        try:
            proc = subprocess.run(
                args, capture_output=True, text=True, encoding="utf-8", timeout=timeout, check=False
            )
            (out_dir / f"{mode}.stdout.txt").write_text(proc.stdout, encoding="utf-8")
            (out_dir / f"{mode}.stderr.txt").write_text(proc.stderr, encoding="utf-8")
            if proc.returncode != 0:
                raise ValueError(f"PIC exit {proc.returncode}")
            raw = json.loads(output.read_text(encoding="utf-8"))
            results[mode] = parse_report(raw, mode)
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            results[mode] = {"status": "error", "error": str(exc), **parse_report({}, mode)}
            results[mode]["status"] = "error"
        results[mode]["elapsed_seconds"] = time.perf_counter() - started
    results["elapsed_seconds"] = sum(results[k]["elapsed_seconds"] for k in ("check", "intake"))
    return results


def feedback(diagnosis: dict[str, Any]) -> str:
    """Lossless field selection, not a task specific interpretation or oracle."""
    return json.dumps(
        {
            "check": {
                k: diagnosis["check"].get(k)
                for k in (
                    "accepted",
                    "workflow_usable",
                    "operationally_usable",
                    "settled",
                    "missing_obligations",
                    "residuals",
                    "next_safe_actions",
                    "status",
                )
            },
            "intake": {
                k: diagnosis["intake"].get(k)
                for k in (
                    "missing_obligations",
                    "residuals",
                    "residual_ledger",
                    "required_tasks",
                    "status",
                )
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    )
