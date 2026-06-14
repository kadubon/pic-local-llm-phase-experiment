from __future__ import annotations

import json
from typing import Any

import requests

from pic_local_llm_phase_experiment.schemas import OllamaGeneration


class OllamaError(RuntimeError):
    """Raised when local Ollama cannot satisfy a generation request."""


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: int = 180,
        generation_retries: int = 1,
        disable_thinking: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.generation_retries = max(0, generation_retries)
        self.disable_thinking = disable_thinking

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
        errors: list[str] = []
        for attempt in range(self.generation_retries + 1):
            try:
                generation = self._generate_once(
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                    top_p=top_p,
                    seed=seed,
                    num_predict=num_predict,
                )
            except OllamaError as exc:
                errors.append(str(exc))
                if attempt >= self.generation_retries:
                    raise OllamaError(
                        "Local Ollama generation failed after "
                        f"{attempt + 1} attempt(s): {' | '.join(errors)}"
                    ) from exc
                continue

            if generation.text.strip():
                generation.raw["attempt_count"] = attempt + 1
                generation.raw["empty_retry_count"] = attempt
                return generation

            errors.append("Ollama returned an empty text response.")

        raise OllamaError(
            f"Local Ollama returned empty text after {self.generation_retries + 1} attempt(s)."
        )

    def _generate_once(
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
            "stream": True,
            "think": not self.disable_thinking,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": num_predict,
            },
        }
        if seed is not None:
            payload["options"]["seed"] = seed

        try:
            with requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=(30, self.timeout_seconds),
            ) as response:
                if response.status_code >= 400:
                    raise OllamaError(
                        f"Local Ollama returned HTTP {response.status_code}: {response.text}\n"
                        f"Run `ollama list`, and run `ollama pull {model}` if the model is "
                        "missing."
                    )

                chunks: list[str] = []
                final_event: dict[str, Any] = {}
                event_count = 0
                for raw_line in response.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    event_count += 1
                    try:
                        event = json.loads(raw_line)
                    except json.JSONDecodeError as exc:
                        raise OllamaError(
                            f"Local Ollama returned a malformed streaming JSON line: {raw_line}"
                        ) from exc
                    if isinstance(event.get("error"), str):
                        raise OllamaError(f"Local Ollama returned an error: {event['error']}")
                    piece = event.get("response")
                    if isinstance(piece, str):
                        chunks.append(piece)
                    if event.get("done") is True:
                        final_event = event
                        break
        except requests.RequestException as exc:
            raise OllamaError(
                "Local Ollama generation failed before receiving a response. "
                "Check that Ollama is running and that `ollama list` includes the "
                f"requested model `{model}`."
            ) from exc

        text = "".join(chunks)
        final_event["stream_event_count"] = event_count
        final_event["streamed"] = True
        return OllamaGeneration(text=text, raw=final_event)
