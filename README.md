# PIC Local LLM Phase Experiment

This repository is a reproducible local experiment for testing whether the
Percolation Inversion Compiler (PIC) improves finite, protocol-relative workflow
indicators in local LLM loops.

It compares two conditions on a fixed synthetic task set:

1. **Baseline LLM-only loop**: local LLM answer, one self-review, final answer.
2. **PIC-assisted loop**: local LLM answer, PIC `agent intake`, residual and
   missing-obligation feedback, one repair attempt, PIC `agent intake` again.

The default local model is:

```text
qwen3.5:35b-a3b
```

## What This Tests

The experiment measures local workflow diagnostics such as:

- missing-obligation counts before and after repair
- residual summary availability
- PIC accepted/settled flags
- heuristic obligation coverage
- whether unresolved assumptions and obligations are preserved
- whether repaired candidates look reusable for downstream review
- a bounded `local_phase_score`

The `local_phase_score` is a local workflow diagnostic, not a measure of real
ASI.

## What This Does Not Test

This repository does **not** test or claim:

- real ASI
- autonomous superintelligence
- real-world capability acceleration
- truth, oracle quality, or physical outcomes
- external adoption or autonomous agent society formation
- that PIC proves intelligence

All results are local, small-sample, model-dependent, protocol-relative, and
heuristic unless a later human evaluation layer is added.

## Requirements

- Python >= 3.11
- `uv`
- `git`
- Ollama running locally
- Ollama model `qwen3.5:35b-a3b`

Check the model with:

```bash
ollama list
```

If it is not present, pull it explicitly:

```bash
ollama pull qwen3.5:35b-a3b
```

The code never silently switches to another model. To use a different model for
a separate run, pass an explicit CLI flag.

## Setup

Install dependencies:

```bash
uv sync
```

Clone and install PIC into an ignored local `external/` directory:

```bash
uv run python scripts/setup_pic.py
```

The setup script:

- creates `external/`
- clones `https://github.com/kadubon/percolation-inversion-compiler` if missing
- leaves an existing checkout untouched and prints its current commit
- installs PIC in editable mode with `uv pip install -e`
- verifies `pic --help`
- attempts `pic agent explain` when available
- writes `results/setup_manifest.json`

PIC source is not vendored into this repository.

## Run

Run the experiment:

```bash
uv run python scripts/run_experiment.py --config configs/experiment.default.yaml
```

Analyze the latest run:

```bash
uv run python scripts/analyze_results.py --run latest
```

Generate the Markdown report:

```bash
uv run python scripts/generate_report.py --run latest
```

Equivalent console scripts are also installed:

```bash
uv run pic-phase-setup
uv run pic-phase-run --config configs/experiment.default.yaml
uv run pic-phase-analyze --run latest
uv run pic-phase-report --run latest
```

## Outputs

The experiment creates timestamped run directories:

```text
results/runs/YYYYMMDD-HHMMSS/
```

Each task directory stores:

- `task.yaml`
- `baseline_initial.txt`
- `baseline_self_review.txt`
- `baseline_final.txt`
- `pic_initial_candidate.txt`
- `pic_initial_report.json`
- `pic_repair_prompt.txt`
- `pic_repaired_output.txt`
- `pic_repaired_report.json`
- `metrics.json`

Summary outputs:

- `results/summary.csv`
- `results/summary.json`
- `results/run_manifest.json`
- `reports/experiment_report.md`

Generated results are ignored by git by default.

## Safety Boundary

This repository is local-only by default:

- no cloud LLM APIs
- no API keys or secrets
- no web browsing during experiments
- no arbitrary shell command execution from LLM output
- no automatic PR comments
- no autonomous external actions
- no mutation of external repositories beyond cloning/installing PIC during setup

Subprocess usage is limited to controlled calls for:

- `git clone` during setup
- `uv pip install -e` during setup
- `pic agent intake` during experiment runs

LLM-generated text is written to files and reviewed; it is never executed.

## Interpreting Results

The report may cautiously state that PIC-assisted loops improved residual
visibility or missing-obligation preservation if the recorded metrics support
that statement.

The report must not state that PIC creates ASI, proves ASI phase formation,
makes a local LLM superintelligent, or proves any external-world capability.

## Development Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Tests use fixtures and mocks. They do not require Ollama or the real PIC repo.
