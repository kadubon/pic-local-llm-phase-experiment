"""Finite-model oracle and exhaustive minimal-proof search. No PIC or model dependency."""

from __future__ import annotations

import itertools
import json
from typing import Any


def equal(a: Any, b: Any) -> bool:
    return type(a) is type(b) and a == b


def outcome(task: dict[str, Any], world: dict[str, Any]) -> dict[str, Any]:
    rule = task["rule"]
    kind = rule["kind"]
    decision: Any = None
    unresolved: list[str] = []
    if kind == "linear":
        decision = sum(world[name] * weight for name, weight in rule["terms"])
        if "conditional_add" in rule:
            flag, value = rule["conditional_add"]
            decision += world[value] if world[flag] else 0
    elif kind in {"limit", "retention"}:
        active = max(
            (p for p in rule["policies"] if p["effective"] <= rule["date"]),
            key=lambda p: p["effective"],
        )["variable"]
        if rule.get("availability") and not world[rule["availability"]]:
            unresolved = ["active-policy-record"]
        elif kind == "limit":
            decision = "permit" if rule["amount"] <= world[active] else "deny"
        else:
            decision = world[active]
    elif kind == "approval":
        if not world["available"]:
            unresolved = ["approval-record"]
        elif not world["signed"]:
            unresolved = ["approval-signature"]
        else:
            decision = "permit" if world["approved"] else "deny"
    elif kind == "consensus":
        if world["lab_a"] != world["lab_b"]:
            unresolved = ["reconcile-reports"]
        else:
            decision = "pass" if world["lab_a"] else "fail"
    elif kind == "rows":
        labels = rule["labels"]
        identifiers = [world[f"{label}_id"] for label in labels]
        decision = sorted(
            label
            for label in labels
            if (
                type(world[f"{label}_qty"]) is not int
                or world[f"{label}_qty"] < 1
                or world[f"{label}_status"] not in {"new", "done"}
                or identifiers.count(world[f"{label}_id"]) > 1
            )
        )
    elif kind == "checksum":
        if not world["artifact_available"]:
            unresolved = ["observed-digest"]
        else:
            decision = "pass" if world["observed"] == rule["expected"] else "fail"
    elif kind == "strict_json":
        pairs = json.loads(world["raw"], object_pairs_hook=list)
        keys = [k for k, _ in pairs]
        record = dict(pairs)
        reading: Any = record.get("reading")
        valid = (
            len(keys) == len(set(keys))
            and set(keys) == {"id", "reading"}
            and isinstance(record.get("id"), str)
            and type(reading) in (int, float)
            and 0 <= reading <= 1
        )
        decision = "pass" if valid else "fail"
    else:
        raise ValueError("unknown fixed rule kind")
    return {"decision": decision, "complete": not bool(unresolved), "unresolved": unresolved}


def worlds(task: dict[str, Any]) -> list[dict[str, Any]]:
    names = list(task["domains"])
    return [
        dict(zip(names, values, strict=True))
        for values in itertools.product(*(task["domains"][n] for n in names))
    ]


def matches(world: dict[str, Any], source: dict[str, Any]) -> bool:
    return all(equal(world[k], v) for k, v in source["facts"].items())


def derive(task: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    possible = worlds(task)
    sources = task["sources"]
    masks = [{i for i, w in enumerate(possible) if matches(w, source)} for source in sources]
    all_indices = set(range(len(possible)))
    full = set.intersection(all_indices, *masks)
    if not full:
        raise ValueError("inconsistent task records")
    outcomes = [outcome(task, w) for w in possible]
    target = outcomes[min(full)]
    if any(outcomes[i] != target for i in full):
        raise ValueError("full records do not determine the epistemic decision")
    minimal: list[tuple[int, ...]] = []
    witnesses = []
    for size in range(len(sources) + 1):
        for subset in itertools.combinations(range(len(sources)), size):
            if any(set(proof) <= set(subset) for proof in minimal):
                continue
            candidates = set.intersection(all_indices, *(masks[i] for i in subset))
            if candidates and all(outcomes[i] == target for i in candidates):
                minimal.append(subset)
                drops = []
                for dropped in subset:
                    reduced = tuple(i for i in subset if i != dropped)
                    alternatives = set.intersection(all_indices, *(masks[i] for i in reduced))
                    witness = next(i for i in sorted(alternatives) if outcomes[i] != target)
                    drops.append(
                        {
                            "removed": sources[dropped]["id"],
                            "counterexample_world": possible[witness],
                            "counterexample_outcome": outcomes[witness],
                        }
                    )
                witnesses.append(
                    {
                        "ids": [sources[i]["id"] for i in subset],
                        "compatible_worlds": len(candidates),
                        "necessity": drops,
                    }
                )
    gold = {
        **target,
        "minimal_evidence_sets": [[sources[i]["id"] for i in subset] for subset in minimal],
        "allowed_evidence": [s["id"] for s in sources],
        "decision_kind": task["decision_kind"],
    }
    audit = {
        "task_id": task["task_id"],
        "world_count": len(possible),
        "full_compatible_worlds": len(full),
        "all_minimal_proofs": witnesses,
        "method": "exhaustive finite-model entailment and deletion counterexamples",
    }
    return gold, audit
