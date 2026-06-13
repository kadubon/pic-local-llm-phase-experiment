from pic_local_llm_phase_experiment.metrics import (
    compute_baseline_metrics,
    compute_pic_metrics,
    local_phase_score,
    missing_obligation_reduction_ratio,
)
from pic_local_llm_phase_experiment.schemas import PICReportSummary, TaskSpec


def test_local_phase_score_is_bounded() -> None:
    assert (
        local_phase_score(
            accepted_after=True,
            residual_preservation=10,
            missing_reduction=10,
            repair_completion=10,
            reusable_candidate=10,
        )
        == 1.0
    )
    assert (
        local_phase_score(
            accepted_after=False,
            residual_preservation=-10,
            missing_reduction=-10,
            repair_completion=-10,
            reusable_candidate=-10,
        )
        == 0.0
    )


def test_missing_obligation_reduction_ratio() -> None:
    assert missing_obligation_reduction_ratio(4, 1) == 0.75
    assert missing_obligation_reduction_ratio(0, 0) == 1.0
    assert missing_obligation_reduction_ratio(1, 3) == 0.0


def test_compute_pic_metrics() -> None:
    task = TaskSpec(
        task_id="t",
        title="T",
        prompt="Prompt",
        expected_obligation_types=["benchmark evidence", "risk caveat"],
    )
    before = PICReportSummary(
        accepted=False,
        settled=False,
        residual_summary="Needs benchmark evidence and risk caveat.",
        missing_obligations=["benchmark evidence", "risk caveat"],
        missing_obligation_count=2,
    )
    after = PICReportSummary(
        accepted=True,
        settled=False,
        residual_summary="Risk caveat remains.",
        missing_obligations=["risk caveat"],
        missing_obligation_count=1,
    )

    metrics = compute_pic_metrics(
        task=task,
        initial_report=before,
        repaired_report=after,
        repaired_output="Summary. Evidence: benchmark evidence. Risk: risk caveat. Tests needed.",
    )

    assert metrics["missing_obligation_delta"] == 1
    assert 0 <= metrics["local_phase_score"] <= 1
    assert metrics["pic_accepted_after"] is True


def test_compute_baseline_metrics() -> None:
    task = TaskSpec(
        task_id="t",
        title="T",
        prompt="Prompt",
        expected_obligation_types=["assumptions", "tests"],
    )

    metrics = compute_baseline_metrics(
        task=task,
        initial_answer="Initial",
        self_review="Review",
        final_answer="Summary with assumptions, tests, and unresolved obligations.",
    )

    assert metrics["lists_missing_assumptions"] is True
    assert metrics["preserves_unresolved_obligations"] is True
    assert metrics["heuristic_obligation_coverage"] == 1.0
