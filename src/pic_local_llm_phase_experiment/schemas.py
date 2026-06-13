from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = "qwen3.5:35b-a3b"
    ollama_url: str = "http://localhost:11434"
    temperature: float = 0
    top_p: float = 1
    seed: int | None = 42
    num_predict: int = 2048
    max_tasks: int = 10
    repair_rounds: int = 1
    pic_profile: str = "development"
    output_dir: Path = Path("results/runs")
    timeout_seconds: int = 180

    @field_validator("output_dir", mode="before")
    @classmethod
    def _coerce_output_dir(cls, value: str | Path) -> Path:
        return Path(value)

    @field_validator("ollama_url")
    @classmethod
    def _local_ollama_only(cls, value: str) -> str:
        normalized = value.rstrip("/")
        allowed = (
            normalized.startswith("http://localhost:"),
            normalized.startswith("http://127.0.0.1:"),
            normalized.startswith("http://[::1]:"),
        )
        if not any(allowed):
            raise ValueError("ollama_url must point to a local Ollama endpoint")
        return normalized


class TaskSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    title: str
    prompt: str
    expected_obligation_types: list[str] = Field(default_factory=list)
    notes: str = ""


class OllamaGeneration(BaseModel):
    text: str
    raw: dict[str, Any] = Field(default_factory=dict)


class PICReportSummary(BaseModel):
    accepted: bool = False
    settled: bool = False
    residual_summary: str = ""
    missing_obligations: list[str] = Field(default_factory=list)
    missing_obligation_count: int = 0
    runtime_report: dict[str, Any] = Field(default_factory=dict)
    raw_report_path: str = ""
    command_failed: bool = False
    error_message: str | None = None


class TaskRunMetrics(BaseModel):
    task_id: str
    title: str
    baseline: dict[str, Any] = Field(default_factory=dict)
    pic: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
