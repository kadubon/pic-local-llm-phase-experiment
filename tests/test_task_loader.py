from pathlib import Path

import pytest

from pic_local_llm_phase_experiment.schemas import ExperimentConfig
from pic_local_llm_phase_experiment.task_loader import load_config, load_task

FIXTURES = Path("tests/fixtures")


def test_load_task_yaml() -> None:
    task = load_task(FIXTURES / "sample_task.yaml")

    assert task.task_id == "sample_task"
    assert task.expected_obligation_types == [
        "benchmark evidence",
        "correctness evidence",
        "assumptions",
    ]


def test_load_config_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "model: qwen3.5:35b-a3b",
                "ollama_url: http://localhost:11434",
                "temperature: 0",
                "top_p: 1",
                "seed: 42",
                "num_predict: 128",
                "max_tasks: 2",
                "repair_rounds: 1",
                "pic_profile: development",
                "output_dir: results/runs",
                "timeout_seconds: 30",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.model == "qwen3.5:35b-a3b"
    assert config.output_dir.as_posix() == "results/runs"


def test_config_rejects_nonlocal_ollama_url() -> None:
    with pytest.raises(ValueError, match="local Ollama"):
        ExperimentConfig(ollama_url="https://api.example.invalid")
