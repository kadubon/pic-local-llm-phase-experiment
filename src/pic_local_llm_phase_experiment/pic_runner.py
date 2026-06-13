from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from pic_local_llm_phase_experiment.paths import ensure_dir, relative_posix, write_text
from pic_local_llm_phase_experiment.schemas import PICReportSummary


def _stringify_obligation(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return str(value)


def parse_pic_report(report_path: Path, base_dir: Path | None = None) -> PICReportSummary:
    raw = json.loads(report_path.read_text(encoding="utf-8"))
    runtime_report = raw.get("runtime_report")
    if not isinstance(runtime_report, dict):
        runtime_report = {}

    residual_summary = raw.get("residual_summary") or runtime_report.get("residual_summary") or ""
    if not isinstance(residual_summary, str):
        residual_summary = json.dumps(residual_summary, sort_keys=True, ensure_ascii=False)

    missing_raw = runtime_report.get("missing_obligations", raw.get("missing_obligations", []))
    if isinstance(missing_raw, dict):
        missing_obligations = [_stringify_obligation(item) for item in missing_raw.values()]
    elif isinstance(missing_raw, list):
        missing_obligations = [_stringify_obligation(item) for item in missing_raw]
    elif missing_raw:
        missing_obligations = [_stringify_obligation(missing_raw)]
    else:
        missing_obligations = []

    raw_report_path = report_path.as_posix()
    if base_dir is not None:
        raw_report_path = relative_posix(report_path, base_dir)

    return PICReportSummary(
        accepted=bool(raw.get("accepted", False)),
        settled=bool(raw.get("settled", False)),
        residual_summary=residual_summary,
        missing_obligations=missing_obligations,
        missing_obligation_count=len(missing_obligations),
        runtime_report=runtime_report,
        raw_report_path=raw_report_path,
    )


class PicRunner:
    def __init__(self, profile: str, timeout_seconds: int = 180, command: str = "pic") -> None:
        self.profile = profile
        self.timeout_seconds = timeout_seconds
        self.command = command

    def run_intake(
        self,
        *,
        candidate_text: str,
        candidate_path: Path,
        report_path: Path,
        run_dir: Path,
    ) -> PICReportSummary:
        ensure_dir(report_path.parent)
        write_text(candidate_path, candidate_text)

        args = [
            self.command,
            "agent",
            "intake",
            "--text-file",
            str(candidate_path),
            "--profile",
            self.profile,
            "--output",
            str(report_path),
        ]

        try:
            completed = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except FileNotFoundError:
            message = (
                "`pic` command was not found. Run `uv run python scripts/setup_pic.py` "
                "before the experiment."
            )
            write_text(report_path.with_suffix(".stderr.txt"), message)
            return PICReportSummary(
                raw_report_path=relative_posix(report_path, run_dir),
                command_failed=True,
                error_message=message,
            )
        except subprocess.TimeoutExpired as exc:
            message = f"PIC intake timed out after {self.timeout_seconds} seconds."
            write_text(report_path.with_suffix(".stdout.txt"), exc.stdout or "")
            write_text(report_path.with_suffix(".stderr.txt"), (exc.stderr or "") + "\n" + message)
            return PICReportSummary(
                raw_report_path=relative_posix(report_path, run_dir),
                command_failed=True,
                error_message=message,
            )

        write_text(report_path.with_suffix(".stdout.txt"), completed.stdout)
        write_text(report_path.with_suffix(".stderr.txt"), completed.stderr)

        if completed.returncode != 0:
            message = f"PIC intake failed with exit code {completed.returncode}."
            return PICReportSummary(
                raw_report_path=relative_posix(report_path, run_dir),
                command_failed=True,
                error_message=message,
            )

        if not report_path.exists():
            message = "PIC intake completed but did not create the expected JSON report."
            return PICReportSummary(
                raw_report_path=relative_posix(report_path, run_dir),
                command_failed=True,
                error_message=message,
            )

        try:
            return parse_pic_report(report_path, base_dir=run_dir)
        except (json.JSONDecodeError, OSError) as exc:
            message = f"PIC report parsing failed: {exc}"
            return PICReportSummary(
                raw_report_path=relative_posix(report_path, run_dir),
                command_failed=True,
                error_message=message,
            )
