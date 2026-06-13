from __future__ import annotations

import argparse
from pathlib import Path

from pic_local_llm_phase_experiment.analyze_cli import collect_metrics, write_summary
from pic_local_llm_phase_experiment.paths import read_json, resolve_run, write_text
from pic_local_llm_phase_experiment.report import render_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Markdown experiment report.")
    parser.add_argument("--run", default="latest", help="Run id, run directory, or 'latest'.")
    parser.add_argument("--output", default="reports/experiment_report.md")
    args = parser.parse_args(argv)

    root = Path.cwd()
    run_dir = resolve_run(root, args.run)
    rows = collect_metrics(run_dir)
    write_summary(root, rows)

    manifest_path = run_dir / "run_manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {}
    setup_manifest_path = root / "results" / "setup_manifest.json"
    setup_manifest = read_json(setup_manifest_path) if setup_manifest_path.exists() else {}

    report = render_report(rows=rows, manifest=manifest, setup_manifest=setup_manifest)
    write_text(root / args.output, report)
    print(f"Wrote Markdown report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
