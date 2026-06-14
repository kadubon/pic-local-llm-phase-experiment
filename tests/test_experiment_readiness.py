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

    assert estimate["experiment_mode"] == "separate_initial"
    assert estimate["shared_initial_answer_used"] is False
    assert estimate["shared_initial_generation_count"] == 0
    assert estimate["baseline_generation_count"] == 30
    assert estimate["pic_candidate_generation_count"] == 10
    assert estimate["pic_repair_generation_count"] == 10
    assert estimate["ollama_generation_count"] == 50
    assert estimate["pic_intake_count"] == 20


def test_estimate_experiment_workload_shared_initial_full_run() -> None:
    estimate = estimate_experiment_workload(
        task_count=10,
        repair_rounds=1,
        experiment_mode="shared_initial",
    )

    assert estimate["experiment_mode"] == "shared_initial"
    assert estimate["shared_initial_answer_used"] is True
    assert estimate["shared_initial_generation_count"] == 10
    assert estimate["baseline_generation_count"] == 20
    assert estimate["pic_candidate_generation_count"] == 0
    assert estimate["pic_repair_generation_count"] == 10
    assert estimate["ollama_generation_count"] == 40
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


class SequencedFakeOllamaClient:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.prompts: list[str] = []

    def generate(self, **kwargs) -> OllamaGeneration:
        self.prompts.append(str(kwargs["prompt"]))
        if not self.outputs:
            raise AssertionError("unexpected extra generation")
        return OllamaGeneration(text=self.outputs.pop(0), raw={})


class FakePicRunner:
    def __init__(self) -> None:
        self.candidate_texts: list[str] = []

    def run_intake(
        self,
        *,
        candidate_text: str,
        candidate_path: Path,
        report_path: Path,
        run_dir: Path,
    ) -> PICReportSummary:
        self.candidate_texts.append(candidate_text)
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
    assert manifest["experiment_mode"] == "separate_initial"
    assert manifest["shared_initial_answer_used"] is False
    assert manifest["estimated_ollama_generation_count"] == 5
    assert manifest["estimated_pic_intake_count"] == 2
    assert manifest["workload_estimate"]["experiment_mode"] == "separate_initial"
    assert manifest["workload_estimate"]["ollama_generation_count"] == 5
    assert manifest["timeout_seconds"] == 180
    assert manifest["generation_retries"] == 1
    assert manifest["disable_ollama_thinking"] is True
    assert manifest["abort_on_generation_error"] is True
    assert manifest["pic_setup"]["status"] == "ok"
    assert manifest["pic_setup"]["pic_commit"] == "abc123"
    assert str(tmp_path) not in serialized


def test_shared_initial_run_reuses_same_initial_for_baseline_and_pic(
    tmp_path: Path,
) -> None:
    config_path = _write_minimal_project(tmp_path)
    fake_pic = FakePicRunner()
    runner = ExperimentRunner(
        config=ExperimentConfig(max_tasks=1, experiment_mode="shared_initial"),
        root=tmp_path,
        ollama_client=SequencedFakeOllamaClient(
            [
                "Shared initial with evidence and unresolved obligations.",
                "Self-review notes missing evidence.",
                "Baseline final with evidence and unresolved obligations.",
                "PIC repaired output with evidence, risk, tests, and next steps.",
            ]
        ),
        pic_runner=fake_pic,
        config_path=config_path,
    )

    run_dir = runner.run()
    task_dir = run_dir / "task_001_sample"
    shared_initial = (task_dir / "shared_initial_answer.txt").read_text(encoding="utf-8")
    baseline_initial = (task_dir / "baseline_initial.txt").read_text(encoding="utf-8")
    pic_initial = (task_dir / "pic_initial_candidate.txt").read_text(encoding="utf-8")
    metrics = read_json(task_dir / "metrics.json")
    manifest = read_json(run_dir / "run_manifest.json")

    assert shared_initial == "Shared initial with evidence and unresolved obligations."
    assert baseline_initial == shared_initial
    assert pic_initial == shared_initial
    assert fake_pic.candidate_texts[0] == shared_initial
    assert metrics["experiment_mode"] == "shared_initial"
    assert metrics["shared_initial_answer_used"] is True
    assert metrics["shared_initial_answer_length"] == len(shared_initial)
    assert metrics["baseline_final_length"] > 0
    assert metrics["pic_repaired_output_length"] > 0
    assert metrics["baseline_obligation_coverage"] >= 0
    assert metrics["pic_obligation_coverage"] >= 0
    assert "obligation_coverage_delta" in metrics
    assert metrics["pic_missing_obligation_delta"] == 1
    assert metrics["pic_residual_charge_delta"] == 1.0
    assert metrics["pic_accepted_after"] is True
    assert metrics["pic_operationally_usable_after"] is True
    assert metrics["pic_settled_after"] is False
    assert metrics["pic_schema_fields_usable"] is True
    assert 0 <= metrics["local_phase_score"] <= 1
    assert manifest["experiment_mode"] == "shared_initial"
    assert manifest["shared_initial_answer_used"] is True
    assert manifest["estimated_ollama_generation_count"] == 4
