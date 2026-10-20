"""Predeclared semantic and format endpoints; no retrospective scoring changes."""

from __future__ import annotations

import re
from typing import Any

from pic_local_llm_phase_experiment.pic110_oracle import parse_answer
from pic_local_llm_phase_experiment.pic110r2_logic import equal


def canonical_decision(value: Any, kind: str) -> tuple[Any, bool]:
    if kind == "integer" and isinstance(value, str) and re.fullmatch(r"-?(0|[1-9][0-9]*)", value):
        return int(value), True
    if kind == "labels" and isinstance(value, list) and all(isinstance(x, str) for x in value):
        result = sorted(set(value))
        return result, result != value
    return value, False


def citations(value: Any, allowed: list[str]) -> tuple[list[str] | None, bool]:
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        return None, False
    result = []
    for ref in value:
        normalized = ref.strip()
        if normalized.startswith("[") and normalized.endswith("]"):
            normalized = normalized[1:-1].strip()
        if normalized not in allowed:
            return None, False
        result.append(normalized)
    return sorted(set(result)), result != value or len(result) != len(set(result))


def evaluate(text: str | None, gold: dict[str, Any]) -> dict[str, Any]:
    empty = {
        "success": False,
        "substantive_false_completion": None,
        "evidence_incomplete_completion": None,
        "semantic_decision_correct": None,
        "evidence_sufficient": None,
        "format_conformant": False,
        "correct_abstention": None,
        "obligations_correct": None,
        "surface_normalization_used": None,
    }
    if text is None:
        return {**empty, "status": "MISSING"}
    try:
        data = parse_answer(text)
    except (ValueError, TypeError):
        return {**empty, "status": "UNPARSEABLE"}
    decision, normalized = canonical_decision(data.get("decision"), gold["decision_kind"])
    decision_ok = "decision" in data and equal(decision, gold["decision"])
    refs, refs_normalized = citations(data.get("evidence"), gold["allowed_evidence"])
    proof_ok = refs is not None and any(set(s) <= set(refs) for s in gold["minimal_evidence_sets"])
    unresolved = data.get("unresolved")
    obligations_ok = (
        isinstance(unresolved, list)
        and all(isinstance(x, str) for x in unresolved)
        and set(unresolved) == set(gold["unresolved"])
    )
    flag = data.get("complete")
    flag_known = type(flag) is bool
    success = (
        decision_ok and proof_ok and obligations_ok and flag_known and flag is gold["complete"]
    )
    substantive = (
        (not decision_ok or not gold["complete"] or not obligations_ok)
        if flag is True
        else (False if flag is False else None)
    )
    evidence_failure = (not proof_ok) if flag is True else (False if flag is False else None)
    kind_ok = data.get("decision") is None or (
        type(data.get("decision")) is int
        if gold["decision_kind"] == "integer"
        else (
            isinstance(data.get("decision"), list)
            and all(isinstance(x, str) for x in data["decision"])
            and data["decision"] == sorted(set(data["decision"]))
        )
        if gold["decision_kind"] == "labels"
        else isinstance(data.get("decision"), str)
    )
    schema_ok = (
        set(data) == {"decision", "complete", "evidence", "unresolved"}
        and flag_known
        and kind_ok
        and refs is not None
        and isinstance(unresolved, list)
        and all(isinstance(x, str) for x in unresolved)
    )
    return {
        "status": "GRADED",
        "success": bool(success),
        "substantive_false_completion": substantive,
        "evidence_incomplete_completion": evidence_failure,
        "semantic_decision_correct": bool(decision_ok),
        "evidence_sufficient": bool(proof_ok),
        "format_conformant": bool(schema_ok),
        "obligations_correct": bool(obligations_ok),
        "correct_abstention": bool(success) if gold["complete"] is False else None,
        "surface_normalization_used": bool(normalized or refs_normalized),
    }
