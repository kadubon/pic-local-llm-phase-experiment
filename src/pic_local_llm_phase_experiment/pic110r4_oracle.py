"""Independent source-based R4 oracle and decomposed answer scoring, analysis only."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from fractions import Fraction

from pic_local_llm_phase_experiment.pic110_oracle import parse_answer


def source_status(task: dict, delivered: dict, trust: dict) -> str:
    try:
        p = delivered["payload"]
        fields = {
            "source_id",
            "scope",
            "issuer",
            "receiver_contexts",
            "produced_at",
            "expires_at",
            "domain",
            "data",
        }
        if (
            not isinstance(p, dict)
            or set(p) != fields
            or not isinstance(p["data"], dict)
            or not isinstance(p["receiver_contexts"], list)
            or not all(isinstance(x, str) for x in p["receiver_contexts"])
            or not all(isinstance(p[k], str) for k in fields - {"data", "receiver_contexts"})
        ):
            return "UNKNOWN"
        pin = trust[task["source_id"]]
        digest = hashlib.sha256(
            json.dumps(p, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        ).hexdigest()
        usable = (
            p["source_id"] == task["source_id"]
            and digest == delivered["advertised_sha256"] == pin["sha256"]
            and p["issuer"] == pin["issuer"]
            and p["scope"] == task["scope"]
            and task["task_id"] in pin["permitted_tasks"]
            and task["receiver"] in p["receiver_contexts"]
            and p["domain"] == task["family"]
            and datetime.fromisoformat(p["produced_at"])
            <= datetime.fromisoformat("2026-10-20T00:00:00+00:00")
            < datetime.fromisoformat(p["expires_at"])
        )
        if not usable:
            return "UNKNOWN"
        data, spec = p["data"], task["parameters"]
        if task["family"] == "numerical":
            a, b = Fraction(str(data["residual"])), Fraction(str(spec["residual_bound"]))
            if (
                min(a, b) < 0
                or type(spec["finite_horizon"]) is not int
                or spec["finite_horizon"] < 0
            ):
                return "UNKNOWN"
            passed = a <= b
        elif task["family"] == "telemetry":
            values, refs = data["samples"], spec["references"]
            if (
                not values
                or len(values) != len(refs)
                or data.get("secondary_samples", values) != values
            ):
                return "UNKNOWN"
            tolerance = Fraction(str(spec["tolerance"]))
            if tolerance < 0:
                return "UNKNOWN"
            passed = (
                max(
                    abs(Fraction(str(values[i])) - Fraction(str(refs[i]))) for i in range(len(refs))
                )
                <= tolerance
            )
        else:
            actual, wanted = data["events"], spec["expected_events"]
            if not isinstance(actual, list) or not all(isinstance(x, str) for x in actual):
                return "UNKNOWN"
            passed = len(actual) == len(wanted) and all(
                actual[i] == wanted[i] for i in range(len(wanted))
            )
        return "PASS" if passed else "FAIL"
    except (KeyError, TypeError, ValueError, OverflowError):
        return "UNKNOWN"


def expected(case: dict) -> dict:
    statuses = [
        source_status(t, case["delivery"][t["source_id"]], case["trust"])
        for t in case["components"]
    ]
    decision = (
        "NONCOMPLIANT"
        if "FAIL" in statuses
        else "COMPLIANT"
        if all(s == "PASS" for s in statuses)
        else "UNKNOWN"
    )
    return {
        "decision": decision,
        "complete": decision != "UNKNOWN",
        "statuses": statuses,
        "evidence_ids": [t["evidence_id"] for t in case["components"]],
        "negative_witnesses": [
            t["evidence_id"]
            for t, s in zip(case["components"], statuses, strict=True)
            if s == "FAIL"
        ],
        "unresolved": [
            t["obligation_id"]
            for t, s in zip(case["components"], statuses, strict=True)
            if s == "UNKNOWN"
        ]
        if decision == "UNKNOWN"
        else [],
    }


def normalized(values: object) -> set[str] | None:
    if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
        return None
    result = set()
    for value in values:
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1].strip()
        result.add(value)
    return result


def score(text: str | None, gold: dict, *, admitted: bool) -> dict:
    empty = {
        "decision_correct": False,
        "supported_success": False,
        "contract_success": False,
        "unsupported_completion": None,
        "unsafe_admission": bool(admitted),
        "citation_valid": False,
        "obligations_correct": False,
        "format_conformant": False,
        "supported_yield": False,
    }
    try:
        obj = parse_answer(text or "")
    except (ValueError, TypeError):
        return {**empty, "status": "UNPARSEABLE" if text else "MISSING"}
    flag = obj.get("complete")
    refs, obligations = normalized(obj.get("evidence")), normalized(obj.get("unresolved"))
    schema = (
        set(obj) == {"decision", "complete", "evidence", "unresolved"}
        and type(flag) is bool
        and isinstance(obj.get("decision"), str)
        and obj["decision"] in {"COMPLIANT", "NONCOMPLIANT", "UNKNOWN"}
        and refs is not None
        and obligations is not None
    )
    correct = obj.get("decision") == gold["decision"] and flag is gold["complete"]
    citation = refs is not None and refs <= set(gold["evidence_ids"])
    proof = (
        refs is not None
        and citation
        and (
            not gold["complete"]
            or (
                set(gold["evidence_ids"]) <= refs
                if gold["decision"] == "COMPLIANT"
                else bool(refs & set(gold["negative_witnesses"]))
            )
        )
    )
    supported = bool(schema and correct and proof)
    return {
        "status": "GRADED",
        "decision_correct": bool(correct),
        "supported_success": supported,
        "contract_success": supported and obligations == set(gold["unresolved"]),
        "unsupported_completion": bool(not correct or not proof)
        if flag is True
        else False
        if flag is False
        else None,
        "unsafe_admission": bool(admitted and not (supported and gold["complete"])),
        "citation_valid": bool(citation),
        "obligations_correct": obligations == set(gold["unresolved"]),
        "format_conformant": bool(schema),
        "supported_yield": bool(admitted and supported and gold["complete"]),
    }
