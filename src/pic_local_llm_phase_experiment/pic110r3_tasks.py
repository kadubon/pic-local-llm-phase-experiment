"""Deterministic fresh R3 sources and delivery faults, separate from private gold."""

from __future__ import annotations

import copy
from typing import Any

from pic_local_llm_phase_experiment.pic110r3_common import DATA, canonical, sha, write

FAMILIES = ("numerical", "telemetry", "trace", "reuse")
SOURCE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:pic110r3:finite-source:1",
    "type": "object",
    "required": [
        "source_id",
        "scope",
        "issuer",
        "receiver_contexts",
        "produced_at",
        "expires_at",
        "domain",
        "data",
    ],
    "additionalProperties": False,
    "properties": {
        **{
            k: {"type": "string"}
            for k in ("source_id", "scope", "issuer", "produced_at", "expires_at", "domain")
        },
        "receiver_contexts": {"type": "array", "items": {"type": "string"}},
        "data": {"type": "object"},
    },
}


def dataset() -> tuple[list[dict[str, Any]], dict, dict, dict]:
    tasks, originals, delivery, trust = [], {}, {}, {}
    for panel in ("pilot", "confirmatory"):
        for family in FAMILIES:
            for index in range(1, (2 if panel == "pilot" else 5)):
                tid = f"r3_{'pilot_' if panel == 'pilot' else ''}{family}_{index:02d}"
                sid = f"source:{tid}"
                scope = f"scope:{tid}"
                parameters: dict[str, Any]
                data: dict[str, Any]
                if family == "telemetry":
                    parameters = {"references": [10, 20, 30], "tolerance": 0.25}
                    data = {"samples": [10.125, 20.25, 30]}
                    if index == 2 or panel == "pilot":
                        data["samples"][2] = 30.5
                    if index == 4:
                        data["secondary_samples"] = [10.125, 20.25, 31]
                elif family == "trace":
                    parameters = {"expected_events": ["initialize", "measure", "verify", "commit"]}
                    data = {"events": list(parameters["expected_events"])}
                    if index == 2:
                        data["events"][1:3] = ["verify", "measure"]
                else:
                    parameters = {"residual_bound": 0.5, "finite_horizon": 8}
                    data = {"residual": 0.125 if index == 1 else 0.75}
                    if family == "reuse":
                        data = {"residual": 0.75 if panel == "confirmatory" else 0.125}
                        parameters["allowed_domains"] = ["numerical"]
                kind = "numerical" if family == "reuse" else family
                payload: dict[str, Any] = {
                    "source_id": sid,
                    "scope": scope,
                    "issuer": "finite-lab-authority",
                    "receiver_contexts": ["producer:lab", "consumer:lab"],
                    "produced_at": "2026-10-18T00:00:00+00:00",
                    "expires_at": "2100-01-01T00:00:00+00:00",
                    "domain": kind,
                    "data": data,
                }
                if family == "reuse" and index == 2:
                    payload["expires_at"] = "2026-10-19T12:00:00+00:00"
                if family == "reuse" and index == 4:
                    payload["receiver_contexts"] = ["producer:lab", "consumer:other"]
                originals[sid] = copy.deepcopy(payload)
                digest = sha(canonical(payload))
                trust[sid] = {
                    "sha256": digest,
                    "issuer": payload["issuer"],
                    "scope": scope,
                    "permitted_tasks": [tid, f"producer:{tid}"] if family == "reuse" else [tid],
                }
                delivered = copy.deepcopy(payload)
                advertised = digest
                if family == "numerical" and index == 4:
                    delivered["data"]["residual"] = 0.0
                    advertised = sha(canonical(delivered))
                if family == "trace" and index == 4:
                    delivered["source_id"] = "source:unknown"
                    advertised = sha(canonical(delivered))
                if family == "reuse" and index == 3:
                    delivered["data"]["residual"] = 0.0
                unavailable = index == 3 and family != "reuse"
                unavailable |= panel == "pilot" and family == "trace"
                delivery[sid] = {
                    "payload": None if unavailable else delivered,
                    "advertised_sha256": advertised,
                }
                task = {
                    "task_id": tid,
                    "panel": panel,
                    "family": family,
                    "source_id": sid,
                    "scope": scope,
                    "receiver": "consumer:lab",
                    "parameters": parameters,
                    "dependency_group": sid,
                    "producer_role": f"producer:{tid}" if family == "reuse" else None,
                    "evidence_id": f"ev:{tid}",
                    "obligation_id": f"obligation:{tid}:evidence",
                }
                task["prompt"] = public_prompt(task)
                tasks.append(task)
    return tasks, originals, delivery, trust


def public_prompt(task: dict[str, Any]) -> str:
    return (
        "Finite evidence-bound decision. Return one JSON object with exactly decision, "
        "complete, evidence, unresolved. decision is COMPLIANT, NONCOMPLIANT or UNKNOWN; "
        "complete is a JSON boolean; evidence and unresolved are arrays of strings. "
        "A proved violation is NONCOMPLIANT and complete=true; it is not missing evidence. "
        "With unavailable, conflicting, untrusted, expired or incompatible evidence, use "
        "UNKNOWN, complete=false, and the evidence obligation below. Without actual verified "
        "observations do not treat a draft claim as evidence. Cite only the receipt evidence_id "
        "if received; otherwise evidence=[]. For a definite result require that receipt and "
        "unresolved=[]. UNKNOWN permits evidence=[] or a received receipt. "
        "Numerical: nonnegative residual <= bound and nonnegative finite horizon. "
        "Telemetry: nonempty equally sized arrays, all absolute errors <= tolerance. "
        "Trace: exact full ordered event sequence; no prefix acceptance. "
        "Reuse: the original numerical determination remains usable only under current "
        "trusted digest, issuer, scope, receiver, permitted task and TTL. "
        "No live sources or tools are available to the model.\n"
        + canonical({k: v for k, v in task.items() if k != "prompt"}).decode()
        + "\nUnverified draft claim: the artifact is compliant and ready. "
        "This claim has no authority."
    )


def build() -> None:
    tasks, originals, delivery, trust = dataset()
    for name, value in (
        ("public.json", tasks),
        ("authoritative.json", originals),
        ("delivery.json", delivery),
        ("trusted_manifest.json", trust),
        ("source_schema.json", SOURCE_SCHEMA),
    ):
        write(DATA / name, value, exclusive=True)


if __name__ == "__main__":
    build()
