"""Bounded, append-preserving local experiment, separate from historical entry points.

The runner never loads oracles.json. Grading happens later in the analysis process.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import random
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
from pic_local_llm_phase_experiment.pic110_prompts import GENERIC, INITIAL, revision
from pic_local_llm_phase_experiment.task_loader import load_tasks

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "pic110"
CONFIG = ROOT / "configs" / "experiment.pic-v1.1.0.yaml"
FROZEN = [
    "configs/experiment.pic-v1.1.0.yaml",
    "configs/requirements.pic110.lock",
    "docs/PROTOCOL_PIC_1_1_0.md",
    "tasks/pic110/public.json",
    "tasks/pic110/oracles.json",
    "scripts/build_pic110_tasks.py",
    "src/pic_local_llm_phase_experiment/pic110_oracle.py",
    "src/pic_local_llm_phase_experiment/pic110_runner.py",
    "src/pic_local_llm_phase_experiment/pic110_adapter.py",
    "src/pic_local_llm_phase_experiment/pic110_prompts.py",
    "src/pic_local_llm_phase_experiment/pic110_analysis.py",
] + [f"tasks/{p.name}" for p in sorted((ROOT / "tasks").glob("task_*.yaml"))]


def sha(data: bytes | str) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def settings() -> dict[str, Any]:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    url = urlsplit(cfg["ollama_url"])
    if url.scheme != "http" or url.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("local Ollama only")
    if cfg["retries"] != 0 or cfg["think"] is not False:
        raise ValueError("preregistered no-retry, no-thinking design required")
    return cfg


def tasks() -> list[dict[str, Any]]:
    public = read(ROOT / "tasks" / "pic110" / "public.json")
    historical = [
        {
            "task_id": t.task_id,
            "family": "historical_review",
            "panel": "historical",
            "prompt": t.prompt,
            "source_ids": [],
        }
        for t in load_tasks(ROOT / "tasks")
    ]
    return public + historical


def schedule(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    rng = random.Random(cfg["order_seed"])
    for panel in ("pilot", "confirmatory", "historical"):
        group = [t for t in tasks() if t["panel"] == panel]
        # Exact counterbalance within each panel, fixed before any panel outcome.
        first_a = set(rng.sample(range(len(group)), len(group) // 2))
        result.extend(
            {**t, "order": ["A", "B"] if i in first_a else ["B", "A"]} for i, t in enumerate(group)
        )
    return result


def freeze(phase: str) -> None:
    cfg = settings()
    path = OUT / f"prereg_{phase}.json"
    if path.exists():
        raise FileExistsError("preregistration already exists; never overwrite")
    hashes = {p: sha((ROOT / p).read_bytes()) for p in FROZEN}
    data = {
        "phase": phase,
        "created_utc": datetime.now(UTC).isoformat(),
        "hashes": hashes,
        "schedule": schedule(cfg),
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
    }
    write(path, data)
    path.with_suffix(".sha256").write_text(sha(path.read_bytes()) + "\n", encoding="ascii")
    print(f"Frozen {phase}: {sha(path.read_bytes())}", flush=True)


def verify(phase: str) -> dict[str, Any]:
    path = OUT / f"prereg_{phase}.json"
    if sha(path.read_bytes()) != path.with_suffix(".sha256").read_text().strip():
        raise ValueError("preregistration manifest hash mismatch")
    manifest = read(path)
    for name, expected in manifest["hashes"].items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError(f"frozen file changed: {name}")
    return manifest


def sample_resources() -> dict[str, Any]:
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "ram_percent": mem.percent,
        "available_ram_bytes": mem.available,
        "total_ram_bytes": mem.total,
        "gpu_utilization": None,
        "gpu_vram_used_bytes": None,
    }


class BudgetStop(RuntimeError):
    pass


class Campaign:
    def __init__(self, cfg: dict[str, Any]):
        self.cfg = cfg
        self.path = OUT / "campaign.json"
        if self.path.exists():
            self.data = read(self.path)
        else:
            warm = read(OUT / "setup" / "warmup_response.json")
            self.data = {
                "started_epoch": time.time(),
                "calls": 1,
                "input_tokens_observed": warm.get("prompt_eval_count", 0),
                "output_tokens_observed": warm.get("eval_count", 0),
                "input_tokens_reserved": 32,
                "output_tokens_reserved": 64,
                "consecutive_failures": 0,
                "stopped_reason": None,
            }
            write(self.path, self.data)

    def guard(self) -> None:
        cfg, data = self.cfg, self.data
        checks = {
            "call_limit": data["calls"] >= cfg["max_calls_including_warmup"],
            "wall_limit": time.time() - data["started_epoch"] + cfg["request_timeout_seconds"]
            > cfg["max_wall_seconds"],
            "input_limit": data["input_tokens_reserved"] + cfg["max_prompt_bytes"]
            > cfg["max_input_tokens"],
            "output_limit": data["output_tokens_reserved"] + cfg["num_predict"]
            > cfg["max_output_tokens"],
            "ram_limit": psutil.virtual_memory().percent > cfg["max_ram_percent"],
            "failure_limit": data["consecutive_failures"] >= cfg["max_consecutive_failures"],
        }
        reasons = [k for k, value in checks.items() if value]
        if data["stopped_reason"] or reasons:
            data["stopped_reason"] = data["stopped_reason"] or ",".join(reasons)
            write(self.path, data)
            raise BudgetStop(data["stopped_reason"])

    def model_identity(self) -> None:
        response = requests.get(self.cfg["ollama_url"] + "/api/tags", timeout=10)
        response.raise_for_status()
        found = next((m for m in response.json()["models"] if m["name"] == self.cfg["model"]), None)
        if found is None or found["digest"] != self.cfg["model_digest"]:
            raise BudgetStop("model absent or digest changed")

    def generate(
        self,
        prompt: str,
        folder: Path,
        task: dict[str, Any],
        condition: str,
        initial_hash: str | None,
    ) -> dict[str, Any]:
        self.guard()
        self.model_identity()
        if len(prompt.encode("utf-8")) > self.cfg["max_prompt_bytes"]:
            raise BudgetStop("prompt exceeds fixed byte bound; no truncation")
        folder.mkdir(parents=True, exist_ok=False)
        cfg = self.cfg
        payload = {
            "model": cfg["model"],
            "prompt": prompt,
            "stream": False,
            "think": cfg["think"],
            "keep_alive": cfg["keep_alive"],
            "options": {
                k: cfg[k] for k in ("temperature", "top_p", "seed", "num_predict", "num_ctx")
            },
        }
        write(folder / "request.json", payload)
        (folder / "prompt.txt").write_text(prompt, encoding="utf-8")
        record = {
            "task_id": task["task_id"],
            "family": task["family"],
            "panel": task["panel"],
            "condition": condition,
            "model_name": cfg["model"],
            "model_digest": cfg["model_digest"],
            "pic_version": cfg["pic_version"],
            "pic_distribution_hash": cfg["pic_distribution_hash"],
            "seed": cfg["seed"],
            "prompt_hash": sha(prompt),
            "input_artifact_hash": sha(task["prompt"]),
            "shared_initial_hash": initial_hash,
            "output_artifact_hash": None,
            "independent_oracle_result": None,
            "pic_status": None,
            "missing_obligations": None,
            "residuals": None,
            "token_usage": None,
            "attempt_status": "STARTED",
            "error_or_timeout": None,
            "started_utc": datetime.now(UTC).isoformat(),
            "resource_before": sample_resources(),
        }
        write(folder / "record.json", record)
        self.data["calls"] += 1
        self.data["input_tokens_reserved"] += cfg["max_prompt_bytes"]
        self.data["output_tokens_reserved"] += cfg["num_predict"]
        write(self.path, self.data)
        started = time.perf_counter()
        try:
            response = requests.post(
                cfg["ollama_url"] + "/api/generate",
                json=payload,
                timeout=(10, cfg["request_timeout_seconds"]),
            )
            response.raise_for_status()
            raw = response.json()
            write(folder / "response.json", raw)
            text = raw.get("response")
            if raw.get("error") or raw.get("done") is not True or not isinstance(text, str):
                raise ValueError("malformed/incomplete Ollama response")
            (folder / "answer.txt").write_text(text, encoding="utf-8")
            record["output_artifact_hash"] = sha(text)
            record["attempt_status"] = (
                "EMPTY"
                if not text.strip()
                else "TRUNCATED"
                if raw.get("done_reason") == "length"
                else "OK"
            )
            usage = {"input": raw.get("prompt_eval_count"), "output": raw.get("eval_count")}
            usage["total"] = (
                sum(usage.values()) if all(type(v) is int for v in usage.values()) else None
            )
            record["token_usage"] = usage
            record["ollama_timing_ns"] = {
                k: raw.get(k)
                for k in (
                    "total_duration",
                    "load_duration",
                    "prompt_eval_duration",
                    "eval_duration",
                )
            }
            record["cached_input_tokens"] = raw.get("prompt_eval_cached_count")
            for target, field in (
                ("input_tokens_observed", "input"),
                ("output_tokens_observed", "output"),
            ):
                if usage[field] is not None:
                    self.data[target] += usage[field]
            self.data["consecutive_failures"] = (
                0 if record["attempt_status"] == "OK" else self.data["consecutive_failures"] + 1
            )
        except (requests.RequestException, ValueError) as exc:
            record["attempt_status"] = "TIMEOUT" if isinstance(exc, requests.Timeout) else "ERROR"
            record["error_or_timeout"] = str(exc)
            self.data["consecutive_failures"] += 1
        finally:
            record["elapsed_time"] = time.perf_counter() - started
            record["resource_after"] = sample_resources()
            write(folder / "record.json", record)
            write(self.path, self.data)
        return record


def run(panel: str) -> None:
    cfg = settings()
    manifest = verify("pilot" if panel == "pilot" else "main")
    if importlib.metadata.version("percolation-inversion-compiler") != cfg["pic_version"]:
        raise ValueError("PIC version mismatch")
    import percolation_inversion_compiler as pic

    if not Path(pic.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise ValueError("PIC is not imported from this isolated environment")
    wheel = OUT / "setup" / "percolation_inversion_compiler-1.1.0-py3-none-any.whl"
    if sha(wheel.read_bytes()) != cfg["pic_distribution_hash"]:
        raise ValueError("PIC wheel hash mismatch")
    panel_dir = OUT / panel
    if (panel_dir / "panel.json").exists():
        raise FileExistsError("panel already started; preserved without automatic retry")
    selected = [t for t in manifest["schedule"] if t["panel"] == panel]
    panel_record: dict[str, Any] = {
        "panel": panel,
        "status": "RUNNING",
        "planned_tasks": len(selected),
        "started_utc": datetime.now(UTC).isoformat(),
    }
    write(panel_dir / "panel.json", panel_record)
    for task in selected:
        for condition in ("initial", "A", "B"):
            write(
                panel_dir / task["task_id"] / f"planned_{condition}.json",
                {
                    "task_id": task["task_id"],
                    "panel": panel,
                    "condition": condition,
                    "attempt_status": "NOT_RUN",
                    "order": task["order"],
                },
            )
    campaign = Campaign(cfg)
    started = time.perf_counter()
    try:
        campaign.model_identity()
        for index, task in enumerate(selected):
            campaign.guard()
            td = panel_dir / task["task_id"]
            write(td / "task_public.json", task)
            initial = campaign.generate(
                INITIAL + task["prompt"], td / "initial", task, "initial", None
            )
            if initial["attempt_status"] not in {"OK", "TRUNCATED"}:
                print(f"{panel} {task['task_id']}: initial {initial['attempt_status']}", flush=True)
                continue
            initial_text = (td / "initial" / "answer.txt").read_text(encoding="utf-8")
            initial_hash = sha(initial_text)
            campaign.guard()
            before = diagnose(
                td / "initial" / "answer.txt",
                td / "initial" / "pic",
                cfg["pic_timeout_seconds"],
                cfg["profile"],
            )
            write(td / "initial" / "diagnosis.json", before)
            # Do not silently convert a failed PIC intervention to generic review.
            pic_valid = all(before[k]["status"] == "parsed" for k in ("check", "intake"))
            for condition in task["order"]:
                if condition == "B" and not pic_valid:
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
                review = GENERIC if condition == "A" else feedback(before)
                record = campaign.generate(
                    revision(task["prompt"], initial_text, review),
                    td / condition,
                    task,
                    condition,
                    initial_hash,
                )
                if record["attempt_status"] in {"OK", "TRUNCATED"}:
                    campaign.guard()
                    diagnosis = diagnose(
                        td / condition / "answer.txt",
                        td / condition / "pic",
                        cfg["pic_timeout_seconds"],
                        cfg["profile"],
                    )
                    write(td / condition / "diagnosis.json", diagnosis)
                    record["pic_status"] = diagnosis["check"]
                    record["missing_obligations"] = diagnosis["intake"]["missing_obligations"]
                    record["residuals"] = diagnosis["intake"]["residuals"]
                    write(td / condition / "record.json", record)
            try:
                ps = requests.get(cfg["ollama_url"] + "/api/ps", timeout=10)
                ps.raise_for_status()
                write(td / "ollama_ps.json", ps.json())
            except (ValueError, requests.RequestException) as exc:
                write(td / "ollama_ps.json", {"error": str(exc)})
            print(
                f"{panel} {index + 1}/{len(selected)} {task['task_id']} "
                f"order={''.join(task['order'])} "
                f"campaign_calls={campaign.data['calls']}",
                flush=True,
            )
        panel_record["status"] = (
            "COMPLETED"
            if all(
                (panel_dir / t["task_id"] / c / "record.json").exists()
                and read(panel_dir / t["task_id"] / c / "record.json")["attempt_status"] == "OK"
                for t in selected
                for c in ("initial", "A", "B")
            )
            else "INCOMPLETE"
        )
    except (BudgetStop, requests.RequestException, KeyboardInterrupt) as exc:
        panel_record["status"] = "INCOMPLETE"
        panel_record["stop_reason"] = str(exc) or "interrupted"
        print(f"Stopped: {panel_record['stop_reason']}", flush=True)
    finally:
        panel_record["elapsed_seconds"] = time.perf_counter() - started
        panel_record["finished_utc"] = datetime.now(UTC).isoformat()
        write(panel_dir / "panel.json", panel_record)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("--phase", choices=["pilot", "main"], required=True)
    r = sub.add_parser("run")
    r.add_argument("--panel", choices=["pilot", "confirmatory", "historical"], required=True)
    args = parser.parse_args()
    if args.command == "freeze":
        freeze(args.phase)
    else:
        run(args.panel)


if __name__ == "__main__":
    main()
