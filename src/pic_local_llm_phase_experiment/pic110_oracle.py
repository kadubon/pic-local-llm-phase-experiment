"""Independent deterministic grading. No PIC or model imports; no code execution."""

from __future__ import annotations

import json
from typing import Any


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def parse_answer(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```json\n") and text.endswith("\n```"):
        text = text[8:-4]
    elif text.startswith("```\n") and text.endswith("\n```"):
        text = text[4:-4]
    data = json.loads(
        text,
        object_pairs_hook=_unique_pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")),
    )
    if not isinstance(data, dict):
        raise ValueError("expected one JSON object")
    return data


def evaluate(text: str | None, gold: dict[str, Any]) -> dict[str, Any]:
    if text is None:
        return {
            "success": False,
            "false_completion": None,
            "status": "missing",
            "valid_evidence": None,
            "correct_abstention": None,
            "unresolved_preserved": None,
        }
    try:
        data = parse_answer(text)
    except (ValueError, TypeError):
        return {
            "success": False,
            "false_completion": None,
            "status": "invalid_json",
            "valid_evidence": False,
            "correct_abstention": False,
            "unresolved_preserved": False,
        }
    evidence, unresolved = data.get("evidence"), data.get("unresolved")
    schema_ok = (
        set(data) == {"decision", "complete", "evidence", "unresolved"}
        and type(data.get("complete")) is bool
        and isinstance(evidence, list)
        and all(isinstance(x, str) for x in evidence)
        and isinstance(unresolved, list)
        and all(isinstance(x, str) for x in unresolved)
    )
    ev_ok = (
        isinstance(evidence, list)
        and all(isinstance(x, str) for x in evidence)
        and len(evidence) == len(set(evidence))
        and set(evidence) <= set(gold["allowed_evidence"])
        and any(set(s) <= set(evidence) for s in gold["minimal_evidence_sets"])
    )
    decision_ok = (
        type(data.get("decision")) is type(gold["decision"])
        and data.get("decision") == gold["decision"]
    )
    if isinstance(gold["decision"], list) and isinstance(data.get("decision"), list):
        decision_ok = data["decision"] == sorted(gold["decision"])
    obligations_ok = (
        isinstance(unresolved, list)
        and all(isinstance(x, str) for x in unresolved)
        and len(unresolved) == len(set(unresolved))
        and set(unresolved) == set(gold["unresolved"])
    )
    success = (
        schema_ok
        and decision_ok
        and ev_ok
        and obligations_ok
        and data.get("complete") is gold["complete"]
    )
    # Claims of completion with a wrong decision, absent required support, or an
    # undisclosed obligation are unsupported. Unreadable/missing claims are unknown.
    fc = (
        (not (decision_ok and ev_ok and obligations_ok and gold["complete"]))
        if data.get("complete") is True
        else (False if data.get("complete") is False else None)
    )
    return {
        "success": bool(success),
        "false_completion": fc,
        "status": "graded" if schema_ok else "invalid_schema",
        "valid_evidence": bool(ev_ok),
        "correct_abstention": bool(success) if gold["decision"] is None else None,
        "unresolved_preserved": bool(obligations_ok),
        "expected_unresolved_count": len(gold["unresolved"]),
    }
