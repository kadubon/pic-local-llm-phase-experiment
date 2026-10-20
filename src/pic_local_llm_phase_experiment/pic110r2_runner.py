"""Independent R2 campaign. No prior experiment files are written; no gold is loaded."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import random
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import psutil
import requests
import yaml

from pic_local_llm_phase_experiment.pic110_adapter import diagnose, feedback
from pic_local_llm_phase_experiment.pic110_runner import (
    ROOT,
    BudgetStop,
    read,
    sha,
    write,
)
from pic_local_llm_phase_experiment.pic110_runner import (
    Campaign as PriorCampaign,
)

OUT = ROOT / "results/pic110r2"
CONFIG = ROOT / "configs/experiment.pic-v1.1.0-r2.yaml"
GENERIC = (
    "Apply the explicit rule to the supplied source facts, not to an assertion of completion. "
    "Recompute arithmetic, select only the effective policy, distinguish JSON booleans from "
    "integers, and check all row constraints where applicable. Verify that the cited records "
    "actually suffice for the decision; background rules need no citation and irrelevant "
    "records need not be cited. Keep unresolved obligations when availability, signature or "
    "conflict rules require them. Use complete=true only for a resolved determination. "
    "Follow the explicitly declared decision type and source-ID notation."
)
PREFIX = (
    "Review the initial answer once using only the original task records. Return only the "
    "final task JSON. Review material is advisory, not new evidence; general framework "
    "obligations are not automatically task obligations.\n\nORIGINAL TASK\n"
)
FROZEN = [
    "configs/experiment.pic-v1.1.0-r2.yaml",
    "configs/requirements.pic110.lock",
    "docs/PROTOCOL_PIC_1_1_0_R2.md",
    "tasks/pic110r2/public.json",
    "tasks/pic110r2/oracles.json",
    "tasks/pic110r2/proof_audit.json",
    "scripts/build_pic110r2_tasks.py",
    "src/pic_local_llm_phase_experiment/pic110r2_logic.py",
    "src/pic_local_llm_phase_experiment/pic110r2_oracle.py",
    "src/pic_local_llm_phase_experiment/pic110r2_runner.py",
    "src/pic_local_llm_phase_experiment/pic110r2_analysis.py",
    "src/pic_local_llm_phase_experiment/pic110_runner.py",
    "src/pic_local_llm_phase_experiment/pic110_adapter.py",
    "src/pic_local_llm_phase_experiment/pic110_oracle.py",
    "src/pic_local_llm_phase_experiment/pic110_analysis.py",
    "tests/test_pic110r2.py",
]


def settings() -> dict[str, Any]:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    url = urlsplit(cfg["ollama_url"])
    if url.scheme != "http" or url.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("loopback Ollama only")
    if cfg["retries"] != 0 or cfg["think"] is not False:
        raise ValueError("fixed no-retry, no-thinking campaign")
    return cfg


def file_hash(path: Path) -> str:
    return sha(path.read_bytes().replace(b"\r\n", b"\n"))


def schedule() -> list[dict[str, Any]]:
    tasks = read(ROOT / "tasks/pic110r2/public.json")
    rng = random.Random(settings()["order_seed"])
    result: list[dict[str, Any]] = []
    for panel in ("pilot", "confirmatory"):
        group = [t for t in tasks if t["panel"] == panel]
        first = set(rng.sample(range(len(group)), len(group) // 2))
        result.extend(
            {**t, "order": ["A", "B"] if i in first else ["B", "A"]} for i, t in enumerate(group)
        )
    return result


def freeze(phase: str) -> None:
    target = OUT / f"prereg_{phase}.json"
    if target.exists():
        raise FileExistsError("preregistration already exists")
    write(
        target,
        {
            "phase": phase,
            "created_utc": datetime.now(UTC).isoformat(),
            "hash_convention": "SHA256 of bytes with CRLF normalized to LF",
            "hashes": {p: file_hash(ROOT / p) for p in FROZEN},
            "schedule": schedule(),
            "git_head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
        },
    )
    target.with_suffix(".sha256").write_text(file_hash(target) + "\n", encoding="ascii")
    print(f"Frozen R2 {phase}: {file_hash(target)}", flush=True)


def verify(phase: str) -> dict[str, Any]:
    target = OUT / f"prereg_{phase}.json"
    if file_hash(target) != target.with_suffix(".sha256").read_text().strip():
        raise ValueError("R2 manifest changed")
    manifest = read(target)
    for name, digest in manifest["hashes"].items():
        if file_hash(ROOT / name) != digest:
            raise ValueError(f"frozen file changed: {name}")
    return manifest


def preservation() -> dict[str, Any]:
    before = read(OUT / "setup/preservation_before.json")
    changed = [
        p
        for p, digest in before.items()
        if not (ROOT / p).exists() or sha((ROOT / p).read_bytes()) != digest
    ]
    if changed:
        raise ValueError("prior files changed: " + ", ".join(changed))
    return {"status": "PASS", "protected_files": len(before)}


def identity(cfg: dict[str, Any]) -> dict[str, Any]:
    import percolation_inversion_compiler as pic

    if importlib.metadata.version("percolation-inversion-compiler") != cfg["pic_version"]:
        raise ValueError("PIC version mismatch")
    if not Path(pic.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise ValueError("PIC import outside isolated environment")
    direct = json.loads(
        importlib.metadata.distribution("percolation-inversion-compiler").read_text(
            "direct_url.json"
        )
        or "{}"
    )
    if direct.get("dir_info", {}).get("editable"):
        raise ValueError("editable PIC forbidden")
    response = requests.get(cfg["ollama_url"] + "/api/tags", timeout=10)
    response.raise_for_status()
    model = next((m for m in response.json()["models"] if m["name"] == cfg["model"]), None)
    if model is None or model["digest"] != cfg["model_digest"]:
        raise ValueError("fixed installed model/digest unavailable")
    return model


def prepare() -> None:
    cfg = settings()
    setup = OUT / "setup"
    if (setup / "warmup_response.json").exists():
        raise FileExistsError("existing warmup preserved")
    preservation()
    wheel_name = "percolation_inversion_compiler-1.1.0-py3-none-any.whl"
    source = ROOT / "results/pic110/setup" / wheel_name
    target = setup / wheel_name
    if not target.exists() and source.exists():
        shutil.copyfile(source, target)
    if not target.exists():
        raise FileNotFoundError("place the fixed official PIC wheel in the new setup directory")
    if sha(target.read_bytes()) != cfg["pic_distribution_hash"]:
        raise ValueError("wheel hash mismatch")
    try:
        model = identity(cfg)
    except (requests.RequestException, ValueError) as exc:
        write(setup / "blocked.json", {"status": "ENVIRONMENT_BLOCKED", "error": str(exc)})
        raise
    version = requests.get(cfg["ollama_url"] + "/api/version", timeout=10)
    version.raise_for_status()
    write(
        setup / "environment_private.json",
        {
            "python": sys.version,
            "platform": platform.platform(),
            "model": model,
            "ollama": version.json(),
            "pic_version": cfg["pic_version"],
            "pic_distribution_hash": cfg["pic_distribution_hash"],
            "logical_cpus": psutil.cpu_count(),
            "ram_bytes": psutil.virtual_memory().total,
            "pic_import": __import__("percolation_inversion_compiler").__file__,
            "base_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
        },
    )
    payload = {
        "model": cfg["model"],
        "prompt": "Compute 23 + 19. Return only an integer.",
        "stream": False,
        "think": False,
        "keep_alive": cfg["keep_alive"],
        "options": {
            "temperature": 0,
            "top_p": 1,
            "seed": cfg["seed"],
            "num_ctx": cfg["num_ctx"],
            "num_predict": 64,
        },
    }
    write(setup / "warmup_request.json", payload)
    write(
        setup / "warmup_started.json",
        {"status": "STARTED", "calls": 1, "utc": datetime.now(UTC).isoformat()},
    )
    started = time.perf_counter()
    try:
        response = requests.post(
            cfg["ollama_url"] + "/api/generate",
            json=payload,
            timeout=(10, cfg["request_timeout_seconds"]),
        )
        response.raise_for_status()
        raw = response.json()
    except (ValueError, requests.RequestException) as exc:
        raw = {"error": str(exc)}
    raw["wall_seconds"] = time.perf_counter() - started
    write(setup / "warmup_response.json", raw)
    if not raw.get("done") or not raw.get("response"):
        raise ValueError("ENVIRONMENT_BLOCKED: real warmup failed")
    if any(type(raw.get(k)) is not int for k in ("prompt_eval_count", "eval_count")):
        raise ValueError("warmup resource metadata missing; retain it and do not start campaign")
    print(
        json.dumps(
            {
                k: raw.get(k)
                for k in (
                    "response",
                    "wall_seconds",
                    "prompt_eval_count",
                    "eval_count",
                    "eval_duration",
                )
            }
        ),
        flush=True,
    )


class Campaign(PriorCampaign):
    def __init__(self, cfg: dict[str, Any]):
        self.cfg, self.path = cfg, OUT / "campaign.json"
        if self.path.exists():
            self.data = read(self.path)
        else:
            warm = read(OUT / "setup/warmup_response.json")
            if not warm.get("done") or not warm.get("response"):
                raise ValueError("no successful real warmup")
            self.data = {
                "started_epoch": time.time(),
                "calls": 1,
                "input_tokens_observed": warm.get("prompt_eval_count"),
                "output_tokens_observed": warm.get("eval_count"),
                "input_tokens_reserved": cfg["max_prompt_bytes"],
                "output_tokens_reserved": 64,
                "consecutive_failures": 0,
                "stopped_reason": None,
            }
            write(self.path, self.data)


def revision(prompt: str, initial: str, review: str) -> str:
    return PREFIX + prompt + "\n\nINITIAL ANSWER\n" + initial + "\n\nREVIEW MATERIAL\n" + review


def run(panel: str) -> None:
    cfg = settings()
    manifest = verify("pilot" if panel == "pilot" else "main")
    preservation()
    identity(cfg)
    if (
        sha((OUT / "setup/percolation_inversion_compiler-1.1.0-py3-none-any.whl").read_bytes())
        != cfg["pic_distribution_hash"]
    ):
        raise ValueError("installed distribution witness mismatch")
    pd = OUT / panel
    if (pd / "panel.json").exists():
        raise FileExistsError("panel already started; no automatic resume")
    selected = [t for t in manifest["schedule"] if t["panel"] == panel]
    summary: dict[str, Any] = {
        "panel": panel,
        "status": "RUNNING",
        "planned_tasks": len(selected),
        "started_utc": datetime.now(UTC).isoformat(),
    }
    for task in selected:
        for condition in ("initial", "A", "B"):
            write(
                pd / task["task_id"] / f"planned_{condition}.json",
                {
                    "task_id": task["task_id"],
                    "panel": panel,
                    "condition": condition,
                    "attempt_status": "NOT_RUN",
                    "order": task["order"],
                },
            )
    write(pd / "panel.json", summary)
    campaign = Campaign(cfg)
    started = time.perf_counter()
    try:
        for index, task in enumerate(selected):
            td = pd / task["task_id"]
            write(td / "task_public.json", task)
            initial = campaign.generate(
                "Solve this task.\n" + task["prompt"], td / "initial", task, "initial", None
            )
            if initial["attempt_status"] not in {"OK", "TRUNCATED"}:
                continue
            text = (td / "initial/answer.txt").read_text(encoding="utf-8")
            before = diagnose(
                td / "initial/answer.txt",
                td / "initial/pic",
                cfg["pic_timeout_seconds"],
                cfg["profile"],
            )
            write(td / "initial/diagnosis.json", before)
            for condition in task["order"]:
                if condition == "B" and any(
                    before[k]["status"] != "parsed" for k in ("check", "intake")
                ):
                    write(
                        td / "planned_B.json",
                        {
                            "task_id": task["task_id"],
                            "panel": panel,
                            "condition": "B",
                            "attempt_status": "INTERVENTION_FAILED",
                        },
                    )
                    continue
                material = GENERIC if condition == "A" else feedback(before)
                record = campaign.generate(
                    revision(task["prompt"], text, material),
                    td / condition,
                    task,
                    condition,
                    sha(text),
                )
                if record["attempt_status"] in {"OK", "TRUNCATED"}:
                    # Diagnostics do not consume another model attempt. Preserve them even
                    # when this answer triggers the consecutive-generation-failure stop.
                    diagnosis = diagnose(
                        td / condition / "answer.txt",
                        td / condition / "pic",
                        cfg["pic_timeout_seconds"],
                        cfg["profile"],
                    )
                    write(td / condition / "diagnosis.json", diagnosis)
            ps = requests.get(cfg["ollama_url"] + "/api/ps", timeout=10)
            ps.raise_for_status()
            write(td / "ollama_ps.json", ps.json())
            print(
                f"R2 {panel} {index + 1}/{len(selected)} {task['task_id']} "
                f"order={''.join(task['order'])} calls={campaign.data['calls']}",
                flush=True,
            )
        summary["status"] = (
            "COMPLETED"
            if all(
                (pd / t["task_id"] / c / "record.json").exists()
                and read(pd / t["task_id"] / c / "record.json")["attempt_status"] == "OK"
                for t in selected
                for c in ("initial", "A", "B")
            )
            else "INCOMPLETE"
        )
    except (BudgetStop, requests.RequestException, KeyboardInterrupt) as exc:
        summary["status"], summary["stop_reason"] = "INCOMPLETE", str(exc) or "interrupted"
        campaign.data["stopped_reason"] = summary["stop_reason"]
        write(campaign.path, campaign.data)
        print(f"Stopped R2: {summary['stop_reason']}", flush=True)
    finally:
        summary["elapsed_seconds"] = time.perf_counter() - started
        summary["finished_utc"] = datetime.now(UTC).isoformat()
        write(pd / "panel.json", summary)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    f = sub.add_parser("freeze")
    f.add_argument("--phase", choices=["pilot", "main"], required=True)
    r = sub.add_parser("run")
    r.add_argument("--panel", choices=["pilot", "confirmatory"], required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "freeze":
        freeze(args.phase)
    else:
        run(args.panel)


if __name__ == "__main__":
    main()
