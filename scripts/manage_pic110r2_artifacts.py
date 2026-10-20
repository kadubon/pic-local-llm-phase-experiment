"""Preservation, offline validation and local archival for the separate R2 run."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from pic_local_llm_phase_experiment.pic110_runner import read, sha, write
from pic_local_llm_phase_experiment.pic110r2_logic import derive
from pic_local_llm_phase_experiment.pic110r2_runner import (
    GENERIC,
    OUT,
    ROOT,
    file_hash,
    preservation,
    revision,
    settings,
    verify,
)


def preserve() -> None:
    target = OUT / "setup/preservation_before.json"
    if target.exists():
        raise FileExistsError("previous preservation manifest already exists")
    base = "bff2907e25fa028732944fa311399600b4918bbe"
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", base], cwd=ROOT, text=True
    ).splitlines()
    paths = [ROOT / p for p in names]
    old_raw = ROOT / "results/pic110"
    paths += [p for p in old_raw.rglob("*") if p.is_file()]
    paths.append(ROOT / "results/pic110-private-recorded-run.zip")
    write(
        target, {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in paths if p.is_file()}
    )
    print(preservation())


def validate() -> None:
    suffix = ".exe" if sys.platform == "win32" else ""
    bin_dir = Path(sys.executable).parent
    setup = OUT / "setup"
    core = sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "src/pic_local_llm_phase_experiment").glob("pic110r2*.py")
    )
    commands = {
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
            "results/pic110r2/setup/pytest_final.xml",
        ],
        "public_safety": [sys.executable, "scripts/public_safety_audit.py"],
        "public_arithmetic": [sys.executable, "scripts/report_pic110r2.py", "--check-public"],
    }
    results = {}
    for name, cmd in commands.items():
        proc = subprocess.run(
            cmd,
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
    xml = ET.parse(setup / "pytest_final.xml").getroot()
    values = {
        key: sum(int(s.get(key, "0")) for s in xml.iter("testsuite"))
        for key in ("tests", "failures", "errors", "skipped")
    }
    results["pytest"].update(values)
    results["pytest"]["passed"] = (
        values["tests"] - values["failures"] - values["errors"] - values["skipped"]
    )
    results["prior_preservation"] = preservation()
    for phase in ("pilot", "main"):
        manifest = verify(phase)
        results[f"frozen_{phase}"] = {"status": "PASS", "files": len(manifest["hashes"])}
    gold = read(ROOT / "tasks/pic110r2/oracles.json")
    proof_audit = read(ROOT / "tasks/pic110r2/proof_audit.json")
    for task in read(ROOT / "tasks/pic110r2/public.json"):
        derived, audit = derive(task)
        if derived != gold[task["task_id"]] or audit != next(
            a for a in proof_audit if a["task_id"] == task["task_id"]
        ):
            raise ValueError("prospective gold/proof audit differs")
    results["minimum_proof_audit"] = {
        "status": "PASS",
        "tasks": 20,
        "worlds": sum(a["world_count"] for a in proof_audit),
        "minimal_sets": sum(len(a["all_minimal_proofs"]) for a in proof_audit),
    }
    summary = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R2.json")
    cfg = settings()
    issues, nrecords, ndiag = [], 0, 0
    for row in summary["rows"]:
        folder = OUT / row["panel"] / row["task_id"] / row["condition"]
        if not (folder / "record.json").exists():
            if (
                row["attempt_status"] != "NOT_RUN"
                or not (folder.parent / f"planned_{row['condition']}.json").exists()
            ):
                issues.append("missing planned status")
            continue
        nrecords += 1
        record, request = read(folder / "record.json"), read(folder / "request.json")
        text = (
            (folder / "answer.txt").read_text(encoding="utf-8")
            if (folder / "answer.txt").exists()
            else None
        )
        raw = read(folder / "response.json") if (folder / "response.json").exists() else None
        if sha(request["prompt"]) != record["prompt_hash"]:
            issues.append("prompt hash mismatch")
        if text is not None and (
            sha(text) != record["output_artifact_hash"] or not raw or raw.get("response") != text
        ):
            issues.append("raw output identity mismatch")
        if "oracles.json" in request["prompt"] or "minimal_evidence_sets" in request["prompt"]:
            issues.append("oracle metadata in generation")
        if request["options"] != {
            k: cfg[k] for k in ("temperature", "top_p", "seed", "num_ctx", "num_predict")
        }:
            issues.append("unmatched model options")
        if request["model"] != cfg["model"] or request["think"] is not False:
            issues.append("model/thinking mismatch")
        if record["model_digest"] != cfg["model_digest"]:
            issues.append("digest mismatch")
        if row["condition"] in ("A", "B"):
            initial = (folder.parent / "initial/answer.txt").read_text(encoding="utf-8")
            task = read(folder.parent / "task_public.json")
            if record["shared_initial_hash"] != sha(initial):
                issues.append("shared initial mismatch")
            if row["condition"] == "A":
                material = GENERIC
            else:
                from pic_local_llm_phase_experiment.pic110_adapter import feedback

                material = feedback(read(folder.parent / "initial/diagnosis.json"))
            if request["prompt"] != revision(task["prompt"], initial, material):
                issues.append("review material differs from frozen intervention")
        if row["pic"] is not None:
            ndiag += 1
            if any(row["pic"][mode]["status"] != "parsed" for mode in ("check", "intake")):
                issues.append("PIC parse error retained")
    results["actual_model_artifact_integrity"] = {
        "status": "PASS" if not issues and nrecords == summary["campaign"]["calls"] - 1 else "FAIL",
        "issues": issues,
        "actual_records": nrecords,
        "planned_slots": len(summary["rows"]),
        "actual_calls_including_warmup": summary["campaign"]["calls"],
        "actual_pic_diagnoses": ndiag,
        "pic_commands_per_diagnosis": 2,
        "attempt_states": {
            s: sum(r["attempt_status"] == s for r in summary["rows"])
            for s in sorted({r["attempt_status"] for r in summary["rows"]})
        },
    }
    # Descriptive preservation audit separates lost obligations from extra labels.
    obligations = []
    for row in summary["rows"]:
        path = OUT / row["panel"] / row["task_id"] / row["condition"] / "answer.txt"
        actual = None
        if path.exists():
            from pic_local_llm_phase_experiment.pic110_oracle import parse_answer

            try:
                value = parse_answer(path.read_text(encoding="utf-8")).get("unresolved")
                if isinstance(value, list) and all(isinstance(v, str) for v in value):
                    actual = set(value)
            except ValueError:
                pass
        expected = set(gold[row["task_id"]]["unresolved"])
        obligations.append(
            {
                "task_id": row["task_id"],
                "panel": row["panel"],
                "condition": row["condition"],
                "lost": sorted(expected - actual) if actual is not None else None,
                "spurious": sorted(actual - expected) if actual is not None else None,
            }
        )
    write(ROOT / "docs/PIC_1_1_0_R2_OBLIGATION_AUDIT.json", obligations)
    result = {
        "status": "PASS" if all(r["status"] == "PASS" for r in results.values()) else "FAIL",
        "checks": results,
        "experiment_execution_status": summary["status"],
    }
    write(ROOT / "docs/PIC_1_1_0_R2_VALIDATION.json", result)
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


def archive() -> None:
    preservation()
    manifest = verify("main")
    target = ROOT / "results/pic110r2-private-recorded-run.zip"
    if target.exists():
        raise FileExistsError("existing private R2 archive preserved")
    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in files:
            z.write(path, "raw/" + path.relative_to(OUT).as_posix())
        for name in manifest["hashes"]:
            z.write(ROOT / name, "frozen_source/" + name)
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:
            raise ValueError("R2 archive CRC failure")
    write(
        ROOT / "docs/PIC_1_1_0_R2_PRIVATE_ARCHIVE_IDENTITY.json",
        {
            "visibility": "LOCAL_IGNORED_NOT_PUBLISHED",
            "basename": target.name,
            "sha256": sha(target.read_bytes()),
            "bytes": target.stat().st_size,
            "raw_files": len(files),
            "crc": "PASS",
        },
    )
    print("R2 private archive created and verified; prior archive unchanged")


def public_manifest() -> None:
    paths = sorted(
        set(
            [
                *ROOT.glob("docs/*PIC_1_1_0_R2*"),
                *ROOT.glob("docs/PIC_1_1_0_R2*"),
                *ROOT.glob("scripts/*pic110r2*.py"),
                *ROOT.glob("src/pic_local_llm_phase_experiment/pic110r2*.py"),
                ROOT / "configs/experiment.pic-v1.1.0-r2.yaml",
                ROOT / "tests/test_pic110r2.py",
                *ROOT.glob("tasks/pic110r2/*.json"),
            ]
        )
    )
    write(
        ROOT / "docs/PIC_1_1_0_R2_PUBLIC_MANIFEST.json",
        {
            "convention": "SHA256 with CRLF normalized to LF; this manifest excluded",
            "files": {
                p.relative_to(ROOT).as_posix(): file_hash(p)
                for p in paths
                if p.is_file() and p.name != "PIC_1_1_0_R2_PUBLIC_MANIFEST.json"
            },
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["preserve", "validate", "archive", "manifest"])
    args = parser.parse_args()
    {"preserve": preserve, "validate": validate, "archive": archive, "manifest": public_manifest}[
        args.command
    ]()


if __name__ == "__main__":
    main()
