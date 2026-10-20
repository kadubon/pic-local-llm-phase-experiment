# PIC 1.1.0 local LLM matched comparison

Status: **INCOMPLETE**. Confirmatory panel: **COMPLETED**.
Run date: 2026-10-20 (Asia/Tokyo). Local execution only; no push or publication.

## 1. Abstract

Twelve new, independently graded synthetic tasks compared a fixed generic
review (A) with PIC-guided review (B), using a single shared initial answer and
one revision call per arm. Independent success was 2/12 for A
and 2/12 for B; unsupported completion was
5/12 and
5/12.
The paired success difference was 0.0
percentage points (conservative exact 95% CI
[-30.6, 30.6] pp). No incremental task success benefit was observed.
PIC produced structured status and residual records, but these remained general
framework obligations. The PIC workflow cost 342.968 measured seconds versus
94.794 for A under the allocation defined below. A post hoc audit found
that citation notation and overinclusive required-evidence sets materially
affect these strict endpoints. The frozen primary labels are retained, but
practical efficacy is **inconclusive** because of measurement-validity limits,
one model and small sample size.

## 2. Research question and hypotheses

H1: structured diagnosis. H2: independent task success. H3: unsupported
completion. H4: resource efficiency. H5: unresolved obligation preservation.
H1 does not establish H2-H5. The target is incremental benefit relative to
ordinary review, not PIC acceptance in isolation. No ASI, intelligence phase
transition, collective intelligence or external-world capability was measured.

## 3. Exact environment and version identities

- PIC: non-editable PyPI **1.1.0**, wheel SHA-256
  `2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7`. PyPI JSON confirmed 1.1.0 as latest stable
  at preparation. Import was verified under the independent environment.
- Model: **gemma4:e4b**, digest
  `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`, 7.5B,
  Q4_K_M, GGUF. Reported parent model:
  `gemma4-validation-20260929:e4b-imatrix-attention-q6-q8-draft2`. This identity is an observed
  local Ollama package; it is not an independently authenticated vendor model.
- Ollama: 0.35.0; Python: `3.14.7 (main, Sep 24 2026, 17:57:14) [MSC v.1944 64 bit (AMD64)]`;
  uv: `uv 0.12.19 (bea138450 2026-09-24 x86_64-pc-windows-msvc)`; platform: `Windows-11-10.0.26300-SP0`.
- CPU: AMD Ryzen 7 8840HS, 8 cores / 16 logical CPUs; RAM:
  66,363,183,104 bytes. GPU: Radeon 780M integrated graphics. Windows adapter
  RAM reports 2 GiB, which is not a measured dedicated VRAM allowance.
- Observed Ollama `size_vram`: [0] bytes. CPU snapshots ranged
  12.3-84.1%; RAM snapshots 43.4-48.9%.
  Snapshots do not measure peaks; GPU utilization is missing.
- Base experiment commit: `50e10a05dec4fc72df4170610778838f686d3223`. Preregistration commit:
  `501a1d8f3afcc281cd82c140da89b5e43c98e5c3`. No changes to PIC source, models or other servers.

The historical `qwen3.5:35b-a3b` was absent. Existing `gemma4:e4b` was selected
for a finite local workload; the installed `qwen3.6:35b-a3b` was unused. No model
download occurred. Results cannot be attributed causally to PIC version changes.

## 4. Preregistered protocol and pilot

The full design is [PROTOCOL_PIC_1_1_0.md](PROTOCOL_PIC_1_1_0.md).
Main manifest SHA-256: `3ad939865c8c50a340f434d0995483d1d0cd7dd1738ed147d7442df8adc1479e`.
Pilot manifest SHA-256: `ea0b04247e429e6659f34d884902cb4d9298e81223c22562833c6f661927c0a0`.
Both manifests and Git/worktree byte identities are provided alongside this
report. Windows CRLF worktree hashes can differ from normalized Git blobs;
SOURCE_IDENTITIES records both. Frozen sources were unchanged during inference.
PREREG_IDENTITIES additionally records normalized LF hashes for the manifests.

Pilot results: initial 4/4,
A 4/4, B 4/4;
unsupported completion 0/4 in each arm. The ceiling and general diagnostics were
recorded before confirmation in [the pilot gate](PIC_1_1_0_PILOT.md). No task,
oracle, prompt, endpoint or stopping rule was changed in response. Pilot outcomes
are excluded from confirmatory estimates. There was no outcome-driven extension.

The protocol and source were locally committed before main freeze and first
confirmatory generation. A legacy secret regex again flagged ordinary prose in
the pilot note during the pre-main repeated audit. The shell sequence continued
after that false positive; the note was corrected and all 81 tests passed.
The frozen inference/evaluation files and protocol were unaffected. This is a
document-audit sequencing deviation, not a revised scientific condition.

## 5. Dataset and independent oracle

Four families have three confirmatory tasks each: multi-record integration,
effective policy version, uncertainty/conflicting evidence and strict validation.
Seven tasks allow definite decisions; five require an incomplete/abstaining
answer. Sources are closed synthetic records. The oracle requires a correct
typed decision, evidence drawn from a predeclared minimal set, correct completion
flag and exact unresolved task obligations. JSON fences are accepted only around
the whole object; duplicate keys/nonfinite values and invented citations fail.
PIC acceptance, prose quality and keyword counts are never gold labels.

Public inputs and gold data are separate files. Generation never reads gold.
PIC is given only candidate text, with live connectors disabled. Neither the
model nor PIC is given filesystem tools or oracle paths. Grading runs after
the scheduled panel, with no feedback into generation. These tasks were authored
before inference, but they are not an externally validated benchmark or a
securely held-out institutional test set. Shared construction limits independence.

## 6. Matched experimental arms

Each task receives exactly one initial call, one A revision and one B revision.
The original task and initial bytes are identical across arms; all 12 shared
initial hash comparisons passed. The common wrapper is fixed. A receives the
predeclared generic checklist; B receives unchanged selected actual check/intake
fields. Both prompts explain that review material is advisory and not evidence.
Seed 20261020 counterbalances six A-first and six B-first tasks. There is no
shared conversation history, external search, tool execution or manual repair.

All task calls: temperature=0, top_p=1, seed=20261020, num_ctx=16384,
num_predict=768, think=false, keep_alive=10m. The exact model/digest is checked
before every request. Equal limits do not mean equal realized tokens or cost.

## 7. Resource accounting

| Confirmatory component | Calls | Input tokens | Output tokens | Model wall seconds | PIC seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Common initial | 12 | 2810 | 657 | 59.390 | 36.492 |
| A revision | 12 | 4871 | 675 | 65.099 | 37.062 observational |
| B revision | 12 | 15697 | 849 | 240.100 | 36.680 |

Half of common initial generation is charged to each arm. B additionally bears
initial plus final PIC diagnosis; A's final PIC diagnosis is research overhead.
Independent evaluator time is 0.000226 seconds for A and
0.000228 for B, measured on this analysis pass. Allocated
workflow totals are **A 94.794 s, B 342.968 s** (B/A 3.62).
These allocated totals sum timed generation, grading and required PIC processes;
they omit identity-query, file I/O and orchestration costs. The actual panel
wall time below includes that work and is reported separately.
Allocated token totals are A 7279.5, B 18279.5
(B/A 2.51). PIC B-path overhead alone is
73.173 seconds.

Same-success matched cases: 2/12. Their exact per-task
revision and PIC costs are in the JSON summary; this comparison is descriptive,
conditioned on joint success. Unconditional all-task totals above remain primary
resource reporting. In those two joint-success cases, A revision time totals
7.723 seconds;
B revision time totals
40.051 seconds,
plus 12.222
seconds of required PIC work. These figures omit the equally shared initial
generation. Recorded Ollama timing components in seconds:
`{"A": {"eval_duration": 21.518361, "load_duration": 0.041038, "prompt_eval_duration": 42.995546}, "B": {"eval_duration": 28.38909, "load_duration": 0.0412662, "prompt_eval_duration": 211.187202999}, "initial": {"eval_duration": 22.078007, "load_duration": 0.0440871, "prompt_eval_duration": 36.651201}}`.

Complete panel wall time is 477.576 seconds, including both
arms and all diagnostic collection. Across all panels, model calls took
829.237 measured seconds and check/intake collection 175.192
seconds, excluding warmup and auxiliary fixed-text probes. Prefix caching and
model load can influence timing. Raw cache counters and load durations are saved;
there was no cache isolation or controlled hardware utilization. Monetary cost,
energy, continuous GPU utilization and true total compute FLOPs are missing.
The elapsed campaign span from pilot start to the historical stopping event was
1245.809 seconds, including inter-panel protocol/report work. The
earlier warmup took 28.194 seconds. Across all 58 real calls, input/output/total
tokens were 37865/
7783/
45648.

## 8. Primary results

| Endpoint | A | B | B minus A | Conservative exact 95% CI |
| --- | ---: | ---: | ---: | --- |
| Independently verified success | 2/12 | 2/12 | 0.0 pp | [-30.6, 30.6] pp |
| Unsupported completion | 5/12 | 5/12 | 0.0 pp | [-30.6, 30.6] pp |

Success wins/ties/losses for B: 0/12/0.
False-completion increases/ties/decreases for B:
0/12/0. Exact McNemar p-values:
success 1.000, false completion
1.000. These do not establish equivalence.

Per-arm success Wilson 95% intervals: A [0.04696514218385378, 0.4480308622529734],
B [0.04696514218385378, 0.4480308622529734]. False-completion intervals:
A [0.19326031365875665, 0.6804886874504503], B [0.19326031365875665, 0.6804886874504503].
Unknown completion flags: A 0,
B 0; paired observable denominator 12.
Planned-denominator false-completion bounds: A
[0.4166666666666667, 0.4166666666666667], B [0.4166666666666667, 0.4166666666666667].

The paired bootstrap success interval is
[0.0, 0.0] pp; false completion is
[0.0, 0.0] pp. With no discordance these
intervals degenerate; the nonzero conservative exact bounds above are emphasized.
The exact construction assumes exchangeable independent tasks for population
interpretation. Template dependence further limits generalization.

| Task | Order | Initial success | A success | B success | A false completion | B false completion |
| --- | --- | ---: | ---: | ---: | --- | --- |
| integrate_01 | AB | 0 | 0 | 0 | True | True |
| integrate_02 | BA | 0 | 0 | 0 | True | True |
| integrate_03 | BA | 0 | 0 | 0 | False | False |
| version_01 | AB | 0 | 0 | 0 | True | True |
| version_02 | BA | 0 | 0 | 0 | True | True |
| version_03 | AB | 0 | 0 | 0 | False | False |
| conflict_01 | BA | 1 | 1 | 1 | False | False |
| conflict_02 | AB | 0 | 0 | 0 | True | True |
| conflict_03 | BA | 1 | 1 | 1 | False | False |
| validate_01 | BA | 0 | 0 | 0 | False | False |
| validate_02 | AB | 0 | 0 | 0 | False | False |
| validate_03 | AB | 0 | 0 | 0 | False | False |

| Family | A success | B success | A false completion | B false completion |
| --- | ---: | ---: | ---: | ---: |
| integration | 0/3 | 0/3 | 2 | 2 |
| uncertainty | 2/3 | 2/3 | 1 | 1 |
| validation | 0/3 | 0/3 | 0 | 0 |
| versioning | 0/3 | 0/3 | 2 | 2 |

## 9. Secondary diagnostic results

Initial success was 2/12. Valid evidence:
A 2/12, B 2/12.
Evidence-complete abstention under the strict oracle:
A 2/5,
B 2/5.
Exact task obligation disclosure: A 11/12,
B 12/12, including empty sets on resolved tasks.
All five intrinsically incomplete tasks retained the required obligation ID in
both arms. A introduced one extra, incorrect obligation label on a resolved
validation task; B also failed that task's decision. These are distinct from
disappearing unresolved obligations.

### Measurement-validity audit (post hoc, not a revised primary analysis)

The model often cited the displayed bracketed form of a source ID while the
oracle required its bare identifier. Some required sets also included context
beyond the logically smallest proof: for example, a later non-retroactive policy
was required in addition to an older rule explicitly effective on the event
date. The inputs did not make every such citation requirement unambiguous.
Consequently, the strict unsupported-completion endpoint combines factual errors
with notation/type/evidence-contract failures. It cannot be read as five false
real-world factual decisions per arm.

The separate [oracle audit](PIC_1_1_0_ORACLE_AUDIT.json) leaves all gold and
primary labels unchanged. Exact typed decision correctness is
7/12 for A and
7/12 for B. Allowing
numeric strings only for integer-valued decisions gives
8/12 in
each arm. Of each arm's five strict unsupported completions, two contain an
incorrect substantive decision; three have the intended decision but fail the
predeclared evidence/type contract. All five intrinsically incomplete-evidence
tasks have complete=false in both arms; their missing evidence was not claimed
verified. Fully evidence-complete abstention nevertheless passes only 2/5.

An explicitly exploratory surface-normalization sensitivity unwraps known
bracketed source IDs and converts decimal integer strings when gold is integer.
It preserves required evidence sets and yields A
4/12 versus B
5/12 successes, and
5/12 versus
4/12
unsupported completions. The one-task difference reflects mirror-record
citation retention; this post hoc rule cannot support a confirmatory benefit
claim. This sensitivity is disclosed to show measurement dependence, not
substituted for the preregistered endpoints. Efficacy judgment is held pending
prospectively validated, unambiguous scoring.

B final compact check flags: accepted 12/12,
workflow_usable 12/12,
operationally_usable 0/12,
settled 0/12. `acceleration_metrics_certified` was
missing in 12/12. A and common
initial flags are separately preserved in the JSON; no missing flag became false.

Across the 56 observed
answer diagnostics (78 answer slots planned), missing-obligation set counts
were `{('obligation:baseline-safety', 'proxy-target-grounding-proof'): 56}` and residual-burden counts `{'2.02': 56}`.
Unsupported PIC obligation disappearances observed: 0.
This establishes persistence of general framework labels, not accurate tracking
of each task's missing fact, current policy or external approval. Text repair
did not provide external verifier evidence or settlement.

Actionability audit: the recurring labels `obligation:baseline-safety` and
`proxy-target-grounding-proof` identify framework requirements. Suggested routes
such as `adapters.domain.verify_ecpt_proxy_target_contract`,
`seed-autocatalytic-closure` and `reduce-downstream-search-cost` concern the
minimal runtime demonstration, not these records' decision rules. No
task source-specific missing evidence or corrective arithmetic was identified
by those labels. Framework verification is not satisfiable by merely rewriting
an answer. Full returned tasks/routes remain in the local diagnosis files;
they were not replaced with task aware advice.

Auxiliary fixed-text boundary probes (not generated model trials):

| Probe | accepted | workflow_usable | operationally_usable | settled | Missing count |
| --- | --- | --- | --- | --- | ---: |
| unsupported_completion | True | True | False | False | 2 |
| honest_missing_evidence | True | True | False | False | 2 |
| self_declared_settlement | True | True | False | False | 2 |
| plain_nonclaim | True | True | False | False | 2 |
| unsupported_completion_repeat | True | True | False | False | 2 |

These probes assess status behavior on self-assertions and missing evidence.
Acceptance remains a structural result, not detection of answer correctness.
No external truth or approval was verified. The repeated identical probe checks
diagnostic stability, not a new statistical unit.

Runtime comparison applicability: **NOT_APPLICABLE_MISSING_RUNTIME_MEASUREMENT_CONTRACT**. Actual saved model
records are not RuntimeRunReport trajectories with a calibrated evidence-backed
resource contract. Missing items include protocol/envelope bindings and
verification yield, receiver reuse and residual half-life measurements. The
intake's embedded proxy scores, costs and acceleration eligibility are modeled
demo-state values and are excluded from empirical performance estimates.
No fabricated run report was submitted and no acceleration certificate claimed.

## 10. Comparison with historical v0.2.0

The original negative result is preserved: heuristic coverage 0.960 versus
0.980, missing-obligation delta -0.200 (before minus after), residual delta
-0.574, accepted-after 10/10, operationally usable 0/10 and settled 0/10.
It did not establish task quality improvement. The old baseline used two
revision-related calls, the old PIC arm one; the model was qwen3.5 and PIC 0.4.1.
Current matched revisions use one call each and a different model. Therefore
neither performance nor residual changes identify a causal PIC version effect.

The ten old prompts were scheduled unchanged: status INCOMPLETE,
9 actual calls. Their
current observed compact B checks show accepted
2/2, workflow usable
2/2,
operationally usable
0/2 and
settled 0/2.
The other 8 planned B
diagnostics are unavailable and remain unknown. Independent
success and false-completion labels for these subjective historical tasks are
null. They are not counted as correct or failed tasks. Only the first two tasks
finished without truncation. The third task's initial and both revisions reached
the 768-token ceiling, triggering the fixed three-consecutive-failure rule after
its B revision. That final B diagnosis was not run. Tasks 004-010 and their 21
generations were not run. This panel is incomplete and cannot support an
across-ten-task diagnostic comparison. No token limit was raised or rerun made.
Original configurations,
tasks, lockfile, project metadata and reports preserved: True.

## 11. Negative and inconclusive findings

No incremental task success benefit was observed. No measured false-completion reduction was demonstrated, and
general PIC persistence did not demonstrate added task sensitive resolution.
The pilot ceiling did not transfer to confirmation: strict initial success was
only 2/12 and substantive decision errors were present. PIC added prompt
tokens and process overhead; equal model-call counts did not equalize cost.
The frozen primary endpoints supply no positive incremental evidence in this
setting. A post hoc one-task difference under notation normalization is
exploratory. Neither analysis proves general ineffectiveness or establishes
validated practical efficacy.

## 12. Threats to validity and full attempt ledger

Small authored sample; family dependence; one locally packaged model; fixed
synthetic records; strict structured evidence grading; one deterministic seed;
one revision; explicit abstention instructions; no authentic external agent
actions, browsing or verifier execution; an unrepresentative ceiling pilot;
ambiguous citation notation and required sets that are not always minimal;
non-isolated caches, load state and background CPU activity. A lightweight
generic checker may not represent a fully integrated PIC verifier workflow.
An immutable protocol prevents outcome-driven selection but does not establish
benchmark validity or adequate statistical power.

| Panel | Status | Tasks planned | Calls attempted | Panel wall seconds |
| --- | --- | ---: | ---: | ---: |
| pilot | COMPLETED | 4 | 12 | 172.269 |
| confirmatory | COMPLETED | 12 | 36 | 477.576 |
| historical | INCOMPLETE | 10 | 9 | 358.646 |

Actual model calls: 58 = 1 warmup + scheduled task attempts.
Non-OK scheduled outcomes: 24. Retained planned initial/A/B states
include three truncated answers and 21 not-run generations;
there were no request errors or timeouts. The third historical B diagnosis and
21 not-run answer diagnoses are null, not successful or failed PIC checks.
All raw attempts and schedule entries are retained locally. No unexecuted trial is silently
dropped. Energy and monetary unknowns remain null. H3 unknown cases remain
unknown. Mock tests and static probes are excluded from the inference count.

## 13. Reproducibility and validation

Use [REPRODUCIBILITY_PIC_1_1_0.md](REPRODUCIBILITY_PIC_1_1_0.md).
The hash-locked dependency profile and protocol/source/task identities accompany
the code. The offline analysis reconstructs counts, paired estimates, intervals,
states and measured resources from preserved files without any model calls.
`scripts/reanalyze_pic110_public.py` independently reruns aggregate arithmetic
from the sanitized JSON's task metrics. Regrading requires the private raw
answers or a new local run; publication of hashes alone does not enable it.

Validation at completion is recorded in `PIC_1_1_0_VALIDATION.json`: old and new
unit tests, compile checks, Ruff, type checks, actual CLI parsing, actual short
local warmup, real pilot, schedule and gold-separation checks, source-preservation
checks and public safety audit. Intermediate development failures are retained
in private setup diagnostics; only final passing checks are not substituted for
the actual model experiment. No arbitrary generated code was executed.

## 14. Interpretation and future external validation

**Q1. What diagnostic problems did 1.1.0 resolve relative to the old interface?**
The inspected compact API explicitly separates routing usability from
operational usability and settlement. The new adapter preserves missing fields,
counts and certification as null and reads unresolved obligations from the
current check/intake locations. It avoids the legacy parser's missing-to-false
or missing-cost-to-zero behavior. This is an interface/harness improvement;
no controlled version comparison proves that semantic diagnosis improved.

**Q2. Did independent task success improve over ordinary review?**
Observed A 2/12 versus B 2/12,
difference 0.0 pp,
95% CI [-30.6, 30.6] pp. No incremental task success benefit was observed.
Measurement validity and small sample size preclude equivalence or efficacy claims.

**Q3. Did false completion decline?**
A 5/12
versus B 5/12.
There was no reduction under the fixed endpoint. Three labels per arm are
contract failures despite the intended decision; two are substantive decision
errors. The paired interval is
[-30.6, 30.6] pp.

**Q4. Were unresolved issues accurately preserved?**
PIC's general labels persisted without observed disappearance. Required task
obligations on all five incomplete tasks were retained by both arms; PIC labels did not represent
the specific missing task evidence. General residual persistence alone does
not establish task sensitive H5 superiority.

**Q5. Is there benefit after PIC's added costs?**
No incremental independently verified benefit was demonstrated at these measured
costs. Allocated B cost was 3.62 times A in measured seconds and
2.51 times A in tokens. These conditional local timings cannot
be generalized to a matched time-to-success frontier, monetary return or
certified acceleration.

**Q6. What remains unproven?**
Generalization to harder externally designed tasks, real tool-using agents,
task bound evidence adapters, multiple models/seeds, iterative workflows and
actual reductions in false completion. A future separately preregistered
external benchmark needs prospective oracle validation, unambiguous source-ID
format and truly minimal evidence sets, genuine baseline errors and independent
verifier evidence. It should compare equal token/time budgets without tuning on this
run. Practical efficacy remains unsupported here; no universal Go/No-Go or ASI
conclusion follows.
