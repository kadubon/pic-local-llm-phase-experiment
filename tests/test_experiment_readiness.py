import json
import subprocess
from pathlib import Path

from pic_local_llm_phase_experiment.experiment import (
    ExperimentRunner,
    estimate_experiment_workload,
)
from pic_local_llm_phase_experiment.ollama_client import OllamaGeneration
from pic_local_llm_phase_experiment.paths import read_json, write_json, write_text
from pic_local_llm_phase_experiment.pic_runner import PicRunner
from pic_local_llm_phase_experiment.run_cli import main as run_main
from pic_local_llm_phase_experiment.schemas import ExperimentConfig, PICReportSummary


def test_estimate_experiment_workload_default_full_run() -> None:
    estimate = estimate_experiment_workload(task_count=10, repair_rounds=1)

    assert estimate["baseline_generation_count"] == 30
    assert estimate["pic_candidate_generation_count"] == 10
    assert estimate["pic_repair_generation_count"] == 10
    assert estimate["ollama_generation_count"] == 50
    assert estimate["pic_intake_count"] == 20


def test_pic_preflight_reports_success(monkeypatch) -> None:
    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("pic_local_llm_phase_experiment.pic_runner.subprocess.run", fake_run)

    result = PicRunner(profile="development").preflight(cwd=Path("."))

    assert result["ok"] is True
    assert result["checks"]["pic_help"]["ok"] is True
    assert result["checks"]["pic_agent_explain"]["ok"] is True


def test_pic_preflight_reports_missing_command(monkeypatch) -> None:
    def fake_run(args, **kwargs):
        raise FileNotFoundError("pic not found")

    monkeypatch.setattr("pic_local_llm_phase_experiment.pic_runner.subprocess.run", fake_run)

    result = PicRunner(profile="development").preflight(cwd=Path("."))

    assert result["ok"] is False
    assert any("pic_help failed" in error for error in result["errors"])
    assert any("pic_agent_explain failed" in error for error in result["errors"])


class FakeOllamaClient:
    def generate(self, **kwargs) -> OllamaGeneration:
        return OllamaGeneration(
            text=(
                "Summary with evidence, tests, risk, unresolved obligations, "
                "and next steps preserved."
            ),
            raw={},
        )


class FakePicRunner:
    def run_intake(
        self,
        *,
        candidate_text: str,
        candidate_path: Path,
        report_path: Path,
        run_dir: Path,
    ) -> PICReportSummary:
        write_text(candidate_path, candidate_text)
        is_initial = "initial" in report_path.name
        write_json(
            report_path,
            {
                "accepted": not is_initial,
                "operationally_usable": True,
                "settled": False,
                "runtime_report": {"missing_obligations": ["evidence"] if is_initial else []},
                "residual_summary": {"evidence": 1.0} if is_initial else {},
            },
        )
        return PICReportSummary(
            accepted=not is_initial,
            operationally_usable=True,
            settled=False,
            residual_summary="evidence=1" if is_initial else "",
            residual_summary_raw={"evidence": 1.0} if is_initial else {},
            residual_summary_key_count=1 if is_initial else 0,
            residual_charge_total=1.0 if is_initial else 0.0,
            missing_obligations=["evidence"] if is_initial else [],
            missing_obligation_count=1 if is_initial else 0,
            runtime_report_present=True,
            raw_report_path=report_path.relative_to(run_dir).as_posix(),
        )


def _write_minimal_project(root: Path) -> Path:
    tasks_dir = root / "tasks"
    tasks_dir.mkdir()
    write_text(
        tasks_dir / "task_001_sample.yaml",
        "\n".join(
            [
                "task_id: task_001_sample",
                "title: Sample",
                "prompt: Review the sample.",
                "expected_obligation_types:",
                "  - evidence",
            ]
        ),
    )
    config_dir = root / "configs"
    config_dir.mkdir()
    config_path = config_dir / "experiment.default.yaml"
    write_text(config_path, "model: qwen3.5:35b-a3b\n")
    return config_path


def test_run_cli_stops_before_experiment_when_pic_preflight_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    class GoodOllama:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def ensure_model_available(self, model: str) -> None:
            assert model == "qwen3.5:35b-a3b"

        def generate(self, **kwargs) -> OllamaGeneration:
            return OllamaGeneration(text="ready", raw={})

    class BadPic:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def preflight(self, *, cwd: Path) -> dict:
            return {"ok": False, "errors": ["pic_help failed with exit code 127"]}

    monkeypatch.setattr("pic_local_llm_phase_experiment.run_cli.OllamaClient", GoodOllama)
    monkeypatch.setattr("pic_local_llm_phase_experiment.run_cli.PicRunner", BadPic)

    assert run_main(["--config", "configs/experiment.default.yaml"]) == 2
    assert not list((tmp_path / "results" / "runs").glob("*"))


def test_run_manifest_contains_full_readiness_metadata(tmp_path: Path) -> None:
    config_path = _write_minimal_project(tmp_path)
    write_json(
        tmp_path / "results" / "setup_manifest.json",
        {
            "status": "ok",
            "pic_commit": "abc123",
            "pic_version": "0.4.1",
            "pic_agent_explain_available": True,
        },
    )

    runner = ExperimentRunner(
        config=ExperimentConfig(max_tasks=1),
        root=tmp_path,
        ollama_client=FakeOllamaClient(),
        pic_runner=FakePicRunner(),
        config_path=config_path,
    )

    run_dir = runner.run()
    manifest = read_json(run_dir / "run_manifest.json")
    serialized = json.dumps(manifest)

    assert manifest["config_path"] == "configs/experiment.default.yaml"
    assert manifest["task_ids"] == ["task_001_sample"]
    assert manifest["estimated_ollama_generation_count"] == 5
    assert manifest["estimated_pic_intake_count"] == 2
    assert manifest["workload_estimate"]["ollama_generation_count"] == 5
    assert manifest["timeout_seconds"] == 180
    assert manifest["generation_retries"] == 1
    assert manifest["disable_ollama_thinking"] is True
    assert manifest["abort_on_generation_error"] is True
    assert manifest["pic_setup"]["status"] == "ok"
    assert manifest["pic_setup"]["pic_commit"] == "abc123"
    assert str(tmp_path) not in serialized
