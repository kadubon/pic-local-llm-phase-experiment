# Changelog

## Unreleased - PIC 1.1.0 R3 (2026-10-20)

- Added a separate preregistered evidence-bound experiment: four pilot and
  sixteen confirmatory tasks with shared initial answers, review A, independent
  verifier plus strong generic ledger B, and the same evidence plus actual PIC C.
  All 81 local generations including warmup completed without retry/truncation.
- Recorded composite success A 0/16, B 15/16, C 13/16. C-B is -12.5 percentage
  points, conservative 95% interval [-41.95, +22.88], exact McNemar p=0.5.
  B/C both have correct decisions 16/16 and supported completion yield 7/7.
  No arm makes an unsupported completion. The predeclared `HARM_OBSERVED`
  label describes composite point degradation, without establishing general harm.
- Added a descriptive endpoint audit: A discloses uncertainty but fails the
  machine obligation-ID contract; C's two extra composite failures concern a
  holding citation or extra obligation text. Frozen scoring remains unchanged.
- Exercised real PIC native predicates, SDK/runtime and five CLI operations.
  Four invalid deterministic cases pass raw packet promotion; a common outer
  provenance/semantic gate protects both B/C. Protection is not PIC-only.
- Recorded C/B measured workflow time ratio 2.043 and approximately twice the
  allocated tokens. One valid main reuse skips verifier calls without a time
  saving. No incremental efficacy, safety or resource-efficiency claim is supported
  by this small, single-model finite benchmark.
- Updated README and Docs for results, limitations and model-free checks.
  Separate publication validation preserves all frozen R3 artifacts and earlier
  results/raw archives; only three prior navigation/changelog files are updated.
  No inference is repeated for publication. Package version remains 0.2.0.

See the [R3 report](docs/EXPERIMENT_REPORT_PIC_1_1_0_R3.md),
[endpoint audit](docs/PIC_1_1_0_R3_ENDPOINT_AUDIT.md) and
[publication guide](docs/PUBLICATION_PIC_1_1_0_R3.md).

## Unreleased - PIC 1.1.0 research campaigns (2026-10-20)

- Added an isolated, hash-locked PIC 1.1.0 profile using the installed local
  `gemma4:e4b` digest, shared initial answers, one revision per arm, an
  independent oracle, bounded stop rules and measured resource accounting.
- Recorded the first campaign's completed 12-task confirmation, stopped
  historical panel, failed/truncated attempts and oracle-validity audit.
  Post-hoc normalization sensitivity is separate from confirmatory results.
- Prospectively fixed source-ID/type semantics and evidence sufficiency in
  R2, with twenty fresh tasks, exhaustive finite-domain proof enumeration,
  deletion counterexamples, separate formatting metrics and substantive false
  completion scoring. Protocol/code/gold were committed locally before pilot
  inference; the confirmatory manifest was frozen before main inference.
- Completed R2: four pilot tasks and sixteen confirmatory tasks, 61 actual
  local generations including warmup, with no generation failure/truncation.
  Confirmatory success is A 8/16 versus B 9/16; false completion is 7/16 versus
  6/16. The success difference is +6.25 percentage points, conservative 95%
  interval [-23.9, +33.8]; superiority is not established. The only discordance
  reflects A losing an initially correct answer. Allocated measured workflow
  time is 191.2 s versus 479.5 s; no resource-efficiency advantage is shown.
- Added sanitized per-answer metrics, protocols, frozen manifests, validation,
  obligation audits and offline arithmetic checks. Raw outputs, private
  archives, local environment details and weights remain excluded from Git.
- Updated the README and documentation index, with a separate publication
  guide explaining immutable experiment snapshots and later Docs updates.
  Prior results/configurations and experiment identities remain preserved.
- Retained package version 0.2.0 and historical workflow behavior. This is a
  research update using PIC 1.1.0, not a new package release or a rerun of the
  historical v0.1.0/v0.2.0 reports.

See the [documentation index](docs/README.md) and
[publication guide](docs/PUBLICATION_PIC_1_1_0.md) for the recorded evidence and
the distinction between local preregistration and later public availability.

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
