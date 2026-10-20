"""Fresh three-source episodes with explicit context changes; no model execution."""

from __future__ import annotations

import copy
import random

from pic_local_llm_phase_experiment.pic110r4_common import (
    DATA,
    OUT,
    ROOT,
    canonical,
    read,
    settings,
    sha,
    write,
)

RULE = (
    "Decide whether ALL THREE finite constraints hold using only the supplied verifier receipts. "
    "Return exactly one JSON object with decision, complete, evidence, unresolved. "
    "decision is COMPLIANT, NONCOMPLIANT or UNKNOWN; complete is a JSON boolean; "
    "evidence and unresolved are string arrays. Any verified FAIL is a sufficient negative "
    "proof: NONCOMPLIANT, complete=true, cite at least one FAIL receipt, unresolved=[]. "
    "COMPLIANT needs all three verified PASS receipts, complete=true and unresolved=[]. "
    "With no FAIL and at least one UNKNOWN, return UNKNOWN, complete=false; evidence may "
    "be empty or cite supplied receipt IDs; unresolved must contain the obligation IDs of "
    "UNKNOWN components. A proved violation is a complete determination. "
    "Citation order, duplicates, outer whitespace and one pair of square brackets are "
    "equivalent. Extra citations must still be supplied receipt IDs. "
    "PIC framework settlement is separate from this finite ALL-THREE decision. "
    "A draft is not evidence. No tools or live sources are available to the model."
)


def prompt(case: dict) -> str:
    return (
        RULE
        + "\nTASK\n"
        + canonical(
            {
                "task_id": case["task_id"],
                "components": [
                    {k: c[k] for k in ("source_id", "evidence_id", "obligation_id")}
                    for c in case["components"]
                ],
            }
        ).decode()
        + '\nUNVERIFIED DRAFT\n{"decision":"COMPLIANT","complete":true,'
        '"evidence":["draft:ready"],"unresolved":[]}'
    )


def dataset() -> list[dict]:
    result = []
    for panel, count in (("pilot", 1), ("confirmatory", 8)):
        for e in range(count):
            episode = f"r4_{panel}_{e:02d}"
            originals: list[dict] = []
            tasks: list[dict] = []
            permitted = [f"{episode}_s{s}_c{j}" for s in range(4) for j in range(3)]
            for j, family in enumerate(("numerical", "telemetry", "trace")):
                fail = e % 2 == 1 and j == (e + 1) % 3
                data = (
                    {"residual": 0.75 if fail else 0.125}
                    if j == 0
                    else {"samples": [10, 21 if fail else 20]}
                    if j == 1
                    else {"events": ["start", "end"] if fail else ["start", "check", "end"]}
                )
                parameters = (
                    {"residual_bound": 0.5, "finite_horizon": 8}
                    if j == 0
                    else {"references": [10, 20], "tolerance": 0.25}
                    if j == 1
                    else {"expected_events": ["start", "check", "end"]}
                )
                sid = f"source:{episode}:{j}"
                payload: dict = {
                    "source_id": sid,
                    "scope": f"scope:{episode}",
                    "issuer": "r4-finite-lab",
                    "receiver_contexts": ["consumer:lab"],
                    "produced_at": "2026-01-01T00:00:00+00:00",
                    "expires_at": "2100-01-01T00:00:00+00:00",
                    "domain": family,
                    "data": data,
                }
                originals.append(payload)
                tasks.append(
                    {
                        "source_id": sid,
                        "scope": payload["scope"],
                        "receiver": "consumer:lab",
                        "family": family,
                        "parameters": parameters,
                    }
                )
            for step in range(4):
                components, delivery, trust = [], {}, {}
                for j in range(3):
                    task = copy.deepcopy(tasks[j])
                    payload = copy.deepcopy(originals[j])
                    task.update(
                        task_id=f"{episode}_s{step}_c{j}",
                        evidence_id=f"ev:{episode}_s{step}:{j}",
                        obligation_id=f"ob:{episode}_s{step}:{j}",
                    )
                    grant = list(permitted)
                    if step == 2:
                        if e == 0 and j == 0:
                            task["receiver"] = "consumer:other"
                        elif e == 1 and j == 2:
                            task["scope"] += ":other"
                        elif e == 2 and j == 1:
                            payload["expires_at"] = "2026-10-19T00:00:00+00:00"
                        elif e == 3 and j == 1:
                            payload["data"]["samples"] = [10, 20]
                        elif e == 5 and j == 0:
                            grant.remove(task["task_id"])
                        elif e == 6 and j == 0:
                            task["parameters"]["residual_bound"] = 0.0625
                        elif e == 7 and j == 1:
                            payload["data"]["secondary_samples"] = [10, 22]
                    if step == 3:
                        # A genuine new source version; even/odd episodes reverse their outcome.
                        if j == 0:
                            payload["data"]["residual"] = 0.75 if e % 2 == 0 else 0.125
                        elif j == 1:
                            payload["data"]["samples"] = [10, 20]
                        else:
                            payload["data"]["events"] = ["start", "check", "end"]
                    digest = sha(canonical(payload))
                    trust[task["source_id"]] = {
                        "sha256": digest,
                        "issuer": payload["issuer"],
                        "scope": payload["scope"],
                        "permitted_tasks": grant,
                    }
                    delivered = copy.deepcopy(payload)
                    if step == 2 and e == 4 and j == 0:
                        delivered["data"]["residual"] = 0
                    delivery[task["source_id"]] = {
                        "payload": None if step == 1 and j == e % 3 else delivered,
                        "advertised_sha256": sha(canonical(delivered)),
                    }
                    components.append(task)
                case = {
                    "task_id": f"{episode}_s{step}",
                    "episode": episode,
                    "panel": panel,
                    "family": "three_source_conjunction",
                    "step": step,
                    "components": components,
                    "delivery": delivery,
                    "trust": trust,
                }
                case["prompt"] = prompt(case)
                result.append(case)
    return result


def schedule() -> list[dict]:
    rng = random.Random(settings()["order_seed"])
    cases = read(DATA / "cases.json")
    ordered = []
    for panel in ("pilot", "confirmatory"):
        episodes = sorted({c["episode"] for c in cases if c["panel"] == panel})
        rng.shuffle(episodes)
        for episode_index, episode in enumerate(episodes):
            for case in sorted(
                (c for c in cases if c["episode"] == episode), key=lambda c: c["step"]
            ):
                first = (episode_index + case["step"]) % 2 == 0
                order = ["minimal", "full"] if first else ["full", "minimal"]
                ordered.append({"task_id": case["task_id"], "order": order})
    return ordered


def build() -> None:
    from pic_local_llm_phase_experiment.pic110r4_oracle import expected

    cases = dataset()
    write(DATA / "cases.json", cases, exclusive=True)
    write(OUT / "setup/gold.json", {c["task_id"]: expected(c) for c in cases}, exclusive=True)
    write(OUT / "setup/schedule.json", schedule(), exclusive=True)
    write(ROOT / "configs/experiment.pic-v1.1.0-r4.json", settings(), exclusive=True)


if __name__ == "__main__":
    build()
