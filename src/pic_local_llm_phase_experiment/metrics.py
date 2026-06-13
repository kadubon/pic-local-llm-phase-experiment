from __future__ import annotations

import re
from statistics import mean
from typing import Any

from pic_local_llm_phase_experiment.schemas import PICReportSummary, TaskSpec


def bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_obligation(text: str, obligation: str) -> bool:
    haystack = _normalize(text)
    needle = _normalize(obligation.replace("_", " ").replace("-", " "))
    if not needle:
        return False
    if needle in haystack:
        return True
    tokens = [token for token in re.findall(r"[a-z0-9]+", needle) if len(token) >= 4]
    if not tokens:
        return False
    return any(token in haystack for token in tokens)


def obligation_coverage_score(text: str, expected_obligation_types: list[str]) -> float:
    if not expected_obligation_types:
        return 1.0
    hits = sum(
        1 for obligation in expected_obligation_types if _contains_obligation(text, obligation)
    )
    return bounded(hits / len(expected_obligation_types))


def lists_missing_assumptions(text: str) -> bool:
    normalized = _normalize(text)
    patterns = (
        "missing assumption",
        "assumptions",
        "unknown",
        "unresolved",
        "not specified",
        "not provided",
    )
    return any(pattern in normalized for pattern in patterns)


def preserves_unresolved_obligations(text: str) -> bool:
    normalized = _normalize(text)
    patterns = (
        "unresolved obligation",
        "remaining obligation",
        "missing obligation",
        "still needed",
        "not yet verified",
    )
    return any(pattern in normalized for pattern in patterns)


def self_contradiction_flags(text: str) -> int:
    normalized = _normalize(text)
    patterns = (
        "contradiction",
        "inconsistent",
        "cannot both",
        "conflicts with",
        "on the other hand",
    )
    return sum(1 for pattern in patterns if pattern in normalized)


def candidate_reuse_score(text: str) -> float:
    normalized = _normalize(text)
    markers = (
        "summary",
        "acceptance criteria",
        "evidence",
        "tests",
        "risk",
        "unresolved",
        "next step",
    )
    hits = sum(1 for marker in markers if marker in normalized)
    return bounded(hits / 5)


def missing_obligation_reduction_ratio(before: int, after: int) -> float:
    if before <= 0:
        return 1.0 if after <= 0 else 0.0
    return bounded((before - after) / before)


def residual_preservation_score(
    missing_obligations_before: list[str],
    residual_summary_before: str,
    repaired_text: str,
) -> float:
    components: list[float] = []
    if missing_obligations_before:
        hits = sum(
            1
            for obligation in missing_obligations_before
            if _contains_obligation(repaired_text, obligation)
        )
        components.append(hits / len(missing_obligations_before))
    if residual_summary_before:
        residual_terms = [
            token
            for token in re.findall(r"[a-z0-9]+", _normalize(residual_summary_before))
            if len(token) >= 5
        ]
        if residual_terms:
            matched = sum(1 for token in set(residual_terms) if token in _normalize(repaired_text))
            components.append(matched / len(set(residual_terms)))
    if not components:
        return 1.0 if repaired_text.strip() else 0.0
    return bounded(mean(components))


def local_phase_score(
    *,
    accepted_after: bool,
    residual_preservation: float,
    missing_reduction: float,
    repair_completion: float,
    reusable_candidate: float,
) -> float:
    score = (
        (0.20 * float(accepted_after))
        + (0.20 * bounded(residual_preservation))
        + (0.25 * bounded(missing_reduction))
        + (0.20 * bounded(repair_completion))
        + (0.15 * bounded(reusable_candidate))
    )
    return bounded(score)


def compute_baseline_metrics(
    *,
    task: TaskSpec,
    initial_answer: str,
    self_review: str,
    final_answer: str,
) -> dict[str, Any]:
    return {
        "answer_length": len(initial_answer),
        "self_review_length": len(self_review),
        "final_answer_length": len(final_answer),
        "lists_missing_assumptions": lists_missing_assumptions(final_answer),
        "preserves_unresolved_obligations": preserves_unresolved_obligations(final_answer),
        "heuristic_obligation_coverage": obligation_coverage_score(
            final_answer, task.expected_obligation_types
        ),
        "self_contradiction_flags": self_contradiction_flags(final_answer),
        "candidate_reuse_score": candidate_reuse_score(final_answer),
    }


def compute_pic_metrics(
    *,
    task: TaskSpec,
    initial_report: PICReportSummary,
    repaired_report: PICReportSummary,
    repaired_output: str,
) -> dict[str, Any]:
    before = initial_report.missing_obligation_count
    after = repaired_report.missing_obligation_count
    missing_reduction = missing_obligation_reduction_ratio(before, after)
    preservation = residual_preservation_score(
        initial_report.missing_obligations,
        initial_report.residual_summary,
        repaired_output,
    )
    repair_completion = 1.0 if repaired_output.strip() else 0.0
    reuse = candidate_reuse_score(repaired_output)
    return {
        "missing_obligation_count_before": before,
        "missing_obligation_count_after": after,
        "missing_obligation_delta": before - after,
        "missing_obligation_reduction_ratio": missing_reduction,
        "residual_summary_length_before": len(initial_report.residual_summary),
        "residual_summary_length_after": len(repaired_report.residual_summary),
        "pic_accepted_before": initial_report.accepted,
        "pic_accepted_after": repaired_report.accepted,
        "pic_settled_before": initial_report.settled,
        "pic_settled_after": repaired_report.settled,
        "repair_attempt_count": 1 if repaired_output.strip() else 0,
        "obligation_preservation_score": preservation,
        "self_contradiction_flags": self_contradiction_flags(repaired_output),
        "candidate_reuse_score": reuse,
        "heuristic_obligation_coverage": obligation_coverage_score(
            repaired_output, task.expected_obligation_types
        ),
        "pic_report_fields_usable": not (
            initial_report.command_failed or repaired_report.command_failed
        ),
        "llm_responded_to_pic_residuals": preservation > 0,
        "local_phase_score": local_phase_score(
            accepted_after=repaired_report.accepted,
            residual_preservation=preservation,
            missing_reduction=missing_reduction,
            repair_completion=repair_completion,
            reusable_candidate=reuse,
        ),
    }
