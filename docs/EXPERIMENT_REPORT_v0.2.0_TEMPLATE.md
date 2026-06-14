# PIC Local LLM Phase Experiment Report v0.2.0 Template

Status: pending run

This is the tracked public template for the v0.2.0 shared-initial experiment.
It is intentionally not a result report. It contains no fabricated metric table,
no invented run id, and no claimed outcome.

For the completed public v0.2.0 run, see
`docs/EXPERIMENT_REPORT_v0.2.0.md`.

## What Is PIC?

Percolation Inversion Compiler (PIC) is a finite certificate,
verifier-routing, and residual-ledger runtime for protocol-relative ASI-proxy
research. In this repository, PIC is used as a bounded agent-output checker. It
parses a local LLM candidate answer into finite diagnostic fields such as
`accepted`, `operationally_usable`, `settled`,
`runtime_report.missing_obligations`, `runtime_report.residual_ledger`, and
`residual_summary`.

PIC is not an ASI detector, ASI creator, truth oracle, or authorization system
for external action. A PIC report can be useful while still leaving
`settled=false` and visible unresolved obligations.

## What v0.2.0 Tests

v0.2.0 introduces `shared_initial` mode. For each task, the local Ollama model
produces one initial answer. That exact same answer is then used by both
branches:

- Baseline branch: the shared initial answer is self-reviewed and revised by the
  local LLM.
- PIC-assisted branch: the shared initial answer is checked by `pic agent
  intake`, repaired using PIC residuals and missing obligations, and checked by
  `pic agent intake` again.

This design reduces comparison noise from different initial generations. It
does not by itself prove that the PIC-assisted branch is better. Any conclusion
must come from the recorded metrics of a real run.

## Planned Configuration

The intended v0.2.0 config is:

```text
configs/experiment.shared_initial.yaml
```

Expected workload for 10 tasks and one repair round:

- `40` local Ollama generations
- `20` PIC intake calls

The historical v0.1.0-compatible config remains:

```text
configs/experiment.default.yaml
```

That mode uses separate initial generations and estimates `50` local Ollama
generations with `20` PIC intake calls.

## Required Artifact Map

Each v0.2.0 task run should include:

- `task.yaml`
- `shared_initial_answer.txt`
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

For `shared_initial` mode, `shared_initial_answer.txt`, `baseline_initial.txt`,
and `pic_initial_candidate.txt` must contain the same initial answer text for
the task.

## Metrics To Report After A Real Run

The generated report should include, at minimum:

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

Sign convention: `pic_missing_obligation_delta = before - after`. A positive
value means fewer missing obligations after repair.

## Interpretation Rules

- Treat `accepted`, `operationally_usable`, and `settled` as separate fields.
- Do not treat `accepted=true` as settlement.
- Treat `local_phase_score` as a local workflow diagnostic only.
- Interpret obligation coverage and residual-charge changes as heuristics, not
  as truth or intelligence measurements.
- Inspect raw PIC reports before making claims about missing fields or schema
  drift.

## What This Template Cannot Conclude

This template cannot conclude that PIC improves any metric, creates ASI, proves
ASI phase formation, makes a local model superintelligent, validates external
actions, or accelerates real-world capability.

The v0.2.0 result report should be generated only after a real shared-initial
run has completed, been analyzed, and passed public safety review.
