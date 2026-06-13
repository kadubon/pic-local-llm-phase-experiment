from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from pic_local_llm_phase_experiment.schemas import ExperimentConfig, TaskSpec


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping in {path.as_posix()}")
    return data


def load_config(path: Path) -> ExperimentConfig:
    return ExperimentConfig.model_validate(_load_yaml(path))


def load_task(path: Path) -> TaskSpec:
    return TaskSpec.model_validate(_load_yaml(path))


def load_tasks(tasks_dir: Path, max_tasks: int | None = None) -> list[TaskSpec]:
    paths = sorted(tasks_dir.glob("task_*.yaml"))
    if not paths:
        raise FileNotFoundError(f"No task YAML files found under {tasks_dir.as_posix()}")
    tasks = [load_task(path) for path in paths]
    if max_tasks is not None:
        return tasks[:max_tasks]
    return tasks
