from __future__ import annotations

from typing import Any

import requests

from pic_local_llm_phase_experiment.schemas import OllamaGeneration


class OllamaError(RuntimeError):
    """Raised when local Ollama cannot satisfy a generation request."""


class OllamaClient:
    def __init__(self, base_url: str, timeout_seconds: int = 180) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def list_models(self) -> list[str]:
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url, timeout=min(self.timeout_seconds, 30))
            response.raise_for_status()
        except requests.RequestException as exc:
            raise OllamaError(
                "Could not reach local Ollama. Start Ollama, then run `ollama list`. "
                "If the target model is missing, run `ollama pull qwen3.5:35b-a3b`."
            ) from exc

        data = response.json()
        models = data.get("models", [])
        names: list[str] = []
        for model in models:
            name = model.get("name")
            if isinstance(name, str):
                names.append(name)
        return names

    def ensure_model_available(self, model: str) -> None:
        names = self.list_models()
        if ":" in model:
            found = model in names
        else:
            base_names = {name.split(":", maxsplit=1)[0] for name in names}
            found = model in names or model in base_names

        if not found:
            raise OllamaError(
                f"Ollama model `{model}` was not found. Run `ollama list` to inspect "
                f"installed models, then run `ollama pull {model}` if appropriate. "
                "The experiment will not silently switch models."
            )

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float,
        top_p: float,
        seed: int | None,
        num_predict: int,
    ) -> OllamaGeneration:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": num_predict,
            },
        }
        if seed is not None:
            payload["options"]["seed"] = seed

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise OllamaError(
                "Local Ollama generation failed before receiving a response. "
                "Check that Ollama is running and that `ollama list` includes the "
                f"requested model `{model}`."
            ) from exc

        if response.status_code >= 400:
            raise OllamaError(
                f"Local Ollama returned HTTP {response.status_code}: {response.text}\n"
                f"Run `ollama list`, and run `ollama pull {model}` if the model is missing."
            )

        data = response.json()
        text = data.get("response")
        if not isinstance(text, str):
            raise OllamaError("Local Ollama response did not include a text `response` field.")
        return OllamaGeneration(text=text, raw=data)
