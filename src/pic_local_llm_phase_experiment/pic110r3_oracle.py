"""Independent exact outcome specification. Does not consume verifier/PIC results."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from fractions import Fraction
from typing import Any

from pic_local_llm_phase_experiment.pic110_oracle import parse_answer
from pic_local_llm_phase_experiment.pic110r3_common import AS_OF


def gold(task: dict, observed: dict, authorities: dict) -> dict:
    try:
        return _gold(task, observed, authorities)
    except (ValueError, TypeError, KeyError, IndexError, OverflowError):
        return {
            "decision": "UNKNOWN",
            "complete": False,
            "evidence_id": task["evidence_id"],
            "unresolved": [task["obligation_id"]],
        }


def _gold(task: dict, observed: dict, authorities: dict) -> dict:
    """Separate trust validation and exact rational/event-index specification."""
    value: Any = observed.get("payload")
    pinned: Any = authorities.get(task["source_id"])
    usable = value is not None and pinned is not None
    if usable:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        digest = hashlib.sha256(encoded).hexdigest()
        usable = (
            digest == pinned["sha256"] == observed.get("advertised_sha256")
            and value.get("source_id") == task["source_id"]
            and value.get("issuer") == pinned["issuer"]
            and value.get("scope") == task["scope"]
            and task["task_id"] in pinned["permitted_tasks"]
            and task["receiver"] in value["receiver_contexts"]
            and datetime.fromisoformat(value["produced_at"])
            <= datetime.fromisoformat(AS_OF)
            < datetime.fromisoformat(value["expires_at"])
            and value.get("domain")
            == ("numerical" if task["family"] == "reuse" else task["family"])
        )
    compliant = None
    if usable:
        data, p = value["data"], task["parameters"]
        if task["family"] in ("numerical", "reuse"):
            a, b = Fraction(str(data["residual"])), Fraction(str(p["residual_bound"]))
            usable = (
                a >= 0 and b >= 0 and type(p["finite_horizon"]) is int and p["finite_horizon"] >= 0
            )
            compliant = a - b <= 0
        elif task["family"] == "telemetry":
            samples, reference = data["samples"], p["references"]
            usable = (
                bool(samples)
                and len(samples) == len(reference)
                and Fraction(str(p["tolerance"])) >= 0
            )
            usable &= data.get("secondary_samples", samples) == samples
            if usable:
                errors = sorted(
                    abs(Fraction(str(samples[i])) - Fraction(str(reference[i])))
                    for i in range(len(samples))
                )
                compliant = errors[-1] <= Fraction(str(p["tolerance"]))
        else:
            sequence, requirement = data["events"], p["expected_events"]
            compliant = len(sequence) == len(requirement) and not any(
                sequence[i] != requirement[i] for i in range(min(len(sequence), len(requirement)))
            )
    return {
        "decision": ("COMPLIANT" if compliant else "NONCOMPLIANT") if usable else "UNKNOWN",
        "complete": bool(usable),
        "evidence_id": task["evidence_id"],
        "unresolved": [] if usable else [task["obligation_id"]],
    }


def evaluate(text: str | None, expected: dict, *, evidence_access: bool) -> dict:
    missing = {
        "success": False,
        "unsupported_completion": None,
        "citation_only_failure": None,
        "format_conformant": False,
        "correct_abstention": False if not expected["complete"] else None,
        "obligations_correct": False,
        "lost_obligations": None,
        "supported_completion": False,
    }
    try:
        result = parse_answer(text or "")
    except (ValueError, TypeError):
        return {**missing, "status": "UNPARSEABLE" if text else "MISSING"}
    flag = result.get("complete")
    evidence, unresolved = result.get("evidence"), result.get("unresolved")
    schema = (
        set(result) == {"decision", "complete", "evidence", "unresolved"}
        and type(flag) is bool
        and isinstance(result.get("decision"), str)
        and result.get("decision") in {"COMPLIANT", "NONCOMPLIANT", "UNKNOWN"}
        and isinstance(evidence, list)
        and all(isinstance(x, str) for x in evidence)
        and isinstance(unresolved, list)
        and all(isinstance(x, str) for x in unresolved)
    )
    refs: set[str] | None = set() if isinstance(evidence, list) and not evidence else None
    if isinstance(evidence, list) and all(isinstance(x, str) for x in evidence):
        refs = set()
        for item in evidence:
            ref = item.strip()
            if ref.startswith("[") and ref.endswith("]"):
                ref = ref[1:-1].strip()
            refs.add(ref)
    cited = refs == {expected["evidence_id"]} and evidence_access
    proof = cited if expected["complete"] else refs == set() or cited
    obligations = (
        isinstance(unresolved, list)
        and all(isinstance(x, str) for x in unresolved)
        and set(unresolved) == set(expected["unresolved"])
    )
    correct = result.get("decision") == expected["decision"]
    success = bool(schema and correct and flag is expected["complete"] and proof and obligations)
    unsupported = (
        bool(not expected["complete"] or not correct or not obligations or not evidence_access)
        if flag is True
        else False
        if flag is False
        else None
    )
    return {
        "status": "GRADED",
        "success": success,
        "unsupported_completion": unsupported,
        "citation_only_failure": bool(
            expected["complete"] and correct and obligations and not cited
        )
        if flag is True and evidence_access
        else False
        if type(flag) is bool
        else None,
        "format_conformant": bool(schema),
        "canonical_citation_notation": bool(
            schema and evidence == ([] if not evidence else [expected["evidence_id"]])
        ),
        "correct_abstention": success if not expected["complete"] else None,
        "obligations_correct": bool(obligations),
        "lost_obligations": sorted(set(expected["unresolved"]) - set(unresolved))
        if isinstance(unresolved, list) and all(isinstance(x, str) for x in unresolved)
        else None,
        "supported_completion": bool(success and expected["complete"]),
        "decision_correct": bool(correct),
    }
