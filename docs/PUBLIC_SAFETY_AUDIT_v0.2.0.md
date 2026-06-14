# Public Safety Audit v0.2.0

Audit date: 2026-06-14

## Scope

This audit covers the v0.2.0 shared-initial repository state after the completed
local run `20260614-050311`. It focuses on release safety, distribution hygiene,
and scientific claim discipline.

v0.2.0 publishes a tracked aggregate report, not raw generated artifacts.
Generated model outputs and raw PIC reports remain ignored by git and require
separate human review before any publication.

## Public Boundary

The public release includes source code, task fixtures, configs, tests, README,
license, changelog, release notes, and tracked docs.

The public release intentionally excludes:

- `external/`
- `results/`
- `reports/`
- local virtual environments
- local caches
- large model files
- generated raw LLM outputs
- generated PIC reports

Only `.gitkeep` placeholders are allowed under ignored artifact directories.

## Automated Checks

The release safety audit checks that public files do not contain:

- local absolute path fragments
- local sync-directory fragments
- cloud LLM key environment variable names
- cloud LLM endpoint references
- obvious secret-token fragments
- tracked generated artifacts under ignored runtime directories
- version drift between package metadata and release version

The audit command is:

```bash
uv run python scripts/public_safety_audit.py
```

The default audit version is `0.2.0`.

## Manual Review Checklist

Manual review should confirm:

- The README begins with a beginner-facing explanation of PIC.
- The README explains `separate_initial` and `shared_initial`.
- The v0.2.0 report document is marked `Status: completed run`.
- The v0.2.0 report contains aggregate metrics and task identifiers, not raw
  model output.
- The v0.2.0 template remains available for future reruns and contains no
  fabricated result table.
- The v0.1.0 report remains available as a historical record.
- `accepted`, `operationally_usable`, and `settled` remain separate.
- The v0.2.0 report states that no repaired output was operationally usable or
  settled in the run.
- The repo does not require cloud LLM APIs or API keys.
- The experiment does not execute LLM-generated commands.
- Generated raw model outputs remain ignored by git.
- PIC source is cloned into an ignored local directory and is not vendored.

## Release Verification Commands

The following commands are expected to pass before publishing v0.2.0:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/public_safety_audit.py
```

Optional local readiness checks before a v0.2.0 rerun:

```bash
uv sync
uv run python scripts/setup_pic.py
uv run python scripts/smoke_check.py --config configs/experiment.shared_initial.yaml
```

The full shared-initial rerun remains operator-triggered:

```bash
uv run python scripts/run_experiment.py --config configs/experiment.shared_initial.yaml
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

## Known Residual Risks

- If raw artifacts are later published, they need separate review for model
  output content, local metadata, and licensing.
- Results depend on a specific local model, PIC commit, prompt design, task
  set, and machine runtime state.
- PIC behavior may change in future upstream commits.
- The experiment still has no human expert grading layer.
- The experiment still has no external task execution or real-world tool-use
  validation.

## Audit Result

v0.2.0 is suitable for public source release as a local-only shared-initial
diagnostic research repo if the verification commands pass. The release should
be described as experimental and protocol-relative, with a negative
repair-effectiveness result for this run, not as evidence of real ASI or
external-world capability.
