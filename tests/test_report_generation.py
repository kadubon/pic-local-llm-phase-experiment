from pic_local_llm_phase_experiment.report import render_report


def test_report_contains_required_non_claims() -> None:
    rows = [
        {
            "task_id": "task_001",
            "run_id": "20260101-000000",
            "baseline_heuristic_obligation_coverage": 0.4,
            "pic_heuristic_obligation_coverage": 0.8,
            "pic_missing_obligation_delta": 1,
            "pic_local_phase_score": 0.75,
            "pic_residual_summary_length_before": 32,
            "pic_pic_accepted_after": True,
        }
    ]
    report = render_report(
        rows=rows,
        manifest={
            "run_id": "20260101-000000",
            "model": "qwen3.5:35b-a3b",
            "repair_rounds": 1,
        },
        setup_manifest={"pic_commit": "abc123"},
    )

    assert "not a measure of real ASI" in report
    assert "PIC did not prove real ASI" in report
    assert "local, small-sample, model-dependent" in report
    assert "| task_id |" in report


def test_report_generation_from_dummy_results_has_threats() -> None:
    rows = [
        {
            "task_id": "task_002",
            "baseline_heuristic_obligation_coverage": 1.0,
            "pic_heuristic_obligation_coverage": 1.0,
            "pic_missing_obligation_delta": 0,
            "pic_local_phase_score": 0.5,
            "pic_residual_summary_length_before": 0,
            "pic_pic_accepted_after": False,
        }
    ]

    report = render_report(rows=rows)

    assert "one model only" in report
    assert "possible parser/schema drift if PIC changes" in report
