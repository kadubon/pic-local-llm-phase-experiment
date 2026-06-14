# PIC Local LLM Phase Experiment

This repository is an English-first, local-only research scaffold for testing
whether the Percolation Inversion Compiler (PIC) improves finite workflow
diagnostics in local LLM loops.

It does not test real ASI. It does not claim external-world capability
acceleration. It asks a narrower and reproducible question:

> When a local LLM answer is checked by PIC and repaired using PIC's residuals
> and missing obligations, do local workflow indicators improve compared with a
> baseline local LLM self-review loop?

## What Is PIC?

PIC, short for Percolation Inversion Compiler, is a finite
certificate/verifier-routing and residual-ledger runtime for protocol-relative
ASI-proxy research. In practical terms, PIC helps an engineer or agent inspect
candidate outputs and produce deterministic JSON about:

- which finite checks were accepted
- which obligations remain missing
- which residual ledger coordinates must stay visible
- which verifier routes or next actions should be considered
- whether a result is merely accepted, operationally usable, or settled under a
  declared protocol

PIC is not an ASI detector, ASI creator, truth oracle, model self-rewrite system,
or permission system for autonomous external actions. Its safety discipline is
fail-closed: unresolved obligations stay explicit instead of being silently
promoted to `settled`.

Useful upstream references:

- [PIC repository](https://github.com/kadubon/percolation-inversion-compiler)
- [PIC overview](https://raw.githubusercontent.com/kadubon/percolation-inversion-compiler/refs/heads/main/docs/00-overview.md)
- [PIC agent integration](https://raw.githubusercontent.com/kadubon/percolation-inversion-compiler/refs/heads/main/docs/agent-integration.md)
- [PIC safety boundary](https://raw.githubusercontent.com/kadubon/percolation-inversion-compiler/refs/heads/main/docs/11-safety-boundary.md)
- [PIC CLI reference](https://raw.githubusercontent.com/kadubon/percolation-inversion-compiler/main/docs/cli-reference.md)

## What This Repository Does

This repository runs a small, synthetic, local experiment over ten review-style
tasks. It compares two conditions:

1. **Baseline LLM-only loop**
   - ask the local LLM to answer a task
   - ask the same local LLM to self-review once
   - ask it to produce a final answer

2. **PIC-assisted loop**
   - ask the local LLM to answer the same task
   - run `pic agent intake` on the candidate answer
   - parse `accepted`, `operationally_usable`, `settled`,
     `runtime_report.missing_obligations`, residual ledger data, and
     `residual_summary`
   - feed those residuals and obligations back to the local LLM
   - ask for a repair attempt
   - run `pic agent intake` again

The repository supports two initial-answer modes:

- `separate_initial`: the v0.1.0-compatible design. Baseline and PIC-assisted
  branches each receive their own initial local LLM generation.
- `shared_initial`: the v0.2.0 design. Baseline and PIC-assisted branches start
  from the exact same initial local LLM answer for each task.

The shared-initial mode reduces one source of comparison noise: the branches no
longer differ merely because the model produced two different initial answers.
It does not make the result stronger than the recorded metrics allow.

Use `configs/experiment.default.yaml` for the historical separate-initial mode.
Use `configs/experiment.shared_initial.yaml` for the v0.2.0 shared-initial
experiment.

The default local model is:

```text
qwen3.5:35b-a3b
```

The default Ollama endpoint is:

```text
http://localhost:11434
```

The code never silently switches models. If you choose a different model, pass it
explicitly with a CLI flag.

The default full-run generation settings are intentionally conservative for a
large local model:

```text
num_predict: 1024
timeout_seconds: 1800
generation_retries: 1
disable_ollama_thinking: true
abort_on_generation_error: true
```

Ollama generation uses streaming responses. Empty generations are retried once.
If a generation is still empty or fails after retry, the experiment stops instead
of continuing with empty files or synthetic success. Thinking output is disabled
for Ollama requests so the experiment records answer text, not hidden reasoning
streams.

## What This Measures

The experiment measures local, finite, protocol-relative workflow indicators:

- missing-obligation counts before and after repair
- residual summary presence and residual charge totals
- PIC `accepted`, `operationally_usable`, and `settled` flags
- route request and agent task counts emitted by PIC
- whether unresolved assumptions and obligations remain visible
- heuristic expected-obligation coverage for each synthetic task
- candidate reuse markers such as evidence, tests, risks, and next steps
- a bounded `local_phase_score`

`local_phase_score` is a local workflow diagnostic. It is not a measure of real
ASI, intelligence, truth, or external-world capability.

## What This Does Not Claim

This repository does not claim:

- PIC creates ASI
- PIC proves real ASI or real-world phase formation
- the local LLM becomes superintelligent
- local text quality proves external adoption or autonomous agent society
  formation
- `accepted` means `settled`
- self-declared LLM text is evidence for physical, oracle, simulator, or policy
  outcomes

All conclusions must remain local, small-sample, model-dependent,
protocol-relative, and heuristic unless a later human expert evaluation layer is
added.

## How To Read The Report

Generated reports are written to:

```text
reports/experiment_report.md
```

The tracked public v0.1.0 report is:

```text
docs/EXPERIMENT_REPORT_v0.1.0.md
```

The tracked public v0.2.0 shared-initial report is:

```text
docs/EXPERIMENT_REPORT_v0.2.0.md
```

Release and audit documents:

- `RELEASE_v0.1.0.md`
- `RELEASE_v0.2.0.md`
- `CHANGELOG.md`
- `docs/PUBLIC_SAFETY_AUDIT_v0.1.0.md`
- `docs/PUBLIC_SAFETY_AUDIT_v0.2.0.md`
- `docs/REPRODUCIBILITY.md`

The reusable v0.2.0 report template remains available for future reruns:

```text
docs/EXPERIMENT_REPORT_v0.2.0_TEMPLATE.md
```

Key terms:

- `accepted`: PIC accepted the finite checker path for the current report shape.
  It is not a global approval.
- `operationally_usable`: PIC indicates the result may be useful for routing
  under the current protocol. It can still have unresolved obligations.
- `settled`: scoped finite obligations were discharged. This is stricter than
  `accepted`, and in many diagnostic runs it is expected to remain false.
- `missing_obligations`: obligations PIC says remain unresolved.
- `residual_summary`: PIC's residual ledger summary, often a dictionary of
  residual coordinate names and numeric charges.
- `local_phase_score`: this repo's bounded heuristic summary of local workflow
  observables. It is not a PIC theorem and not a real ASI metric.

The report may cautiously say that PIC-assisted loops improved residual
visibility or missing-obligation handling if the recorded metrics support that
claim. It must not say that PIC proves ASI, truth, physical outcomes, or
external-world capability.

## Requirements

- Python >= 3.11
- `uv`
- `git`
- Ollama running locally
- Ollama model `qwen3.5:35b-a3b`

Check the local model:

```bash
ollama list
```

Pull it if needed:

```bash
ollama pull qwen3.5:35b-a3b
```

## Setup

Install this repository's dependencies:

```bash
uv sync
```

Clone and install PIC into the ignored local `external/` directory:

```bash
uv run python scripts/setup_pic.py
```

The setup script:

- creates `external/`
- clones `https://github.com/kadubon/percolation-inversion-compiler` if missing
- leaves an existing checkout untouched and prints its current commit
- installs PIC in editable mode with `uv pip install -e`
- verifies `pic --help`
- attempts `pic agent explain`
- writes `results/setup_manifest.json`

PIC source is not vendored into this repository.

## Smoke Check

Run the lightweight readiness check before the full experiment:

```bash
uv run python scripts/smoke_check.py
```

The smoke check verifies:

- this package imports in the `uv` environment
- local Ollama can see the exact model `qwen3.5:35b-a3b`
- a short local Ollama streaming generation returns non-empty text
- the default experiment config loads
- the configured task set is present
- `results/setup_manifest.json` shows a successful local PIC setup
- `pic --help` works
- `pic agent explain` works
- `pic agent intake --text ... --profile development --output ...` writes
  parseable JSON
- report generation works from smoke metrics
- the default full run size is estimated before you start it

Smoke outputs are ignored by git:

```text
results/smoke/
reports/smoke_experiment_report.md
```

## v0.2.0 Shared-Initial Experiment

The v0.2.0 experiment should use:

```text
configs/experiment.shared_initial.yaml
```

In this mode, each task creates one initial local LLM answer and reuses it for
both branches:

- `shared_initial_answer.txt`: the one initial answer generated for the task
- `baseline_initial.txt`: an identical copy used by the baseline self-review
  branch
- `pic_initial_candidate.txt`: the same text passed to `pic agent intake`

The baseline branch then performs self-review and final revision. The
PIC-assisted branch runs PIC intake on the same initial text, feeds PIC residuals
and missing obligations into one repair prompt, and runs PIC intake again.

With 10 tasks and one repair round, this mode estimates:

```text
40 local Ollama generations
20 PIC intake calls
```

The completed public v0.2.0 run, `20260614-050311`, found:

- shared-initial artifact equality: `10 / 10` tasks
- average baseline heuristic obligation coverage: `0.960`
- average PIC-assisted heuristic obligation coverage: `0.980`
- average PIC missing-obligation delta: `-0.200`
- average PIC residual charge delta: `-0.574`
- PIC accepted-after ratio: `1.000`
- PIC operationally-usable-after ratio: `0.000`
- PIC settled-after ratio: `0.000`

The cautious interpretation is that PIC improved diagnostic visibility, but one
PIC-assisted repair round did not improve missing-obligation count, residual
charge, operational usability, or settlement in this run.

The older `configs/experiment.default.yaml` remains valid and preserves the
v0.1.0-compatible `separate_initial` design:

```text
50 local Ollama generations
20 PIC intake calls
```

## Before The Full Run

Use this checklist before starting the 10-task run:

- `uv sync` completed successfully
- Ollama is running on `http://localhost:11434`
- `ollama list` shows the exact model `qwen3.5:35b-a3b`
- `uv run python scripts/setup_pic.py` completed with `status: ok`
- `uv run python scripts/smoke_check.py` passed
- you have enough time for the local model to complete the run

With the default v0.1.0-compatible config, the full experiment runs 10 tasks.
Each task uses three baseline local generations, one PIC candidate generation,
one PIC repair generation, and two PIC intake calls. That is about:

```text
50 local Ollama generations
20 PIC intake calls
```

With the v0.2.0 shared-initial config, the full experiment runs 10 tasks. Each
task uses one shared initial generation, two baseline local generations, one PIC
repair generation, and two PIC intake calls. That is about:

```text
40 local Ollama generations
20 PIC intake calls
```

`run_experiment.py` repeats the important preflight checks before starting. If
Ollama, the short local generation check, or PIC is missing, it exits before
spending the expensive local generations and prints the setup/smoke commands to
run. If a later generation fails or returns empty text even after retry, the run
stops and leaves partial artifacts under `results/runs/` for diagnosis.

## Run The Full Experiment

Canonical v0.2.0 shared-initial full sequence:

```powershell
uv sync
uv run python scripts/setup_pic.py
uv run python scripts/smoke_check.py
uv run python scripts/run_experiment.py --config configs/experiment.shared_initial.yaml
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

Historical v0.1.0-compatible sequence:

```powershell
uv run python scripts/run_experiment.py --config configs/experiment.default.yaml
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

Equivalent console scripts:

```bash
uv run pic-phase-setup
uv run pic-phase-smoke
uv run pic-phase-run --config configs/experiment.shared_initial.yaml
uv run pic-phase-analyze --run latest
uv run pic-phase-report --run latest
```

For a quick rehearsal that still uses the real local model and PIC, limit the
experiment to one task:

```powershell
uv run python scripts/run_experiment.py --config configs/experiment.shared_initial.yaml --max-tasks 1
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

## Outputs

Each full experiment creates:

```text
results/runs/YYYYMMDD-HHMMSS/
```

Per-task artifacts include:

- `task.yaml`
- `shared_initial_answer.txt`, in `shared_initial` mode
- `baseline_initial.txt`
- `baseline_self_review.txt`
- `baseline_final.txt`
- `pic_initial_candidate.txt`
- `pic_initial_report.json`
- `pic_repair_prompt.txt`
- `pic_repaired_output.txt`
- `pic_repaired_candidate_for_pic.txt`
- `pic_repaired_report.json`
- `metrics.json`

Summary artifacts include:

- `results/summary.csv`
- `results/summary.json`
- `results/run_manifest.json`, which points to the latest run manifest
- `results/runs/YYYYMMDD-HHMMSS/run_manifest.json`, which records the model,
  task IDs, PIC setup status, and estimated local generation/PIC intake counts
- `reports/experiment_report.md`

Generated results are ignored by git by default.

## Safety Boundary

This repository is local-only by default:

- no cloud LLM APIs
- no API keys or secrets
- no web browsing during experiment runs
- no arbitrary shell command execution from LLM output
- no automatic PR comments
- no autonomous external actions
- no mutation of external repositories beyond cloning/installing PIC during setup

Subprocess usage is limited to controlled calls for:

- `git clone` during setup
- `uv pip install -e` during setup
- `pic agent intake` during experiment and smoke runs

LLM-generated text is written to files and reviewed; it is never executed.

## Development Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/public_safety_audit.py
```

Tests use fixtures and mocks. They do not require Ollama or the real PIC repo.
The public audit can also be run with `uv run pic-phase-public-audit`.
