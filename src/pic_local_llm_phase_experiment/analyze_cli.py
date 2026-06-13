from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from pic_local_llm_phase_experiment.paths import read_json, resolve_run, write_json


def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}{key}" if not prefix else f"{prefix}_{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(value, full_key))
        else:
            flattened[full_key] = value
    return flattened


def collect_metrics(run_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metrics_path in sorted(run_dir.glob("task_*/metrics.json")):
        metrics = read_json(metrics_path)
        row = _flatten(metrics)
        row["run_id"] = run_dir.name
        rows.append(row)
    if not rows:
        raise FileNotFoundError(f"No per-task metrics found under {run_dir.as_posix()}")
    return rows


def write_summary(root: Path, rows: list[dict[str, Any]]) -> None:
    results_dir = root / "results"
    write_json(results_dir / "summary.json", rows)
    fieldnames = sorted({key for row in rows for key in row})
    csv_path = results_dir / "summary.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def analyze_run(*, root: Path, run: str) -> list[dict[str, Any]]:
    run_dir = resolve_run(root, run)
    rows = collect_metrics(run_dir)
    write_summary(root, rows)
    write_json(run_dir / "summary.json", rows)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze PIC local LLM experiment results.")
    parser.add_argument("--run", default="latest", help="Run id, run directory, or 'latest'.")
    args = parser.parse_args(argv)

    root = Path.cwd()
    rows = analyze_run(root=root, run=args.run)
    print(f"Wrote summary for {len(rows)} task(s) to results/summary.csv and results/summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
