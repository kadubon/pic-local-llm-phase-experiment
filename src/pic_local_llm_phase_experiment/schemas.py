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
    generation_retries: int = 1
    disable_ollama_thinking: bool = True
    abort_on_generation_error: bool = True

    @field_validator("output_dir", mode="before")
    @classmethod
    def _coerce_output_dir(cls, value: str | Path) -> Path:
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("output_dir must be a relative path under the project")
        return path

    @field_validator("max_tasks")
    @classmethod
    def _positive_max_tasks(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("max_tasks must be positive")
        return value

    @field_validator("repair_rounds")
    @classmethod
    def _supported_repair_rounds(cls, value: int) -> int:
        if value != 1:
            raise ValueError("this experiment currently supports exactly one repair round")
        return value

    @field_validator("timeout_seconds")
    @classmethod
    def _positive_timeout_seconds(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("timeout_seconds must be positive")
        return value

    @field_validator("generation_retries")
    @classmethod
    def _nonnegative_generation_retries(cls, value: int) -> int:
        if value < 0:
            raise ValueError("generation_retries must be nonnegative")
        return value

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
    operationally_usable: bool = False
    settled: bool = False
    reasons: list[str] = Field(default_factory=list)
    recommended_next_commands: list[str] = Field(default_factory=list)
    residual_summary: str = ""
    residual_summary_raw: dict[str, float] | str | None = None
    residual_summary_key_count: int = 0
    residual_charge_total: float = 0.0
    missing_obligations: list[str] = Field(default_factory=list)
    missing_obligation_count: int = 0
    runtime_report: dict[str, Any] = Field(default_factory=dict)
    runtime_report_present: bool = False
    route_execution_request_count: int = 0
    agent_task_count: int = 0
    raw_report_path: str = ""
    command_failed: bool = False
    error_message: str | None = None


class TaskRunMetrics(BaseModel):
    task_id: str
    title: str
    baseline: dict[str, Any] = Field(default_factory=dict)
    pic: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
