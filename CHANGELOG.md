# Changelog

## v0.2.0 - 2026-06-14

Shared-initial experiment release with a completed local v0.2.0 run.

### Added

- `experiment_mode` config field with `separate_initial` and `shared_initial`
  modes.
- `configs/experiment.shared_initial.yaml` for the v0.2.0 design.
- Shared-initial runner path where baseline and PIC-assisted branches start from
  the exact same local LLM initial answer.
- `shared_initial_answer.txt` artifact for shared-initial task runs.
- Mode-aware workload estimates:
  - `separate_initial`: `50` local Ollama generations and `20` PIC intake calls
    for the default 10-task run.
  - `shared_initial`: `40` local Ollama generations and `20` PIC intake calls
    for the default 10-task run.
- Top-level metrics for experiment mode, shared-initial usage, obligation
  coverage, PIC after flags, residual-charge delta, and local phase score.
- `docs/EXPERIMENT_REPORT_v0.2.0.md`, the public shared-initial result report.
- `docs/EXPERIMENT_REPORT_v0.2.0_TEMPLATE.md`, marked pending run.
- `docs/PUBLIC_SAFETY_AUDIT_v0.2.0.md`.
- `RELEASE_v0.2.0.md`.

### Changed

- Bumped package version to `0.2.0`.
- Updated report rendering to show experiment mode and explain why shared
  initial answers matter.
- Updated README and reproducibility docs for v0.2.0 shared-initial execution.
- Updated public safety audit default version to `0.2.0`.

### Compatibility

- `configs/experiment.default.yaml` remains valid and preserves v0.1.0 behavior
  through the schema default `experiment_mode: separate_initial`.
- Nested v0.1.0-style `baseline` and `pic` metrics remain present.
- `docs/EXPERIMENT_REPORT_v0.1.0.md` remains unchanged as the historical public
  report.

### Scientific Interpretation

Shared-initial branching worked as intended: all 10 tasks reused the exact same
initial answer in the baseline and PIC-assisted branches.

### Results

- Reference run: `20260614-050311`
- Tasks completed: `10 / 10`
- Task errors: none
- Shared-initial artifact equality: `10 / 10`
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

### Scientific Interpretation

PIC improved diagnostic visibility and produced parseable runtime/schema fields
on all tasks. One PIC-assisted repair round did not reduce missing obligations
on average, did not reduce residual charge on average, and did not produce any
operationally usable or settled PIC reports. The repository still makes no claim
that PIC creates ASI, proves real ASI, or demonstrates external-world
capability.

## v0.1.0 - 2026-06-14

Initial public research release.

### Added

- Local-only PIC plus Ollama experiment pipeline.
- Baseline local LLM self-review condition.
- PIC-assisted residual-preserving repair condition.
- PIC report parser for `accepted`, `operationally_usable`, `settled`,
  `runtime_report`, missing obligations, residual summaries, residual charge,
  route requests, and agent task counts.
- Scientific report generation with non-claims and threats to validity.
- Full-run preflight for Ollama, short local generation, PIC, task fixtures, and
  output directory writability.
- Streaming Ollama generation with thinking disabled, empty-response retry, and
  fail-fast behavior for unusable generation output.
- Smoke check covering imports, Ollama model availability, short generation,
  PIC help, PIC explain, PIC intake, and report generation.
- Public v0.1.0 report under `docs/`.
- Public safety audit script and audit documentation.

### Results

- Reference run: `20260614-004542`
- Tasks completed: `10 / 10`
- Task errors: none
- Average baseline heuristic obligation coverage: `0.960`
- Average PIC-assisted heuristic obligation coverage: `0.980`
- Average PIC missing-obligation delta: `-0.200`
- Average PIC residual charge delta: `-0.574`
- PIC accepted-after ratio: `1.000`
- PIC operationally-usable-after ratio: `0.000`
- PIC settled-after ratio: `0.000`
- PIC schema-field usable ratio: `1.000`

### Scientific Interpretation

PIC improved residual visibility and diagnostic traceability in the reference
run. One PIC-assisted repair round did not reduce missing obligations, did not
reduce residual charge on average, and did not produce operationally usable or
settled PIC reports.

### Safety

- No cloud LLM APIs.
- No API keys or secrets.
- No web browsing during experiment runs.
- No execution of LLM-generated commands.
- Generated raw outputs remain ignored by git.
