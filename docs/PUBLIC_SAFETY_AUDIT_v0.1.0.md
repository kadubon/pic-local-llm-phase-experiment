# Public Safety Audit v0.1.0

Audit date: 2026-06-14

## Scope

This audit covers the v0.1.0 public repository state. It is concerned with
release safety, distribution hygiene, and scientific claim discipline.

The audit does not certify that generated model output is safe for arbitrary
reuse. Generated artifacts remain ignored by git and should receive a separate
human review before publication.

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

## Manual Review

Manual review confirmed:

- The README begins with a beginner-facing explanation of PIC.
- The public report states that PIC is not an ASI detector or creator.
- The public report includes the negative result that one repair round did not
  reduce PIC missing obligations.
- `accepted`, `operationally_usable`, and `settled` are reported separately.
- The repo does not require cloud LLM APIs or API keys.
- The experiment does not execute LLM-generated commands.
- Generated raw model outputs remain ignored by git.
- Generated raw outputs remain ignored by git.
- PIC source is cloned into an ignored local directory and is not vendored.

## Release Verification Commands

The following commands are expected to pass before publishing v0.1.0:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/setup_pic.py
uv run python scripts/smoke_check.py
uv run python scripts/public_safety_audit.py
```

The completed full experiment used:

```bash
uv run python scripts/run_experiment.py --config configs/experiment.default.yaml
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

## Known Residual Risks

- The generated local artifacts are not published in this release.
- If raw artifacts are later published, they need separate review for model
  output content, local metadata, and licensing.
- Results depend on a specific local model, PIC commit, prompt design, task set,
  and machine runtime state.
- PIC behavior may change in future upstream commits.
- The current experiment has no human expert grading layer.
- The current experiment has no external task execution or real-world tool-use
  validation.

## Audit Result

v0.1.0 is suitable for public source release as a local-only, diagnostic research
repo if the verification commands pass at release time. The release should be
described as experimental and protocol-relative, not as evidence of real ASI or
external-world capability.
