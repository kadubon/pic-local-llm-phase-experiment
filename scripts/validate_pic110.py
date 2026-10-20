"""Final bounded checks and artifact audit; no new inference or PIC execution."""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from pic_local_llm_phase_experiment.pic110_runner import OUT, ROOT, read, sha, verify, write


def main() -> int:
    setup = OUT / "setup"
    bin_dir = Path(sys.executable).parent
    suffix = ".exe" if sys.platform == "win32" else ""
    core = sorted(
        str(p.relative_to(ROOT))
        for p in (ROOT / "src/pic_local_llm_phase_experiment").glob("pic110*.py")
    )
    checks = {
        "syntax": [sys.executable, "-m", "compileall", "-q", "src", "scripts", "tests"],
        "ruff": [str(bin_dir / ("ruff" + suffix)), "check", "."],
        "format": [str(bin_dir / ("ruff" + suffix)), "format", "--check", "."],
        "mypy_new_core": [str(bin_dir / ("mypy" + suffix)), "--ignore-missing-imports", *core],
        "pytest": [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--junitxml",
            "results/pic110/setup/pytest_final.xml",
        ],
        "public_safety": [sys.executable, "scripts/public_safety_audit.py"],
        "public_reanalysis": [sys.executable, "scripts/reanalyze_pic110_public.py"],
    }
    results = {}
    for name, command in checks.items():
        proc = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
        )
        (setup / f"validation_{name}.txt").write_text(proc.stdout + proc.stderr, encoding="utf-8")
        results[name] = {
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "returncode": proc.returncode,
        }
    suites = ET.parse(setup / "pytest_final.xml").getroot()
    test_count = sum(int(s.get("tests", "0")) for s in suites.iter("testsuite"))
    failures = sum(int(s.get("failures", "0")) for s in suites.iter("testsuite"))
    errors = sum(int(s.get("errors", "0")) for s in suites.iter("testsuite"))
    skipped = sum(int(s.get("skipped", "0")) for s in suites.iter("testsuite"))
    results["pytest"].update(
        tests=test_count,
        passed=test_count - failures - errors - skipped,
        failed=failures,
        errors=errors,
        skipped=skipped,
    )
    for phase in ("pilot", "main"):
        manifest = verify(phase)
        results[f"frozen_{phase}"] = {"status": "PASS", "files": len(manifest["hashes"])}
    summary = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0.json")
    integrity_failures = []
    records = 0
    for row in summary["rows"]:
        folder = OUT / row["panel"] / row["task_id"] / row["condition"]
        if not (folder / "record.json").exists():
            if (
                row["attempt_status"] != "NOT_RUN"
                or not (folder.parent / f"planned_{row['condition']}.json").exists()
            ):
                integrity_failures.append("missing scheduled record or not-run plan")
            continue
        records += 1
        req = read(folder / "request.json")
        rec = read(folder / "record.json")
        raw = read(folder / "response.json")
        answer = (folder / "answer.txt").read_text(encoding="utf-8")
        if sha(req["prompt"]) != rec["prompt_hash"] or sha(answer) != rec["output_artifact_hash"]:
            integrity_failures.append("artifact hash")
        if raw.get("done") is not True or raw.get("response") != answer:
            integrity_failures.append("actual response identity")
        if "oracles.json" in req["prompt"] or "minimal_evidence_sets" in req["prompt"]:
            integrity_failures.append("gold metadata leaked")
        if row["condition"] != "initial":
            initial = (folder.parent / "initial/answer.txt").read_text(encoding="utf-8")
            if rec["shared_initial_hash"] != sha(initial) or initial not in req["prompt"]:
                integrity_failures.append("shared initial mismatch")
        if req["options"] != {
            "temperature": 0,
            "top_p": 1,
            "seed": 20261020,
            "num_predict": 768,
            "num_ctx": 16384,
        }:
            integrity_failures.append("unmatched generation options")
        if req.get("think") is not False or req["model"] != summary["model"]["name"]:
            integrity_failures.append("model or think setting")
    results["saved_real_trial_integrity"] = {
        "status": "PASS"
        if not integrity_failures and records == summary["campaign"]["calls"] - 1
        else "FAIL",
        "records": records,
        "planned_records": 78,
        "retained_not_run_entries": sum(r["attempt_status"] == "NOT_RUN" for r in summary["rows"]),
        "retained_truncated_records": sum(
            r["attempt_status"] == "TRUNCATED" for r in summary["rows"]
        ),
        "issues": integrity_failures,
        "inference_attempts_including_warmup": summary["campaign"]["calls"],
    }
    old_paths = [
        p
        for p in subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", summary["base_commit"]], cwd=ROOT, text=True
        ).splitlines()
        if p not in {"README.md", ".gitignore"}
    ]
    unchanged = subprocess.run(
        ["git", "diff", "--exit-code", summary["base_commit"], "--", *old_paths],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    results["historical_files_preserved"] = {
        "status": "PASS" if unchanged.returncode == 0 else "FAIL",
        "files": len(old_paths),
    }
    diagnosed = [r for r in summary["rows"] if r["pic_status"] is not None]
    missing_diagnosis = [r for r in summary["rows"] if r["pic_status"] is None]
    results["live_cli_parsing"] = {
        "status": "PASS"
        if all(
            r["pic_status"]["status"] == "parsed"
            and r["intake_status"] is not None
            and r["intake_status"]["status"] == "parsed"
            for r in diagnosed
        )
        and all(r["attempt_status"] in {"NOT_RUN", "TRUNCATED"} for r in missing_diagnosis)
        else "FAIL",
        "answer_diagnostics": len(diagnosed),
        "missing_due_to_stopping_or_not_run": len(missing_diagnosis),
        "commands_per_diagnosis": 2,
    }
    results["warmup"] = {
        "status": "PASS" if read(setup / "warmup_response.json").get("done") else "FAIL",
        "real_inference_calls": 1,
    }
    public = {
        "status": "PASS" if all(r["status"] == "PASS" for r in results.values()) else "FAIL",
        "checks": results,
        "development_history": {
            "first_combined_test_run": {"passed": 80, "failed": 1},
            "postpilot_document_audit_repeat": {"passed": 80, "failed": 1},
            "reason": "Legacy secret regex false positives on prose; "
            "wording corrected without weakening scanner. "
            "Pre-pilot type/format/syntax issues also fixed.",
        },
    }
    write(ROOT / "docs/PIC_1_1_0_VALIDATION.json", public)
    print(json.dumps(public, indent=2))
    return 0 if public["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
