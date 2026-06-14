# Release v0.1.0

Release date: 2026-06-14

## Summary

v0.1.0 is the first public-ready release of the PIC Local LLM Phase Experiment.
It provides a local-only research pipeline for comparing a baseline local LLM
self-review loop against a PIC-assisted residual-preserving repair loop.

This release is experimental. It does not claim real ASI, truth, external-world
capability, autonomous superintelligence, or settlement of protocol obligations.

## Public Report

Read the tracked public report:

- `docs/EXPERIMENT_REPORT_v0.1.0.md`

The key empirical result is cautious and partly negative:

- PIC exposed residual summaries and runtime diagnostic fields for every task.
- PIC accepted all repaired outputs under the finite checker path.
- PIC did not mark any repaired output as operationally usable.
- PIC did not mark any repaired output as settled.
- One repair round did not reduce missing obligations on average.

## Reproducibility

Run:

```bash
uv sync
uv run python scripts/setup_pic.py
uv run python scripts/smoke_check.py
uv run python scripts/run_experiment.py --config configs/experiment.default.yaml
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

The release reference run used:

- Model: `qwen3.5:35b-a3b`
- PIC commit: `fa5ca5ddafc104effa7116559e2d8a46acd57cdd`
- Run id: `20260614-004542`
- Task count: `10`
- Local Ollama generations: `50`
- PIC intakes: `20`

## Verification

Before publishing, run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/setup_pic.py
uv run python scripts/smoke_check.py
uv run python scripts/public_safety_audit.py
```

## Public Safety Boundary

- Local Ollama only.
- No cloud LLM APIs.
- No API keys.
- No web browsing during experiment runs.
- No arbitrary shell execution from LLM output.
- PIC is cloned and installed into an ignored local directory during setup.
- Generated raw outputs and PIC reports are ignored by git.

## Known Limitations

- One model only.
- Ten synthetic tasks only.
- One repair round only.
- Heuristic metrics only.
- No human expert grading layer.
- No external task execution.
- No real-world tool-use validation.
- PIC behavior is tied to the referenced upstream commit and profile.

## Release Checklist

- [x] Version set to `0.1.0`.
- [x] Public report added under `docs/`.
- [x] Reproducibility docs added.
- [x] Changelog added.
- [x] Safety audit docs added.
- [x] Generated artifacts remain ignored.
- [x] Scientific non-claims preserved.
