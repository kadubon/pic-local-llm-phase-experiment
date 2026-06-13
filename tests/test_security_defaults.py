from pathlib import Path

from pic_local_llm_phase_experiment.schemas import ExperimentConfig


def test_no_cloud_llm_dependencies() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8").lower()

    assert "openai" not in pyproject
    assert "anthropic" not in pyproject
    assert "google-generativeai" not in pyproject


def test_default_config_requires_no_api_key() -> None:
    config = ExperimentConfig()

    assert config.ollama_url == "http://localhost:11434"
    assert config.model == "qwen3.5:35b-a3b"
