# PIC Local LLM Phase Experiment Report v0.2.0

Status: completed run

Run id: `20260614-050311`

This is the public, tracked report for the v0.2.0 shared-initial experiment. It
summarizes bounded local metrics only. It does not publish raw model outputs,
raw PIC reports, or local runtime paths.

## Abstract

v0.2.0 tested whether a PIC-assisted residual-preserving repair loop improves
finite local workflow diagnostics when both the baseline and PIC-assisted
branches start from the exact same initial local LLM answer.

The shared-initial design worked as intended: all 10 tasks used the same initial
answer for `shared_initial_answer.txt`, `baseline_initial.txt`, and
`pic_initial_candidate.txt`.

The main result is mixed and mostly negative. PIC exposed residual summaries and
runtime fields consistently, and the PIC-assisted branch had a small positive
heuristic obligation-coverage delta. However, one repair round did not reduce
PIC missing obligations on average, did not reduce residual charge on average,
and did not produce any `operationally_usable=true` or `settled=true` repaired
reports.

## What Is PIC?

Percolation Inversion Compiler (PIC) is a finite certificate,
verifier-routing, and residual-ledger runtime for protocol-relative ASI-proxy
research. In this repository, PIC is used as a bounded agent-output checker. It
parses local LLM candidate answers into finite diagnostic fields such as
`accepted`, `operationally_usable`, `settled`,
`runtime_report.missing_obligations`, `runtime_report.residual_ledger`, and
`residual_summary`.

PIC is not an ASI detector, ASI creator, truth oracle, or authorization system
for autonomous external action. A useful diagnostic report can still have
`settled=false`.

## Research Question

Does adding PIC as a residual-preserving checker improve local LLM workflow
diagnostics compared with a baseline local LLM self-review loop when both
branches begin from the same initial answer?

## Experimental Design

- Experiment mode: `shared_initial`
- Task count: `10`
- Local model: `qwen3.5:35b-a3b`
- Ollama endpoint class: local endpoint
- Temperature: `0.0`
- Top-p: `1.0`
- Seed: `42`
- Max generated tokens: `1024`
- Repair rounds: `1`
- Estimated workload: `40` local Ollama generations and `20` PIC intake calls
- PIC profile: `development`
- PIC version: `0.4.1`
- PIC commit: `fa5ca5ddafc104effa7116559e2d8a46acd57cdd`
- Task errors recorded in metrics: `0`

The experiment remained local-only. It did not use cloud LLM APIs, API keys, web
browsing during experiment runs, arbitrary execution of LLM output, or automatic
external actions.

## Why Shared Initial Answer Matters

In v0.1.0, the baseline branch and PIC-assisted branch each received a separate
initial local LLM generation. That design was useful for a first public run, but
it left a confound: branch differences could come from different initial
answers before PIC entered the loop.

v0.2.0 removes that confound for this task set. For each task, the initial
answer was generated once and reused by both branches:

- `shared_initial_answer.txt`
- `baseline_initial.txt`
- `pic_initial_candidate.txt`

Artifact equality check: `10 / 10` task directories had identical shared,
baseline-initial, and PIC-initial candidate text.

## Conditions

Baseline condition:

- Start from the shared initial answer.
- Ask the local LLM to self-review once.
- Ask the local LLM to produce a final answer.

PIC-assisted condition:

- Start from the same shared initial answer.
- Run `pic agent intake` on that answer.
- Feed PIC residual summary and missing obligations into one repair prompt.
- Ask the local LLM for one repaired output.
- Run `pic agent intake` on the repaired output.

## Operational Definitions

- `accepted`: PIC accepted the finite checker path for this report shape. This
  is not treated as settlement.
- `operationally_usable`: PIC indicated the result may be useful for routing
  under the current protocol.
- `settled`: scoped finite obligations were discharged. This is stricter than
  `accepted`.
- `pic_missing_obligation_delta`: `before - after`; positive means fewer missing
  obligations after repair.
- `pic_residual_charge_delta`: `before - after`; positive means normalized
  residual charge decreased after repair.
- `local_phase_score`: this repository's bounded heuristic score over finite
  observables. It is not a PIC theorem and not an intelligence metric.

## Results Table

| task | baseline coverage | PIC coverage | coverage delta | missing obligation delta | residual charge delta | PIC usable after | PIC settled after | local phase score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| task_001_readme_improvement | 1.000 | 1.000 | 0.000 | 0 | 0.000 | no | no | 0.690 |
| task_002_python_bugfix | 1.000 | 1.000 | 0.000 | 0 | 0.000 | no | no | 0.640 |
| task_003_test_plan | 1.000 | 1.000 | 0.000 | 0 | 0.000 | no | no | 0.480 |
| task_004_pr_summary_critique | 1.000 | 1.000 | 0.000 | 0 | -1.000 | no | no | 0.750 |
| task_005_evidence_requirements | 1.000 | 1.000 | 0.000 | -2 | -2.735 | no | no | 0.660 |
| task_006_safety_boundary | 1.000 | 1.000 | 0.000 | 0 | -1.000 | no | no | 0.720 |
| task_007_refactoring_plan_review | 0.600 | 0.800 | 0.200 | 0 | 0.000 | no | no | 0.460 |
| task_008_documentation_gap | 1.000 | 1.000 | 0.000 | 0 | 0.000 | no | no | 0.610 |
| task_009_rag_answer_audit | 1.000 | 1.000 | 0.000 | 0 | 0.000 | no | no | 0.720 |
| task_010_agent_message_audit | 1.000 | 1.000 | 0.000 | 0 | -1.000 | no | no | 0.720 |

## Aggregate Results

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
- PIC obligation-preservation score mean: `0.775`
- PIC candidate-reuse score mean: `0.600`
- Baseline candidate-reuse score mean: `0.500`

## Distribution Notes

- Missing-obligation delta distribution: `0` on 9 tasks, `-2` on 1 task.
- Residual-charge delta distribution: `0.000` on 6 tasks, `-1.000` on 3 tasks,
  `-2.735` on 1 task.
- Only one task improved heuristic obligation coverage:
  `task_007_refactoring_plan_review`, from `0.600` to `0.800`.
- One task worsened missing-obligation count:
  `task_005_evidence_requirements`, from `2` before repair to `4` after repair.
- Four tasks worsened residual charge:
  `task_004_pr_summary_critique`, `task_005_evidence_requirements`,
  `task_006_safety_boundary`, and `task_010_agent_message_audit`.
- PIC runtime/schema fields were parseable on all 10 tasks.
- PIC residual response was detected heuristically on 9 of 10 tasks.

## Interpretation

The strongest positive result is methodological: shared-initial branching worked
and reduced the initial-answer confound present in v0.1.0.

The strongest PIC-specific positive result is diagnostic visibility. PIC
produced parseable runtime reports, residual summaries, missing-obligation
counts, route request counts, and residual charge totals for every task.

The strongest negative result is repair effectiveness. One PIC-guided repair
round did not reduce missing obligations on average and did not reduce residual
charge on average. PIC accepted every repaired report, but none became
operationally usable or settled under the observed PIC fields.

The small average coverage gain, `+0.020`, should be treated cautiously. It came
from one task and uses this repository's heuristic obligation matcher, not human
expert grading.

## Relation To v0.1.0

The v0.1.0 public report remains a historical record. v0.2.0 is not a direct
replication with the same branching design; it changes the initial-answer
control. The broad pattern is nevertheless consistent with v0.1.0: PIC improved
diagnostic traceability, but a single repair round did not produce settled or
operationally usable repaired outputs.

## Important Negative Result

This run does not support a claim that one PIC-assisted repair round improves
PIC settlement, operational usability, missing-obligation count, or residual
charge in this local 10-task setup.

## Threats To Validity

- One local model only.
- Small synthetic task set.
- No human expert grading layer.
- No external task execution or real-world tool-use validation.
- Heuristic obligation coverage can miss semantic quality differences.
- PIC metrics are protocol-relative and may change with upstream PIC behavior.
- Local Ollama behavior may vary across hardware, drivers, and model packaging.
- One repair round may be too shallow to test iterative PIC-guided repair.
- The shared-initial design improves branch comparability but does not solve
  task set size, metric validity, or external-validity limits.

## Public Safety Notes

- Generated raw model outputs remain ignored by git.
- Generated PIC reports remain ignored by git.
- This tracked report contains aggregate metrics and task identifiers, not raw
  model text.
- The experiment did not call cloud LLM APIs.
- The experiment did not require API keys.
- The experiment did not execute LLM-generated commands.

## What This Report Cannot Conclude

This report cannot conclude that PIC creates ASI, proves ASI phase formation,
makes a local model superintelligent, validates physical or oracle outcomes,
improves real-world capability, or proves autonomous external adoption.

The result supports only cautious local claims about this repository's observed
workflow diagnostics under this model, task set, PIC version, and prompt design.

## Conclusion

v0.2.0 successfully implemented and ran the shared-initial experimental design.
PIC provided consistent residual visibility and parseable diagnostic fields, but
one PIC-assisted repair round did not improve PIC missing-obligation counts,
residual charge, operational usability, or settlement in this run. The public
scientific posture should therefore emphasize diagnostic traceability and the
negative repair-effectiveness result, not capability claims.
