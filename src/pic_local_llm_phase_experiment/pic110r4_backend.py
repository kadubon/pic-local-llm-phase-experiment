"""Unmodified PIC 1.1.0 versus a strong generic cache with shared trust policy."""

from __future__ import annotations

import time
from pathlib import Path

from percolation_inversion_compiler.runtime.algorithms import build_runtime_step
from percolation_inversion_compiler.runtime.records import AgentRuntimeConfig, RuntimeStepInput

from pic_local_llm_phase_experiment.pic110_oracle import parse_answer
from pic_local_llm_phase_experiment.pic110r3_pic_adapter import diagnose, feedback, state
from pic_local_llm_phase_experiment.pic110r3_verifiers import verify
from pic_local_llm_phase_experiment.pic110r4_common import canonical, read, sha, write


def cache_key(task: dict, delivered: dict) -> str:
    payload = delivered.get("payload")
    digest = sha(canonical(payload)) if payload is not None else None
    return sha(canonical([task["source_id"], digest, task["parameters"], task["scope"]]))


def acquire(case: dict, folder: Path, cache: dict, pic_cache: dict) -> dict:
    receipts, pics, generic_times, pic_times = [], [], [], []
    for index, task in enumerate(case["components"]):
        delivered = case["delivery"][task["source_id"]]
        receipt = verify(task, delivered, case["trust"], cache)
        key = cache_key(task, delivered)
        saved = pic_cache.get(key)
        pic = diagnose(
            task,
            delivered,
            receipt,
            folder / f"c{index}",
            cached_native=saved["native"] if saved else None,
            producer_packet=saved["protected_packet"] if saved else None,
        )
        if pic["pic_ready"]:
            pic_cache[key] = pic
        receipts.append(receipt.json())
        pics.append(pic)
        generic_times.append(receipt.elapsed_seconds)
        pic_times.append(pic["elapsed_seconds"])
    compact = {
        "receipts": [
            {
                "evidence_id": r["evidence_id"],
                "source_id": r["source_id"],
                "status": "UNKNOWN"
                if not r["sufficient"]
                else "PASS"
                if r["decision"] == "COMPLIANT"
                else "FAIL",
                "unresolved": r["unresolved"],
                "reasons": r["reasons"],
                "facts": r["facts"],
            }
            for r in receipts
        ]
    }
    detailed = {**compact, "PIC": [feedback(p) for p in pics]}
    result = {
        "receipts": receipts,
        "pics": pics,
        "compact": compact,
        "detailed": detailed,
        "generic_seconds": sum(generic_times),
        "pic_seconds": sum(pic_times),
    }
    write(folder / "acquisition.json", result)
    return result


def states(acquisition: dict, backend: str) -> list[str]:
    result = []
    for receipt, pic in zip(acquisition["receipts"], acquisition["pics"], strict=True):
        if not receipt["sufficient"] or not receipt["trusted"]:
            result.append("UNKNOWN")
        elif backend == "generic":
            result.append("PASS" if receipt["decision"] == "COMPLIANT" else "FAIL")
        elif not pic["pic_ready"]:
            result.append("UNKNOWN")
        else:
            result.append("PASS" if pic["native"][0]["result"]["accepted"] else "FAIL")
    return result


def gate(text: str | None, acquisition: dict, backend: str) -> dict:
    started = time.perf_counter()
    admitted = False
    try:
        answer = parse_answer(text or "")
        refs = answer.get("evidence")
        schema = (
            set(answer) == {"decision", "complete", "evidence", "unresolved"}
            and answer.get("complete") is True
            and isinstance(refs, list)
            and all(isinstance(x, str) for x in refs)
            and answer.get("unresolved") == []
        )
        if schema and isinstance(refs, list):
            normalized = set()
            for raw in refs:
                ref = raw.strip()
                normalized.add(
                    ref[1:-1].strip() if ref.startswith("[") and ref.endswith("]") else ref
                )
            all_ids = {r["evidence_id"] for r in acquisition["receipts"]}
            statuses = states(acquisition, backend)
            fail_ids = {
                r["evidence_id"]
                for r, s in zip(acquisition["receipts"], statuses, strict=True)
                if s == "FAIL"
            }
            admitted = normalized <= all_ids and (
                answer.get("decision") == "NONCOMPLIANT"
                and bool(normalized & fail_ids)
                or answer.get("decision") == "COMPLIANT"
                and all(s == "PASS" for s in statuses)
                and normalized == all_ids
            )
    except (ValueError, TypeError):
        pass
    return {
        "admitted_complete": bool(admitted),
        "backend": backend,
        "elapsed_seconds": time.perf_counter() - started,
    }


def final_runtime(case: dict, folder: Path, text: str | None, destination: Path) -> dict:
    incoming = [
        RuntimeStepInput.model_validate(read(folder / f"c{j}" / "step_input.json"))
        for j in range(3)
    ]
    merged = RuntimeStepInput(
        input_id=case["task_id"],
        allow_live_connectors=False,
        agent_output=text,
        evidence_envelopes=[e for item in incoming for e in item.evidence_envelopes],
        packets=[p for item in incoming for p in item.packets],
    )
    started = time.perf_counter()
    report = build_runtime_step(
        state(case["task_id"]),
        merged,
        AgentRuntimeConfig(profile="development", allow_live_connectors=False),
    )
    value = {
        "report": report.model_dump(mode="json"),
        "elapsed_seconds": time.perf_counter() - started,
    }
    write(destination, value)
    return value
