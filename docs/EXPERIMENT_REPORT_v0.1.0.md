# PIC Local LLM Phase Experiment Report v0.1.0

## Abstract

This is the public, tracked report for v0.1.0. It summarizes a bounded local
experiment comparing a baseline local LLM self-review workflow with a
PIC-assisted residual-preserving repair workflow.

The report is diagnostic. It does not measure real ASI, intelligence, truth, or
external-world capability.

## What Is PIC?

Percolation Inversion Compiler (PIC) is used here as a finite
certificate/verifier-routing and residual-ledger runtime. In this experiment,
PIC checks local LLM candidate answers and returns finite diagnostic fields such
as `accepted`, `operationally_usable`, `settled`,
`runtime_report.missing_obligations`, residual ledger data, and
`residual_summary`.

PIC is not an ASI detector, ASI creator, oracle, or proof that a local model has
external-world capability. In this repo, PIC is treated as a local diagnostic
runtime that keeps obligations and residuals visible.

## Research Question

When a local LLM answer is checked by PIC and repaired using PIC residuals and
missing obligations, do local workflow indicators improve compared with a
baseline local LLM self-review loop?

## Experimental Setup

- Release: `v0.1.0`
- Run id: `20260614-004542`
- Task count: `10`
- Model: `qwen3.5:35b-a3b`
- Runtime: local Ollama
- PIC profile: `development`
- PIC commit: `fa5ca5ddafc104effa7116559e2d8a46acd57cdd`
- Temperature: `0`
- Top-p: `1`
- Seed: `42`
- Max generated tokens: `1024`
- Ollama request mode: streaming with thinking disabled
- Repair rounds: `1`
- Local generation count estimate: `50`
- PIC intake count estimate: `20`

## Conditions

Baseline condition:

- Ask the local LLM to answer the task.
- Ask the same local LLM to self-review once.
- Ask it to produce a final answer.

PIC-assisted condition:

- Ask the local LLM to answer the same task.
- Run `pic agent intake` on the candidate answer.
- Parse PIC residual summaries and missing obligations.
- Feed the diagnostic fields back to the local LLM.
- Ask for one repair attempt.
- Run `pic agent intake` again.

## Result Table

| task | baseline coverage | PIC coverage | missing obligation delta | PIC usable after | PIC settled after | local phase score |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| task_001_readme_improvement | 1.000 | 1.000 | 0 | no | no | 0.690 |
| task_002_python_bugfix | 1.000 | 1.000 | 0 | no | no | 0.640 |
| task_003_test_plan | 1.000 | 1.000 | 0 | no | no | 0.480 |
| task_004_pr_summary_critique | 1.000 | 1.000 | 0 | no | no | 0.750 |
| task_005_evidence_requirements | 1.000 | 1.000 | -2 | no | no | 0.660 |
| task_006_safety_boundary | 1.000 | 1.000 | 0 | no | no | 0.720 |
| task_007_refactoring_plan_review | 0.600 | 0.800 | 0 | no | no | 0.460 |
| task_008_documentation_gap | 1.000 | 1.000 | 0 | no | no | 0.610 |
| task_009_rag_answer_audit | 1.000 | 1.000 | 0 | no | no | 0.720 |
| task_010_agent_message_audit | 1.000 | 1.000 | 0 | no | no | 0.720 |

## Aggregate Results

- Average baseline heuristic obligation coverage: `0.960`
- Average PIC-assisted heuristic obligation coverage: `0.980`
- Average PIC missing-obligation delta: `-0.200`
- Average PIC residual charge delta: `-0.574`
- PIC accepted-after ratio: `1.000`
- PIC operationally-usable-after ratio: `0.000`
- PIC settled-after ratio: `0.000`
- PIC schema-field usable ratio: `1.000`
- Average local phase score: `0.645`
- Task errors recorded by this repo: none

## Interpretation

The run supports a narrow positive claim: PIC exposed parseable residual
summaries, missing obligations, runtime report fields, route request counts, and
agent task counts for every task. This improved diagnostic traceability.

The run does not support a claim that one PIC-assisted repair round reduced PIC
obligations. Missing-obligation counts did not decrease in nine tasks and
increased in one task. Residual charge also increased on average.

The run does not support a claim that outputs became operationally usable or
settled under PIC. All repaired outputs remained `operationally_usable=false`
and `settled=false`.

## Important Negative Result

The most important result is negative: PIC made unresolved obligations visible,
but one local LLM repair round did not reduce missing obligations or discharge
those obligations. This is a useful scientific boundary. It prevents the repo
from overstating PIC-assisted repair as settlement or real-world capability.

The recurring remaining obligations were:

- `obligation:baseline-safety`
- `proxy-target-grounding-proof`

For `task_005_evidence_requirements`, the repaired output exposed additional
obligations:

- `continuous-physics-envelope`
- `resource-calendar-domain-witness`

These obligations are protocol-level diagnostics, not ordinary prose quality
checks. A text-only local repair loop should not be expected to discharge them
without additional verifier inputs.

## What This Report Cannot Conclude

This report cannot conclude that PIC creates ASI, proves ASI phase formation,
makes a local model superintelligent, validates physical or oracle outcomes, or
proves external-world capability acceleration.

It also cannot conclude that PIC-assisted output quality is generally better
than baseline output quality. The experiment used one local model, ten synthetic
tasks, heuristic metrics, and no human expert grading.

## Release-Level Conclusion

For v0.1.0, the repo demonstrates a working local PIC plus Ollama experiment
pipeline and a reproducible diagnostic report. The empirical result is cautious:
PIC improved residual visibility and schema-level traceability, but did not
reduce missing obligations, residual charge, operational usability failures, or
settlement failures in this one-round repair design.
