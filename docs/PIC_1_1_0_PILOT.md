# PIC 1.1.0 technical pilot gate

Date: 2026-10-20 (Asia/Tokyo). Recorded after the four pilot tasks and before
any confirmatory generation. Pilot preregistration SHA-256:
`ea0b04247e429e6659f34d884902cb4d9298e81223c22562833c6f661927c0a0`.

All 12 scheduled model calls completed without retry, timeout, empty output or
truncation. Counts were initial 4, A 4, B 4; one earlier real warmup makes 13
actual calls so far. Every revision used the shared initial answer. Both check
and intake reports parsed for initial and final outputs in both arms.

Independent success was initial 4/4, A 4/4, B 4/4; false completion was 0/4
throughout. The one incomplete-evidence task was correctly declined in all
three stages. These observations indicate a substantial ceiling/floor problem,
not evidence that the arms are equivalent. The independent evaluator's negative
fixtures reject incorrect or unsupported answers, but the pilot did not
demonstrate sensitivity to an incremental treatment effect.

No task, oracle, prompt, inference setting or stopping rule is changed in
response. The twelve confirmatory tasks were authored and frozen before the
pilot; they will be run unchanged. Their results will carry the pilot's
measurement-sensitivity limitation. Pilot effects are excluded from primary
estimates. Historical tasks remain last in the budget order.

PIC returned the same two missing obligations for every pilot answer:
`obligation:baseline-safety` and `proxy-target-grounding-proof`, with residual
burden 2.02. All compact checks had accepted=true, workflow_usable=true,
operationally_usable=false, settled=false. The certification field was absent.
These are stable general framework diagnostics, not task specific verification
requirements. No concrete task evidence acquisition was performed or inferred.

The panel took 172.269 seconds. Recorded model wall times were 36.283 seconds
for common initials, 19.146 for A revisions and 79.491 for B revisions. Actual
revision input tokens were 1502 for A and 5114 for B; both generated 229 tokens.
Initial/final-B PIC diagnosis took 24.273 seconds; A's observational diagnosis
took another 12.164 seconds. This is an overhead warning, not a claim about
general hardware-independent latency.

Before pilot inference: all 81 tests passed (34 historical tests and 47 added
cases), no skips; syntax, Ruff and type checks on all five new core modules
passed. Earlier development checks found an overbroad legacy secret pattern
matching ordinary prose, a literal PowerShell wildcard passed to mypy, three
type-check issues and a string-formatting syntax error in the task builder.
All were corrected before freezing or inference. The old scanner was not
weakened; prose was reworded. The original first combined run was 80 passed,
1 failed; this history is retained in ignored setup diagnostics.

Gate decision: technically runnable within the fixed budget; proceed with
the unchanged main protocol. No efficacy Go decision is made. The ceiling and
generic actionability findings constrain any later inference.
