# Release v0.2.0

Release date: 2026-06-14

v0.2.0 adds and reports a shared-initial PIC plus local Ollama experiment. The
shared-initial design starts the baseline and PIC-assisted branches from the
exact same initial local LLM answer for each task.

The completed public run is documented in:

```bash
docs/EXPERIMENT_REPORT_v0.2.0.md
```

## Main Change

v0.2.0 adds `experiment_mode: shared_initial`.

In shared-initial mode, each task starts with one local LLM initial answer. The
baseline branch and PIC-assisted branch both receive that exact same initial
answer. This improves the experimental design by reducing comparison noise from
two different initial generations.

The previous v0.1.0 behavior remains available as `experiment_mode:
separate_initial`.

## New Config

Use this config for the v0.2.0 experiment:

```bash
configs/experiment.shared_initial.yaml
```

Expected workload with the default 10 tasks and one repair round:

- `40` local Ollama generations
- `20` PIC intake calls

The historical default config remains:

```bash
configs/experiment.default.yaml
```

That config preserves the v0.1.0-compatible separate-initial flow and estimates
`50` local Ollama generations with `20` PIC intake calls.

## Results

Reference run: `20260614-050311`

- Experiment mode: `shared_initial`
- Tasks completed: `10 / 10`
- Shared-initial artifact equality: `10 / 10`
- Task errors: none
- Average baseline heuristic obligation coverage: `0.960`
- Average PIC-assisted heuristic obligation coverage: `0.980`
- Average obligation coverage delta: `0.020`
- Average PIC missing-obligation delta: `-0.200`
- Average PIC residual charge delta: `-0.574`
- PIC accepted-after ratio: `1.000`
- PIC operationally-usable-after ratio: `0.000`
- PIC settled-after ratio: `0.000`
- PIC schema-field usable ratio: `1.000`
- Average local phase score: `0.645`

Scientific interpretation:

- PIC produced parseable runtime/schema fields on all tasks.
- PIC exposed residual summaries and residual charge totals on all tasks.
- One PIC-guided repair round did not reduce missing obligations on average.
- One PIC-guided repair round did not reduce residual charge on average.
- No repaired output was marked operationally usable or settled by PIC.
- The small average coverage gain came from one task and should be treated as a
  heuristic signal, not as a broad quality or capability result.

## Artifact Changes

In `shared_initial` mode, each task directory includes:

- `shared_initial_answer.txt`
- `baseline_initial.txt`
- `pic_initial_candidate.txt`

For a valid shared-initial task run, these three files begin from the same
initial answer text. The baseline branch then performs self-review and final
revision; the PIC-assisted branch performs PIC intake, one residual-preserving
repair, and a second PIC intake.

## Metrics

v0.2.0 adds top-level metrics for easier analysis:

- `experiment_mode`
- `shared_initial_answer_used`
- `shared_initial_answer_length`
- `baseline_final_length`
- `pic_repaired_output_length`
- `baseline_obligation_coverage`
- `pic_obligation_coverage`
- `obligation_coverage_delta`
- `pic_missing_obligation_count_before`
- `pic_missing_obligation_count_after`
- `pic_missing_obligation_delta`
- `pic_residual_charge_delta`
- `pic_accepted_after`
- `pic_operationally_usable_after`
- `pic_settled_after`
- `pic_schema_fields_usable`
- `local_phase_score`

Nested v0.1.0-style `baseline` and `pic` metric dictionaries remain present for
compatibility.

Sign convention: `pic_missing_obligation_delta = before - after`. A positive
value means fewer missing obligations after repair.

## Reporting And Documentation

Added:

- `docs/EXPERIMENT_REPORT_v0.2.0.md`
- `docs/EXPERIMENT_REPORT_v0.2.0_TEMPLATE.md`
- `docs/PUBLIC_SAFETY_AUDIT_v0.2.0.md`
- this release note

Updated:

- README shared-initial instructions
- reproducibility guidance
- public safety audit default version
- changelog
- tests for shared-initial behavior

The v0.1.0 report remains unchanged as a historical record.

## Scientific Boundary

v0.2.0 does not claim:

- PIC creates ASI
- PIC proves real ASI or real-world phase formation
- the local LLM becomes superintelligent
- local text quality proves external adoption or autonomous agent society
  formation
- `accepted` means `settled`
- heuristic metric deltas prove truth, intelligence, or external-world
  capability

All conclusions from the v0.2.0 run must remain local, small-sample,
model-dependent, protocol-relative, and tied to observed metrics.

## Suggested Verification

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/public_safety_audit.py
```

Optional local readiness checks before a rerun:

```bash
uv sync
uv run python scripts/setup_pic.py
uv run python scripts/smoke_check.py --config configs/experiment.shared_initial.yaml
```

Canonical full v0.2.0 rerun, when intentionally started by the operator:

```bash
uv run python scripts/run_experiment.py --config configs/experiment.shared_initial.yaml
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

Generated raw outputs, PIC reports, summaries, and rendered reports remain
ignored by git unless separately reviewed and intentionally promoted into
tracked documentation.
