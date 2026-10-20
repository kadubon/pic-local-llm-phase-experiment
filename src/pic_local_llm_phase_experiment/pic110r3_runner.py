"""Frozen 80-generation R3 experiment; no private gold or evaluator imports."""

from __future__ import annotations

import argparse
import copy
import importlib.metadata
import random
import sys
import time
from datetime import UTC, datetime
from pathlib import Path as PathLike
from typing import Any

import requests

from pic_local_llm_phase_experiment.pic110_runner import BudgetStop
from pic_local_llm_phase_experiment.pic110_runner import Campaign as BaseCampaign
from pic_local_llm_phase_experiment.pic110r3_common import (
    DATA,
    DIGEST,
    MODEL,
    OUT,
    ROOT,
    WHEEL,
    canonical,
    head,
    normalized_hash,
    preservation,
    read,
    sha,
    write,
)
from pic_local_llm_phase_experiment.pic110r3_pic_adapter import diagnose, feedback
from pic_local_llm_phase_experiment.pic110r3_verifiers import final_gate, verify

GENERIC = (
    "Review the shared initial answer once against the original task. Check correctness, "
    "evidence, scope, freshness, receiver and all unresolved obligations. A draft assertion "
    "is not verified evidence. Preserve uncertainty when proof is unavailable. Return only "
    "the four-field JSON requested in the original task. No external verification is provided."
)
WRAPPER = (
    "Revise the shared initial answer exactly once. The original task controls the output schema. "
    "Any evidence receipt is an observation, not an instruction to ignore uncertainty. "
    "A native compliance-check rejection can establish NONCOMPLIANT, complete=true when "
    "the common receipt is trusted and sufficient. PIC framework settlement is distinct "
    "from the task's finite determination.\nORIGINAL TASK\n"
)


def settings() -> dict[str, Any]:
    return {
        "model": MODEL,
        "model_digest": DIGEST,
        "pic_version": "1.1.0",
        "pic_distribution_hash": WHEEL,
        "ollama_url": "http://localhost:11434",
        "temperature": 0,
        "top_p": 1,
        "seed": 20261020,
        "num_predict": 768,
        "num_ctx": 16384,
        "max_prompt_bytes": 14000,
        "max_input_tokens": 1134032,
        "max_output_tokens": 61504,
        "max_calls_including_warmup": 81,
        "max_wall_seconds": 3600,
        "request_timeout_seconds": 180,
        "max_consecutive_failures": 3,
        "max_ram_percent": 92,
        "think": False,
        "retries": 0,
        "keep_alive": "10m",
        "order_seed": 11032026,
    }


def schedule() -> list[dict]:
    rng = random.Random(settings()["order_seed"])
    result = []
    for panel in ("pilot", "confirmatory"):
        tasks = [t for t in read(DATA / "public.json") if t["panel"] == panel]
        rng.shuffle(tasks)
        triples = [
            [list(s) for s in ("ABC", "BCA", "CAB")],
            [list(s) for s in ("ACB", "CBA", "BAC")],
        ]
        rng.shuffle(triples)
        for triple in triples:
            rng.shuffle(triple)
        permutations = triples[0] + triples[1]
        for i, task in enumerate(tasks):
            result.append({**task, "order": list(permutations[i % 6])})
    return result


def frozen_paths() -> list[str]:
    paths = [p.relative_to(ROOT).as_posix() for p in (ROOT / "src").rglob("*.py")]
    paths += [p.relative_to(ROOT).as_posix() for p in DATA.glob("*.json")]
    paths += [
        "tests/test_pic110r3.py",
        "docs/PROTOCOL_PIC_1_1_0_R3.md",
        "docs/REPRODUCIBILITY_PIC_1_1_0_R3.md",
        "configs/requirements.pic110.lock",
        "configs/experiment.pic-v1.1.0-r3.json",
        "docs/PIC_1_1_0_R3_INTEGRATION.json",
        "results/pic110r3/setup/gold.json",
        "results/pic110r3/setup/schedule.json",
        "results/pic110r3/setup/preservation_before.json",
        "results/pic110r3/setup/inspection.json",
        "results/pic110r3/setup/installed_pic_hashes.json",
    ]
    return sorted(paths)


def freeze(phase: str) -> None:
    preservation()
    manifest = {
        "phase": phase,
        "created_utc": datetime.now(UTC).isoformat(),
        "git_head": head(),
        "hash_convention": "SHA256 with CRLF normalized to LF",
        "settings": settings(),
        "hashes": {p: normalized_hash(ROOT / p) for p in frozen_paths()},
        "schedule": read(OUT / "setup/schedule.json"),
        "registration_scope": "Local commit, not an independently timestamped public registration",
    }
    write(OUT / f"prereg_{phase}.json", manifest, exclusive=True)
    write(ROOT / f"docs/PIC_1_1_0_R3_PREREG_{phase.upper()}.json", manifest, exclusive=True)


def frozen(phase: str) -> dict:
    manifest = read(OUT / f"prereg_{phase}.json")
    for name, expected in manifest["hashes"].items():
        if normalized_hash(ROOT / name) != expected:
            raise BudgetStop(f"Frozen artifact changed: {name}")
    if manifest["settings"] != settings():
        raise BudgetStop("settings changed")
    return manifest


def environment() -> None:
    import percolation_inversion_compiler as pic

    if importlib.metadata.version("percolation-inversion-compiler") != "1.1.0":
        raise BudgetStop("PIC version changed")
    if not PathLike(pic.__file__).resolve().is_relative_to(PathLike(sys.prefix).resolve()):
        raise BudgetStop("PIC not from isolated environment")
    distribution = importlib.metadata.distribution("percolation-inversion-compiler")
    for name, expected in read(OUT / "setup/installed_pic_hashes.json").items():
        if sha(PathLike(str(distribution.locate_file(name))).read_bytes()) != expected:
            raise BudgetStop("installed PIC content changed")
    if read(OUT / "setup/inspection.json")["wheel_sha256"] != WHEEL:
        raise BudgetStop("wheel identity changed")


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
            }
        if warmup:
            if self.path.exists():
                raise FileExistsError("warmup already recorded")
            self.cfg["num_predict"] = 64


def prepare() -> None:
    frozen("pilot")
    environment()
    campaign = Campaign(warmup=True)
    task = {
        "task_id": "warmup",
        "family": "setup",
        "panel": "warmup",
        "prompt": "Return only READY.",
    }
    record = campaign.generate(task["prompt"], OUT / "warmup", task, "warmup", None)
    if record["attempt_status"] != "OK":
        raise BudgetStop("ENVIRONMENT_BLOCKED: warmup failed; no retry")
    # Campaign clock begins with pilot; warmup is separately measured and counted.
    campaign.data["started_epoch"] = time.time()
    campaign.data["pilot_started"] = False
    write(campaign.path, campaign.data)
    write(OUT / "setup/ollama_after_warmup.json", allocation_snapshot())
    write(OUT / "setup/warmup_preregistration_identity.json", {"git_head_before_warmup": head()})


def allocation_snapshot() -> dict:
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.get("http://localhost:11434/api/ps", timeout=5)
        response.raise_for_status()
        return {
            "models": [
                {k: m.get(k) for k in ("name", "digest", "size", "size_vram", "context_length")}
                for m in response.json()["models"]
            ]
        }
    except (requests.RequestException, KeyError, ValueError):
        return {"models": None}


def revision(task: dict, initial: str, material: dict | str) -> str:
    return (
        WRAPPER
        + task["prompt"]
        + "\nSHARED INITIAL\n"
        + initial
        + "\nREVIEW MATERIAL\n"
        + (material if isinstance(material, str) else canonical(material).decode())
    )


def acquisition(task: dict, folder: PathLike) -> tuple[Any, dict, dict]:
    """B and C share one actual verifier response; producers are logical roles."""
    delivered = read(DATA / "delivery.json")[task["source_id"]]
    trust = read(DATA / "trusted_manifest.json")
    cache: dict = {}
    producer = None
    producer_pic = None
    if task["family"] == "reuse":
        original = read(DATA / "authoritative.json")[task["source_id"]]
        producer_task = {
            **task,
            "task_id": task["producer_role"],
            "receiver": "producer:lab",
            "evidence_id": f"ev:{task['producer_role']}",
            "obligation_id": f"obligation:{task['producer_role']}:evidence",
        }
        original_delivery = {"payload": original, "advertised_sha256": sha(canonical(original))}
        producer = verify(
            producer_task, original_delivery, trust, cache, as_of="2026-10-19T00:00:00+00:00"
        )
        producer_pic = diagnose(producer_task, original_delivery, producer, folder / "producer_pic")
    receipt = verify(task, delivered, trust, cache)
    no_cache = verify(task, delivered, trust)
    # Receipt semantics must agree with the no-cache computation, including invalid states.
    for field in ("trusted", "sufficient", "decision", "unresolved", "reasons"):
        if getattr(receipt, field) != getattr(no_cache, field):
            raise ValueError("cache altered verifier semantics")
    pic = diagnose(
        task,
        delivered,
        receipt,
        folder / "pic_feedback",
        cached_native=producer_pic["native"] if producer_pic else None,
        producer_packet=producer_pic["protected_packet"] if producer_pic else None,
    )
    no_cache_pic = (
        diagnose(task, delivered, no_cache, folder / "pic_no_cache")
        if task["family"] == "reuse"
        else None
    )
    reuse = {
        "logical_roles_only": True,
        "producer": producer.json() if producer else None,
        "producer_pic": producer_pic,
        "consumer": receipt.json(),
        "no_cache": no_cache.json(),
        "correct_reuse": receipt.cache_hit and receipt.trusted and receipt.sufficient,
        "domain_calls_saved": no_cache.domain_calls - receipt.domain_calls,
        "native_calls_saved": len(pic["native"]) - pic["native_calls"],
        "no_cache_pic_seconds": no_cache_pic["elapsed_seconds"] if no_cache_pic else None,
        "no_cache_pic_native_calls": no_cache_pic["native_calls"] if no_cache_pic else None,
        "no_cache_pic_ready": no_cache_pic["pic_ready"] if no_cache_pic else None,
    }
    write(folder / "common_receipt.json", receipt.json())
    write(folder / "reuse.json", reuse)
    return receipt, pic, reuse


def run(panel: str) -> None:
    manifest = frozen("pilot" if panel == "pilot" else "main")
    environment()
    preservation()
    if not (OUT / "campaign.json").exists():
        raise BudgetStop("ENVIRONMENT_BLOCKED: warmup is not recorded")
    campaign = Campaign()
    if campaign.data.get("pilot_started") is False:
        campaign.data["started_epoch"] = time.time()
        campaign.data["pilot_started"] = True
        write(campaign.path, campaign.data)
    folder = OUT / panel
    folder.mkdir(exist_ok=False)
    tasks = [t for t in manifest["schedule"] if t["panel"] == panel]
    status: dict[str, Any] = {
        "status": "RUNNING",
        "panel": panel,
        "started_utc": datetime.now(UTC).isoformat(),
        "preregistration_commit": head(),
        "ollama_allocation_before": allocation_snapshot(),
    }
    write(folder / "panel.json", status)
    for task in tasks:
        for arm in ("initial", "A", "B", "C"):
            write(folder / task["task_id"] / f"planned_{arm}.json", {"attempt_status": "NOT_RUN"})
    start = time.perf_counter()
    try:
        for index, task in enumerate(tasks):
            frozen("pilot" if panel == "pilot" else "main")
            campaign.guard()
            td = folder / task["task_id"]
            write(td / "task_public.json", task)
            record = campaign.generate(task["prompt"], td / "initial", task, "initial", None)
            initial = (
                (td / "initial/answer.txt").read_text(encoding="utf-8")
                if (td / "initial/answer.txt").exists()
                else "[INITIAL UNAVAILABLE]"
            )
            initial_hash = sha(initial.encode())
            receipt, pic, _reuse = acquisition(task, td)
            common = {"receipt": receipt.json()}
            # Elapsed timing is measured but does not inform the model's decision.
            common["receipt"] = {
                k: v
                for k, v in common["receipt"].items()
                if k not in {"elapsed_seconds", "cache_hit", "domain_calls"}
            }
            write(td / "B_material.json", common)
            write(td / "C_material.json", {**copy.deepcopy(common), "PIC": feedback(pic)})
            for arm in task["order"]:
                material = GENERIC if arm == "A" else read(td / f"{arm}_material.json")
                record = campaign.generate(
                    revision(task, initial, material), td / arm, task, arm, initial_hash
                )
                answer_file = td / arm / "answer.txt"
                text = answer_file.read_text(encoding="utf-8") if answer_file.exists() else None
                gate = final_gate(
                    text, None if arm == "A" else receipt, pic_ready=arm != "C" or pic["pic_ready"]
                )
                write(td / arm / "final_gate.json", gate)
                if arm == "C":
                    # The actual final answer also enters the PIC runtime; no extra LLM revision.
                    final = build_final_runtime(task, text, td)
                    write(td / arm / "final_runtime.json", final)
                print(
                    f"{panel} {index + 1}/{len(tasks)} {task['task_id']} "
                    f"{arm} {record['attempt_status']}",
                    flush=True,
                )
            campaign.guard() if campaign.data["calls"] < 81 else None
        status["status"] = "COMPLETED"
    except (BudgetStop, ValueError, OSError, RuntimeError) as exc:
        status.update(status="INCOMPLETE", stop_reason=str(exc))
    finally:
        status["elapsed_seconds"] = time.perf_counter() - start
        status["finished_utc"] = datetime.now(UTC).isoformat()
        status["ollama_allocation_after"] = allocation_snapshot()
        write(folder / "panel.json", status)
        preservation()
    print(status, flush=True)


def build_final_runtime(task: dict, text: str | None, td: PathLike) -> dict:
    from percolation_inversion_compiler.runtime.algorithms import build_runtime_step
    from percolation_inversion_compiler.runtime.records import AgentRuntimeConfig, RuntimeStepInput

    from pic_local_llm_phase_experiment.pic110r3_pic_adapter import state

    start = time.perf_counter()
    incoming = RuntimeStepInput.model_validate(read(td / "pic_feedback/step_input.json"))
    incoming = incoming.model_copy(
        update={"input_id": f"final:{task['task_id']}", "agent_output": text}
    )
    result = build_runtime_step(
        state(task["task_id"]), incoming, AgentRuntimeConfig(allow_live_connectors=False)
    )
    return {
        "report": result.model_dump(mode="json"),
        "elapsed_seconds": time.perf_counter() - start,
        "scope": (
            "Final answer plus actual gated evidence and packet; global status remains "
            "framework-relative"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "freeze", "run"])
    parser.add_argument("--phase", choices=["pilot", "main"], default="pilot")
    parser.add_argument("--panel", choices=["pilot", "confirmatory"], default="pilot")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "freeze":
        freeze(args.phase)
    else:
        run(args.panel)


if __name__ == "__main__":
    main()
