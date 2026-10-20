"""Bounded R4 inference; never imports the task oracle or parses private gold."""

from __future__ import annotations

import argparse
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pic_local_llm_phase_experiment.pic110_runner import BudgetStop
from pic_local_llm_phase_experiment.pic110_runner import Campaign as BaseCampaign
from pic_local_llm_phase_experiment.pic110r3_runner import allocation_snapshot
from pic_local_llm_phase_experiment.pic110r4_backend import acquire, final_runtime, gate
from pic_local_llm_phase_experiment.pic110r4_common import (
    DATA,
    OUT,
    canonical,
    environment,
    freeze,
    frozen,
    head,
    preservation,
    read,
    settings,
    sha,
    write,
)


class Campaign(BaseCampaign):
    def __init__(self, *, warmup: bool = False):
        self.cfg = settings()
        self.path = OUT / "campaign.json"
        if self.path.exists():
            self.data = read(self.path)
        else:
            self.data = {
                "started_epoch": time.time(),
                "calls": 0,
                "input_tokens_observed": 0,
                "output_tokens_observed": 0,
                "input_tokens_reserved": 0,
                "output_tokens_reserved": 0,
                "consecutive_failures": 0,
                "stopped_reason": None,
                "pilot_started": False,
            }
        if warmup:
            if self.path.exists():
                raise FileExistsError("Warmup already recorded")
            self.cfg["num_predict"] = 64

    def generate(
        self,
        prompt: str,
        folder: Path,
        task: dict[str, Any],
        condition: str,
        initial_hash: str | None,
    ) -> dict[str, Any]:
        result = super().generate(prompt, folder, task, condition, initial_hash)
        count = (result.get("token_usage") or {}).get("input")
        boundary = self.cfg["num_ctx"] - self.cfg["num_predict"]
        result["context_boundary_check"] = (
            "WITHIN_BOUND"
            if type(count) is int and count < boundary
            else "POSSIBLE_CONTEXT_TRUNCATION"
            if type(count) is int
            else "UNAVAILABLE"
        )
        if result["context_boundary_check"] == "POSSIBLE_CONTEXT_TRUNCATION":
            result["attempt_status"] = "CONTEXT_BOUNDARY"
            self.data["stopped_reason"] = "Possible prompt context truncation; no retry"
            write(self.path, self.data)
        write(folder / "record.json", result)
        return result


def prepare() -> None:
    frozen("pilot")
    environment()
    preservation()
    campaign = Campaign(warmup=True)
    task = {"task_id": "r4_warmup", "family": "warmup", "panel": "warmup", "prompt": "Reply READY."}
    result = campaign.generate(task["prompt"], OUT / "warmup", task, "warmup", None)
    if result["attempt_status"] != "OK":
        raise BudgetStop("Warmup failed; record retained without retry")


def run(panel: str) -> None:
    phase = "pilot" if panel == "pilot" else "main"
    frozen(phase)
    environment()
    preservation()
    campaign = Campaign()
    assert campaign.path.exists(), "Run prepare after pilot registration"
    if not campaign.data["pilot_started"]:
        campaign.data.update(started_epoch=time.time(), pilot_started=True)
        write(campaign.path, campaign.data)
    folder = OUT / panel
    folder.mkdir(exist_ok=False)
    cases = {c["task_id"]: c for c in read(DATA / "cases.json") if c["panel"] == panel}
    ordered = [entry for entry in read(OUT / "setup/schedule.json") if entry["task_id"] in cases]
    record: dict = {
        "status": "RUNNING",
        "panel": panel,
        "preregistration_commit": head(),
        "started_utc": datetime.now(UTC).isoformat(),
        "allocation_before": allocation_snapshot(),
    }
    write(folder / "panel.json", record)
    for entry in ordered:
        write(folder / entry["task_id"] / "planned.json", {"minimal": "NOT_RUN", "full": "NOT_RUN"})
    caches: dict = {}
    pic_caches: dict = {}
    started = time.perf_counter()
    try:
        for index, entry in enumerate(ordered):
            frozen(phase)
            campaign.guard()
            case = cases[entry["task_id"]]
            td = folder / case["task_id"]
            cache = caches.setdefault(case["episode"], {})
            pic_cache = pic_caches.setdefault(case["episode"], {})
            acquisition = acquire(case, td / "evidence", cache, pic_cache)
            prompts = {
                "minimal": case["prompt"]
                + "\nVERIFIED MATERIAL\n"
                + canonical(acquisition["compact"]).decode(),
                "full": case["prompt"]
                + "\nVERIFIED MATERIAL\n"
                + canonical(acquisition["detailed"]).decode(),
            }
            write(
                td / "design.json",
                {
                    "shared_compact_prompt_hash": sha(prompts["minimal"].encode()),
                    "G_P_minimal_identical": True,
                    "model_replay_not_independent_samples": True,
                },
            )
            for arm in entry["order"]:
                result = campaign.generate(prompts[arm], td / arm, case, arm, None)
                answer_file = td / arm / "answer.txt"
                text = answer_file.read_text(encoding="utf-8") if answer_file.exists() else None
                for backend in ["generic", "pic"] if arm == "minimal" else ["pic"]:
                    write(td / arm / f"gate_{backend}.json", gate(text, acquisition, backend))
                final_runtime(case, td / "evidence", text, td / arm / "final_pic_runtime.json")
                print(
                    f"{panel} {index + 1}/{len(ordered)} {case['task_id']} "
                    f"{arm} {result['attempt_status']}",
                    flush=True,
                )
        record["status"] = "COMPLETED"
    except (BudgetStop, ValueError, OSError, RuntimeError, AssertionError) as exc:
        record.update(status="INCOMPLETE", stop_reason=str(exc))
    finally:
        record.update(
            elapsed_seconds=time.perf_counter() - started,
            finished_utc=datetime.now(UTC).isoformat(),
            allocation_after=allocation_snapshot(),
        )
        write(folder / "panel.json", record)
        preservation()
        environment()
    print(record, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "prepare", "run"])
    parser.add_argument("--phase", choices=["pilot", "main"], default="pilot")
    parser.add_argument("--panel", choices=["pilot", "confirmatory"], default="pilot")
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.phase)
    elif args.action == "prepare":
        prepare()
    else:
        run(args.panel)


if __name__ == "__main__":
    main()
