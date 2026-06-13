from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative_posix(path: Path, start: Path) -> str:
    try:
        return path.resolve().relative_to(start.resolve()).as_posix()
    except ValueError:
        return path.name


def latest_run(runs_dir: Path) -> Path:
    candidates = [path for path in runs_dir.glob("*") if path.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No run directories found under {runs_dir.as_posix()}")
    return max(candidates, key=lambda path: path.name)


def resolve_run(root: Path, run: str) -> Path:
    runs_dir = root / "results" / "runs"
    if run == "latest":
        return latest_run(runs_dir)

    candidate = Path(run)
    if candidate.is_absolute() and candidate.exists():
        return candidate

    by_id = runs_dir / run
    if by_id.exists():
        return by_id

    if candidate.exists():
        return candidate

    raise FileNotFoundError(f"Run not found: {run}")
