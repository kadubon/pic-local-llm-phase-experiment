# PIC 1.1.0 R4: backend, feedback and reuse mechanisms

Execution: COMPLETED. PIC 1.1.0 and its installed 617 payload files are unchanged.

## Design and interpretation

G_minimal and P_minimal consume the exact same generated answer from an identical prompt. They are paired backend replays, not independent model samples. P_full adds actual PIC detail to the same receipt facts. Its effect includes representation, auxiliary runtime information and prompt length; it is not a pure token-length intervention. All finite routes are selected by the orchestrator. Trust/issuer/task/recipient/TTL policy is common and external.

Thirty-two main decisions form eight four-step episodes with three sources each. Pilot is one separate four-step episode. Canonical ID adherence is a secondary endpoint; the primary is correct decision/flag with sufficient authorized evidence. Source updates, partial observations and negative witnesses are kept distinct.

## Confirmatory results

| Endpoint | G minimal | P minimal | P full |
| --- | ---: | ---: | ---: |
| decision_correct | 32 | 32 | 32 |
| supported_success | 32 | 32 | 32 |
| contract_success | 32 | 32 | 32 |
| unsupported_completion | 0 | 0 | 0 |
| unsafe_admission | 0 | 0 | 0 |
| supported_yield | 23 | 23 | 23 |
| obligations_correct | 32 | 32 | 32 |

Primary P_full minus P_minimal: 0.00 percentage points; wins/ties/losses 0/32/0. Episode sign-flip p=1.0; episode bootstrap descriptive interval [0.0, 0.0].

Only eight authored episodes are independent blocks under the working model. Sign-flip inference assumes blockwise exchangeability under the null. Bootstrap intervals are small-sample descriptions; a degenerate interval does not establish equivalence. Task independent exact estimates are explicitly sensitivity analyses, not primary inference.

## Cost

| Arm | Model seconds | PIC seconds | Standalone workflow seconds | Input / output tokens |
| --- | ---: | ---: | ---: | ---: |
| G_minimal | 423.166 | 0.000 | 423.181 | 20754 / 2727 |
| P_minimal | 423.166 | 1.656 | 424.836 | 20754 / 2727 |
| P_full | 2322.110 | 1.642 | 2323.767 | 136454 / 2727 |

Standalone times assign a full observed minimal generation to each hypothetical backend workflow; their sum is not actual campaign compute. The compact inference is physically executed only once per case. Setup is shared between P variants. Campaign metadata records actual attempts and totals. I/O/orchestration is not included in these standalone sums. Prompt order is balanced across episodes; prefix caching and background load are not isolated. Energy, continuous GPU use, FLOPs and monetary cost remain unknown.

## Reuse in separate processes

Each producer persists a content-pinned cache; each consumer starts a fresh interpreter. Both backends recheck current source digest, issuer, task, recipient and TTL. Native checks may be reused; PIC resolution/promotion/runtime still execute. No artificial sleep or simulated verification cost is added. Positive end-to-end savings include producer cost, process startup and persisted I/O; core timings are separate.

| Backend | Samples | Fanout | Cached / no-cache total seconds (two repeats) | Correct |
| --- | ---: | ---: | --- | --- |
| generic | 16 | 1 | 2.3462/2.4196, 2.3428/2.3172 | True |
| generic | 16 | 8 | 2.4350/2.4434, 2.4079/2.4199 | True |
| generic | 4096 | 1 | 2.4056/2.3743, 2.3385/2.3022 | True |
| generic | 4096 | 8 | 2.5066/2.4333, 2.4329/2.4115 | True |
| generic | 65536 | 1 | 2.4443/2.4889, 2.5206/2.5280 | True |
| generic | 65536 | 8 | 2.3776/2.6428, 2.5454/2.6472 | True |
| pic | 16 | 1 | 2.3837/2.3139, 2.5526/2.5510 | True |
| pic | 16 | 8 | 2.6180/2.7079, 2.6655/2.7607 | True |
| pic | 4096 | 1 | 2.4433/2.3916, 2.4295/2.5540 | True |
| pic | 4096 | 8 | 2.7707/2.9613, 2.7114/2.6849 | True |
| pic | 65536 | 1 | 2.5313/2.5772, 2.5037/2.6197 | True |
| pic | 65536 | 8 | 3.0379/3.0914, 2.9240/3.0703 | True |

Two repeats on a fixed local grid cannot establish a general break-even threshold. PIC versus its own no-cache path and PIC versus the generic cache are separate comparisons. Skipped calls are not themselves an efficiency benefit. This workload tests real finite array verification, not arbitrary expensive external proof systems.

## Boundaries and preservation

The common independent verifier supplies per-source verdicts but no aggregate task verdict. A complete negative result needs only one failing witness; missing irrelevant sources do not invalidate that proof. Schema, reference validity and obligation IDs remain separately visible. PIC raw metadata acceptance and protected final admission remain distinct. Development packet identity and production content-reference envelope policy are mixed explicitly as in R3; production cryptographic identity is not tested. Observed time is not the simulated policy clock. These are fixed pipelines and separate producer/consumer processes, not autonomous agents.

Backend replay intentionally removes the model-channel difference. It measures additional backend rejection/acceptance and cost under the same trust policy. Because the generic gate already implements the task proof rule, backend parity here is a conformance observation, not a population equivalence test or proof of improved intelligence. Causal effects of individual PIC fields, general auditability, engineering effort and collective intelligence remain unmeasured. No R1/R2/R3 observations are pooled.

Existing files remain byte-identical under the pre-R4 snapshot; the installed PIC payload is checked before and after execution. Local pre-inference commits are not independently public timestamped registration. Raw prompts/responses and exact runtime artifacts remain private. Public rows support arithmetic checking, not answer-level regrading without raw access.

[Protocol](PROTOCOL_PIC_1_1_0_R4.md), [reproduction](REPRODUCIBILITY_PIC_1_1_0_R4.md), [summary](EXPERIMENT_SUMMARY_PIC_1_1_0_R4.json).
