import pytest

from pic_local_llm_phase_experiment.ollama_client import OllamaClient, OllamaError


def test_explicit_model_tag_requires_exact_match(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OllamaClient("http://localhost:11434")
    monkeypatch.setattr(client, "list_models", lambda: ["qwen3.5:other-tag"])

    with pytest.raises(OllamaError, match="was not found"):
        client.ensure_model_available("qwen3.5:35b-a3b")


def test_untagged_model_allows_installed_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OllamaClient("http://localhost:11434")
    monkeypatch.setattr(client, "list_models", lambda: ["gemma4:e4b"])

    client.ensure_model_available("gemma4")
