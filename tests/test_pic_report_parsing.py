import json
from pathlib import Path

from pic_local_llm_phase_experiment.pic_runner import parse_pic_report

FIXTURES = Path("tests/fixtures")


def test_parse_pic_report_before() -> None:
    report = parse_pic_report(FIXTURES / "sample_pic_report_before.json", base_dir=FIXTURES)

    assert report.accepted is True
    assert report.operationally_usable is True
    assert report.settled is False
    assert report.missing_obligation_count == 2
    assert report.residual_summary == "missing-evidence=1, risk_caveat=0.5"
    assert report.residual_summary_raw == {"missing-evidence": 1.0, "risk_caveat": 0.5}
    assert report.residual_summary_key_count == 2
    assert report.residual_charge_total == 1.5
    assert report.route_execution_request_count == 1
    assert report.agent_task_count == 1
    assert report.runtime_report_present is True
    assert report.raw_report_path == "sample_pic_report_before.json"


def test_parse_pic_report_after() -> None:
    report = parse_pic_report(FIXTURES / "sample_pic_report_after.json", base_dir=FIXTURES)

    assert report.accepted is True
    assert report.operationally_usable is True
    assert report.settled is False
    assert report.missing_obligation_count == 1
    assert report.missing_obligations == ["independent correctness review"]
    assert report.residual_summary_key_count == 1
    assert report.residual_charge_total == 0.25


def test_parse_pic_report_with_missing_optional_fields(tmp_path: Path) -> None:
    report_path = tmp_path / "minimal.json"
    report_path.write_text(json.dumps({"accepted": True}), encoding="utf-8")

    report = parse_pic_report(report_path, base_dir=tmp_path)

    assert report.accepted is True
    assert report.operationally_usable is False
    assert report.settled is False
    assert report.runtime_report_present is False
    assert report.missing_obligation_count == 0
    assert report.residual_summary == ""
