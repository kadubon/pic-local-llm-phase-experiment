from pathlib import Path

from pic_local_llm_phase_experiment.pic_runner import parse_pic_report

FIXTURES = Path("tests/fixtures")


def test_parse_pic_report_before() -> None:
    report = parse_pic_report(FIXTURES / "sample_pic_report_before.json", base_dir=FIXTURES)

    assert report.accepted is False
    assert report.settled is False
    assert report.missing_obligation_count == 2
    assert "evidence" in report.residual_summary
    assert report.raw_report_path == "sample_pic_report_before.json"


def test_parse_pic_report_after() -> None:
    report = parse_pic_report(FIXTURES / "sample_pic_report_after.json", base_dir=FIXTURES)

    assert report.accepted is True
    assert report.missing_obligation_count == 1
    assert report.missing_obligations == ["independent correctness review"]
