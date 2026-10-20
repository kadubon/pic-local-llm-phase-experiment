"""Independent finite verifier and strong generic ledger. No PIC or gold imports."""

from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from pic_local_llm_phase_experiment.pic110_oracle import parse_answer
from pic_local_llm_phase_experiment.pic110r3_common import AS_OF, canonical, sha


@dataclass(frozen=True)
class EvidenceReceipt:
    evidence_id: str
    source_id: str
    source_sha256: str | None
    trusted: bool
    sufficient: bool
    decision: str
    unresolved: tuple[str, ...]
    reasons: tuple[str, ...]
    facts: dict[str, Any] | None
    cache_hit: bool
    domain_calls: int
    elapsed_seconds: float

    def json(self) -> dict[str, Any]:
        return {**asdict(self), "unresolved": list(self.unresolved), "reasons": list(self.reasons)}


def finite(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def preflight(task: dict, delivered: dict, trust: dict, *, as_of: str = AS_OF) -> list[str]:
    """Checks a pinned authority, not an attacker-selected content hash alone."""
    payload = delivered.get("payload")
    if payload is None:
        return ["missing-evidence"]
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
        not isinstance(payload, dict)
        or set(payload) != fields
        or not isinstance(payload.get("data"), dict)
        or not isinstance(payload.get("receiver_contexts"), list)
        or not all(isinstance(x, str) for x in payload["receiver_contexts"])
        or not all(isinstance(payload[k], str) for k in fields - {"data", "receiver_contexts"})
    ):
        return ["invalid-source-schema"]
    reasons = []
    sid = task["source_id"]
    pinned = trust.get(sid)
    if pinned is None or payload.get("source_id") != sid:
        reasons.append("unknown-source-id")
    try:
        digest = sha(canonical(payload))
    except (ValueError, TypeError):
        return ["invalid-finite-json"]
    if delivered.get("advertised_sha256") != digest:
        reasons.append("content-hash-mismatch")
    if not pinned or pinned["sha256"] != digest:
        reasons.append("trusted-source-digest-mismatch")
    if pinned and payload.get("issuer") != pinned["issuer"]:
        reasons.append("issuer-mismatch")
    if payload.get("scope") != task["scope"] or (
        pinned and task["task_id"] not in pinned["permitted_tasks"]
    ):
        reasons.append("task_scope_mismatch")
    if task["receiver"] not in payload.get("receiver_contexts", []):
        reasons.append("receiver-context-mismatch")
    try:
        now = datetime.fromisoformat(as_of)
        if (
            not datetime.fromisoformat(payload["produced_at"])
            <= now
            < datetime.fromisoformat(payload["expires_at"])
        ):
            reasons.append("expired-or-not-yet-valid")
    except (KeyError, ValueError, TypeError):
        reasons.append("invalid-validity-window")
    if payload.get("domain") != ("numerical" if task["family"] == "reuse" else task["family"]):
        reasons.append("domain-mismatch")
    return sorted(set(reasons))


def domain_check(task: dict, data: dict) -> tuple[bool | None, list[str]]:
    p = task["parameters"]
    if task["family"] in ("numerical", "reuse"):
        values = [data.get("residual"), p["residual_bound"], p["finite_horizon"]]
        if (
            not all(finite(v) for v in values)
            or any(v < 0 for v in values)
            or type(p["finite_horizon"]) is not int
        ):
            return None, ["invalid-numerical-data"]
        return values[0] <= values[1], []
    if task["family"] == "telemetry":
        samples, refs = data.get("samples"), p["references"]
        if not isinstance(samples, list) or not samples or len(samples) != len(refs):
            return None, ["incomplete-telemetry"]
        if not all(finite(v) for v in samples + refs + [p["tolerance"]]) or p["tolerance"] < 0:
            return None, ["invalid-telemetry"]
        if "secondary_samples" in data and data["secondary_samples"] != samples:
            return None, ["conflicting-observations"]
        return all(abs(a - b) <= p["tolerance"] for a, b in zip(samples, refs, strict=True)), []
    events = data.get("events")
    if not isinstance(events, list) or not all(isinstance(v, str) for v in events):
        return None, ["incomplete-trace"]
    return events == p["expected_events"], []


def verify(
    task: dict, delivered: dict, trust: dict, cache: dict | None = None, *, as_of: str = AS_OF
) -> EvidenceReceipt:
    started = time.perf_counter()
    reasons = preflight(task, delivered, trust, as_of=as_of)
    payload = delivered.get("payload")
    hit = False
    calls = 0
    result = None
    try:
        digest = sha(canonical(payload)) if payload is not None else None
    except (TypeError, ValueError):
        digest = None
    key = sha(canonical([task["source_id"], digest, task["parameters"], task["scope"]]))
    if not reasons:
        assert isinstance(payload, dict)
        if cache is not None and key in cache:
            result, domain_reasons = cache[key]
            hit = True
        else:
            calls = 1
            result, domain_reasons = domain_check(task, payload["data"])
            if cache is not None and result is not None:
                cache[key] = (result, domain_reasons)
        reasons.extend(domain_reasons)
    sufficient = not reasons and result is not None
    return EvidenceReceipt(
        evidence_id=task["evidence_id"],
        source_id=task["source_id"],
        source_sha256=digest,
        trusted=not preflight(task, delivered, trust, as_of=as_of),
        sufficient=sufficient,
        decision=("COMPLIANT" if result else "NONCOMPLIANT") if sufficient else "UNKNOWN",
        unresolved=() if sufficient else (task["obligation_id"],),
        reasons=tuple(sorted(set(reasons))),
        facts=payload.get("data") if isinstance(payload, dict) else None,
        cache_hit=hit,
        domain_calls=calls,
        elapsed_seconds=time.perf_counter() - started,
    )


def final_gate(
    text: str | None, receipt: EvidenceReceipt | None, *, pic_ready: bool = True
) -> dict:
    """Common external gate; A has only a schema-level declaration gate."""
    try:
        answer = parse_answer(text or "")
    except (ValueError, TypeError):
        return {"admitted_complete": False, "evidence_supported": False, "reason": "unparseable"}
    schema = (
        set(answer) == {"decision", "complete", "evidence", "unresolved"}
        and type(answer.get("complete")) is bool
        and isinstance(answer.get("decision"), str)
        and answer.get("decision") in {"COMPLIANT", "NONCOMPLIANT", "UNKNOWN"}
        and all(
            isinstance(answer.get(k), list) and all(isinstance(x, str) for x in answer[k])
            for k in ("evidence", "unresolved")
        )
    )
    if receipt is None:
        return {
            "admitted_complete": bool(schema and answer.get("complete") is True),
            "evidence_supported": False,
            "reason": "A-has-no-evidence-gate",
        }
    refs = answer.get("evidence", [])
    normalized_refs = set()
    if isinstance(refs, list) and all(isinstance(s, str) for s in refs):
        for raw in refs:
            ref = raw.strip()
            if ref.startswith("[") and ref.endswith("]"):
                ref = ref[1:-1].strip()
            normalized_refs.add(ref)
    supported = bool(
        schema
        and receipt.trusted
        and receipt.sufficient
        and answer.get("complete") is True
        and answer.get("decision") == receipt.decision
        and answer.get("unresolved") == []
        and normalized_refs == {receipt.evidence_id}
        and pic_ready
    )
    return {
        "admitted_complete": supported,
        "evidence_supported": supported,
        "reason": "supported" if supported else "unresolved-or-mismatched-evidence",
    }
