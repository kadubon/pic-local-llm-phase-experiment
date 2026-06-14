# Changelog

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
