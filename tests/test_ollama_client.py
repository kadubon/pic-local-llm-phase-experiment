import json

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


class FakeStreamResponse:
    def __init__(self, lines: list[dict], status_code: int = 200) -> None:
        self.lines = lines
        self.status_code = status_code
        self.text = "error text"

    def __enter__(self) -> "FakeStreamResponse":
        return self

    def __exit__(self, *args) -> None:
        return None

    def iter_lines(self, decode_unicode: bool = False):
        assert decode_unicode is True
        for line in self.lines:
            yield json.dumps(line)


def test_generate_streams_and_joins_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args, **kwargs) -> FakeStreamResponse:
        assert kwargs["json"]["stream"] is True
        assert kwargs["json"]["think"] is False
        assert kwargs["stream"] is True
        return FakeStreamResponse(
            [
                {"response": "ready", "done": False},
                {"response": " now", "done": False},
                {"response": "", "done": True, "done_reason": "stop"},
            ]
        )

    monkeypatch.setattr("pic_local_llm_phase_experiment.ollama_client.requests.post", fake_post)
    client = OllamaClient("http://localhost:11434", generation_retries=0)

    generation = client.generate(
        model="qwen3.5:35b-a3b",
        prompt="Prompt",
        temperature=0,
        top_p=1,
        seed=42,
        num_predict=32,
    )

    assert generation.text == "ready now"
    assert generation.raw["streamed"] is True
    assert generation.raw["attempt_count"] == 1


def test_generate_retries_empty_stream_response(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = [
        FakeStreamResponse([{"response": "", "done": True}]),
        FakeStreamResponse([{"response": "nonempty", "done": True}]),
    ]

    def fake_post(*args, **kwargs) -> FakeStreamResponse:
        return responses.pop(0)

    monkeypatch.setattr("pic_local_llm_phase_experiment.ollama_client.requests.post", fake_post)
    client = OllamaClient("http://localhost:11434", generation_retries=1)

    generation = client.generate(
        model="qwen3.5:35b-a3b",
        prompt="Prompt",
        temperature=0,
        top_p=1,
        seed=42,
        num_predict=32,
    )

    assert generation.text == "nonempty"
    assert generation.raw["attempt_count"] == 2
    assert generation.raw["empty_retry_count"] == 1


def test_generate_fails_after_empty_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args, **kwargs) -> FakeStreamResponse:
        return FakeStreamResponse([{"response": "", "done": True}])

    monkeypatch.setattr("pic_local_llm_phase_experiment.ollama_client.requests.post", fake_post)
    client = OllamaClient("http://localhost:11434", generation_retries=1)

    with pytest.raises(OllamaError, match="empty text"):
        client.generate(
            model="qwen3.5:35b-a3b",
            prompt="Prompt",
            temperature=0,
            top_p=1,
            seed=42,
            num_predict=32,
        )
