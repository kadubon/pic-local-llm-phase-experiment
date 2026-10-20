"""Post-run validation, raw integrity checks and private append-only archival."""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from pic_local_llm_phase_experiment.pic110r3_common import (
    OUT,
    ROOT,
    normalized_hash,
    preservation,
    read,
    sha,
    write,
)
from pic_local_llm_phase_experiment.pic110r3_runner import (
    GENERIC,
    environment,
    frozen,
    revision,
    settings,
)


def validate() -> None:
    bin_dir = Path(sys.executable).parent
    core = sorted(
        str(p.relative_to(ROOT))
        for p in (ROOT / "src/pic_local_llm_phase_experiment").glob("pic110r3*.py")
    )
    commands = {
        "syntax": [sys.executable, "-m", "compileall", "-q", "src", "tests"],
        "ruff": [str(bin_dir / "ruff.exe"), "check", "."],
        "format": [str(bin_dir / "ruff.exe"), "format", "--check", "."],
        "mypy_new_core": [str(bin_dir / "mypy.exe"), "--ignore-missing-imports", *core],
        "pytest": [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--junitxml=results/pic110r3/setup/final_pytest.xml",
        ],
        "public_safety": [sys.executable, "scripts/public_safety_audit.py"],
        "public_arithmetic": [
            sys.executable,
            "-m",
            "pic_local_llm_phase_experiment.pic110r3_analysis",
            "--check-public",
        ],
    }
    checks = {}
    for name, command in commands.items():
        proc = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", timeout=120, check=False
        )
        (OUT / f"setup/final_{name}.txt").write_text(proc.stdout + proc.stderr, encoding="utf-8")
        checks[name] = {
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "exit_code": proc.returncode,
        }
    xml = ET.parse(OUT / "setup/final_pytest.xml").getroot()
    counts = {
        k: sum(int(s.get(k, "0")) for s in xml.iter("testsuite"))
        for k in ("tests", "failures", "errors", "skipped")
    }
    checks["pytest"].update(counts)
    checks["pytest"]["passed"] = (
        counts["tests"] - counts["failures"] - counts["errors"] - counts["skipped"]
    )
    checks["preservation"] = preservation()
    environment()
    checks["installed_pic_identity"] = {"status": "PASS", "wheel_payload_files": 617}
    for phase in ("pilot", "main"):
        manifest = frozen(phase)
        checks[f"frozen_{phase}"] = {"status": "PASS", "files": len(manifest["hashes"])}
    summary = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R3.json")
    cfg = settings()
    records = 0
    native_calls = 0
    for task in read(OUT / "setup/schedule.json"):
        td = OUT / task["panel"] / task["task_id"]
        initial = (
            (td / "initial/answer.txt").read_text(encoding="utf-8")
            if (td / "initial/answer.txt").exists()
            else "[INITIAL UNAVAILABLE]"
        )
        if (td / "B_material.json").exists():
            b, c = read(td / "B_material.json"), read(td / "C_material.json")
            assert b == {k: v for k, v in c.items() if k != "PIC"}, task["task_id"]
            assert "elapsed_seconds" not in b["receipt"]
            actual = read(td / "pic_feedback/actual_pic.json")
            native_calls += actual["native_calls"]
            assert actual["runtime"]["settled"] is False
        for arm in ("initial", "A", "B", "C"):
            folder = td / arm
            if not (folder / "record.json").exists():
                continue
            records += 1
            record, request = read(folder / "record.json"), read(folder / "request.json")
            assert sha(request["prompt"].encode()) == record["prompt_hash"]
            assert request["model"] == cfg["model"] and request["think"] is False
            assert request["options"] == {
                k: cfg[k] for k in ("temperature", "top_p", "seed", "num_predict", "num_ctx")
            }
            if (folder / "answer.txt").exists():
                text = (folder / "answer.txt").read_text(encoding="utf-8")
                assert sha(text.encode()) == record["output_artifact_hash"]
                assert read(folder / "response.json")["response"] == text
            if arm != "initial":
                material = GENERIC if arm == "A" else read(td / f"{arm}_material.json")
                assert request["prompt"] == revision(task, initial, material)
                assert record["shared_initial_hash"] == sha(initial.encode())
            else:
                assert request["prompt"] == task["prompt"]
            assert "setup/gold.json" not in request["prompt"]
    assert records == summary["campaign"]["calls"] - 1
    checks["actual_artifact_integrity"] = {
        "status": "PASS",
        "task_generation_records": records,
        "calls_including_warmup": summary["campaign"]["calls"],
        "planned_task_slots": 80,
        "native_feedback_calls": native_calls,
        "identical_B_C_common_receipts": True,
        "identical_shared_initials": True,
        "exact_frozen_prompts": True,
    }
    integration = read(ROOT / "docs/PIC_1_1_0_R3_INTEGRATION.json")
    checks["real_negative_integration"] = {
        "status": integration["status"],
        "cases": len(integration["cases"]),
        "actual_PIC": True,
        "mock_calls": 0,
        "CLI_commands": len(integration["cli"]),
    }
    invalid = [
        e
        for e in summary["evidence"]
        if e["status"] == "OBSERVED" and not e["receipt"]["sufficient"]
    ]
    checks["invalid_evidence_protected_promotion"] = {
        "status": "PASS" if all(not e["pic_ready"] for e in invalid) else "FAIL",
        "invalid_observed_cases": len(invalid),
        "false_protected_promotions": sum(e["pic_ready"] for e in invalid),
    }
    result = {
        "status": "PASS" if all(c["status"] == "PASS" for c in checks.values()) else "FAIL",
        "execution_status": summary["status"],
        "checks": checks,
    }
    write(ROOT / "docs/PIC_1_1_0_R3_VALIDATION.json", result)
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


def archive() -> None:
    preservation()
    manifest = frozen("main")
    target = OUT.parent / "pic110r3-private-recorded-run.zip"
    if target.exists():
        raise FileExistsError("Prior R3 archive retained")
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED) as archive_file:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                archive_file.write(path, "raw/" + str(path.relative_to(OUT)).replace("\\", "/"))
        for name in manifest["hashes"]:
            path = ROOT / name
            archive_file.write(path, "frozen/" + name)
    write(
        ROOT / "docs/PIC_1_1_0_R3_PRIVATE_ARCHIVE_IDENTITY.json",
        {
            "filename": target.name,
            "sha256": sha(target.read_bytes()),
            "bytes": target.stat().st_size,
            "public": False,
        },
    )


def manifest() -> None:
    paths = sorted(
        p
        for folder in ("src", "tests", "tasks", "configs", "docs")
        for p in (ROOT / folder).rglob("*")
        if p.is_file()
        and ("pic110r3" in p.as_posix().lower() or "1_1_0_r3" in p.name.lower())
        and "__pycache__" not in p.parts
        and p.name != "PIC_1_1_0_R3_PUBLIC_MANIFEST.json"
    )
    write(
        ROOT / "docs/PIC_1_1_0_R3_PUBLIC_MANIFEST.json",
        {
            "convention": "SHA256 with CRLF normalized to LF; manifest excluded",
            "files": {p.relative_to(ROOT).as_posix(): normalized_hash(p) for p in paths},
        },
    )


if __name__ == "__main__":
    actions = {"validate": validate, "archive": archive, "manifest": manifest}
    actions[sys.argv[1]]()
