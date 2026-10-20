# PIC 1.1.0 R2: prospective evidence-oracle experiment

Execution status: **COMPLETED**; confirmatory panel **COMPLETED**.
Run date: 2026-10-20, Asia/Tokyo. Local execution; no external publication.

## Abstract

R2 prospectively repaired the earlier oracle's source-ID/type ambiguity and
overinclusive required evidence sets. Sixteen fresh confirmatory tasks used the
same installed local model, one common initial answer and one revision per arm.
Success was A 8/16, B 9/16; substantive false
completion was A 7/16,
B 6/16.
Success difference B-A: 6.2 pp, conservative 95% CI
[-23.9, 33.8] pp. The paired success interval does not establish incremental superiority.
Allocated measured workflow seconds: A 191.167,
B 479.477. The design tests this finite integration, not
general intelligence, external truth, ASI or universal PIC effectiveness.

## Research question and fixed hypotheses

Does unchanged PIC 1.1.0 add independently verified success or reduce substantive
false completion beyond a fixed generic review? H1 is structured diagnosis;
H2 task success; H3 substantive false completion; H4 measured resource efficiency;
H5 preservation of unresolved obligations. PIC's own acceptance cannot serve as
an independent correctness label. The original run and R2 are not pooled.

## Exact environment and identities

- Model: `gemma4:e4b`, digest
  `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`, 7.5B,
  Q4_K_M, GGUF.
- Reported parent: `gemma4-validation-20260929:e4b-imatrix-attention-q6-q8-draft2`. This is
  an observed local package, not independent vendor authentication.
- PIC 1.1.0, non-editable official wheel SHA-256
  `2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7`. Imported from the isolated environment.
- Ollama 0.35.0; Python `3.14.7 (main, Sep 24 2026, 17:57:14) [MSC v.1944 64 bit (AMD64)]`;
  platform `Windows-11-10.0.26300-SP0`. The unchanged dependency lock was reused.
- CPU AMD Ryzen 7 8840HS, 8 cores/16 threads; RAM 66363183104 bytes;
  Radeon 780M integrated graphics. GPU allocation snapshots are in raw Ollama
  process records. CPU snapshots 10.4-
  60.9%; RAM snapshots
  47.1-49.3%.
  No continuous GPU/energy monitoring was available.
  Observed Ollama size_vram snapshots: [0] bytes;
  this is actual reported allocation, not nominal dedicated VRAM.

No model was downloaded, changed or silently substituted. The prior qwen3.5
reference remains unavailable; this is the same gemma4 digest used in the first
PIC 1.1.0 run. No cloud inference or external lookup was performed.

## Preregistration and pilot gate

Protocol: [PROTOCOL_PIC_1_1_0_R2.md](PROTOCOL_PIC_1_1_0_R2.md).
Pilot/main normalized-LF manifest SHA-256:
`c0ad1c5ee2ff38fc207933686aac8ac2189a6740faa512bae6477d6869abdf5b` /
`da6de40e65bb6957ae163fa2b00260a0438aaf636a669e50a1bb819913aee133`.
The protocol, prompts, tasks, all gold/proof data, evaluator, logic, runner,
analysis and tests were fixed before pilot inference and committed locally.
Main was frozen before any confirmatory inference. Any technical amendments,
if present, are listed in the pilot gate note; no effect-driven task selection
or primary-endpoint change is permitted.

Pilot status COMPLETED; success initial/A/B
2/2/2
out of four each. Pilot is excluded from primary estimates. Warmup returned
3 output tokens in 20.560 s including
load; it is one real call, not a mock or task trial.

## Dataset and independent minimum-proof oracle

Four families, four new confirmatory tasks each; five require explicit unresolved
answers. Public rule/domain/source facts are separate from gold/proof files.
The runner never loads gold for generation, and neither Ollama nor PIC has
filesystem tools. PIC live connectors are disabled. No generated code executes.

Across all twenty new tasks, 59830 finite worlds and 21 minimal
evidence proofs were enumerated before inference. Every proof is sufficient
under all compatible worlds and has a saved different-outcome counterexample
when any member is removed. All alternative minima are retained. Known source
supersets are accepted. Inactive policies, irrelevant quantities and duplicate
mirror context are not made mandatory. Background rules require no citation.
Minimality is relative to the declared domain; it does not prove external truth.

Source IDs use explicit bare id fields. Bare/bracketed/whitespace variants of
known IDs are equivalent prospectively. Integer strings are accepted as semantic
integers, while type compliance is separate; booleans never become integers.
Label arrays denote sets, not objects. No output-driven normalization was added.
Hand-calculated expected decisions, irrelevant-record invariance, alternative
proofs, notation/type examples and negative cases were checked before the pilot.

## Endpoints and matched arms

Primary success requires correct semantic decision, correct complete flag,
preserved obligations and a proved sufficient citation set; non-OK/missing
generations fail success. Primary substantive false completion requires an
explicit true flag with a wrong decision, actual missing/conflicting evidence
or incorrect obligation disclosure. Citation omission alone is a separate
evidence-incomplete-completion endpoint, not a false factual decision.

A receives the fixed generic checklist. B receives unchanged actual selected
compact check/intake fields. Both receive identical original records and shared
initial bytes, the same wrapper, one independent revision call and no extra
tools or oracle feedback. Eight tasks are A-first and eight B-first, fixed seed
11022026. Every task call uses temperature 0, top_p 1, seed 20261020,
context 16384, output cap 768, thinking disabled, timeout 180 s, no retries.
Equal allowances/call counts do not imply equal actual tokens or wall time.

## Primary results and uncertainty

| Endpoint | A | B | B-A | Conservative exact 95% CI |
| --- | ---: | ---: | ---: | --- |
| Semantically verified task success | 8/16 | 9/16 | 6.2 pp | [-23.9, 33.8] pp |
| Substantive false completion | 7/16 | 6/16 | -6.2 pp | [-33.8, 23.9] pp |

Success B wins/ties/losses: 1/15/0.
False-completion B increases/ties/decreases: 0/15/1.
Observed paired H3 denominator 16; unknown completion flags A
0, B 0. Planned-denominator
H3 bounds: A [0.4375, 0.4375], B [0.375, 0.375].
Wilson success intervals: A [0.27999563610326017, 0.7200043638967398], B [0.331785563988119, 0.7690134759450765].
Wilson false-completion intervals: A [0.23098652405492354, 0.6682144360118811], B [0.18481232558863633, 0.6135895945449727].
Exact McNemar p-values: success 1.0,
false completion 1.0. Paired 20000-replicate
bootstrap intervals: success [0.0, 18.8] pp,
false completion [-18.8, 0.0] pp.
Degenerate bootstrap intervals do not prove equivalence. The conservative
intervals and synthetic family dependence limit population interpretation.
These intervals assume independent exchangeable task outcomes; nominal coverage
is not established for a broader population with dependent template clusters.

### Relation to the common initial answers

Initial success was 9/16, with
6 substantive false completions. Initial-to-final
success-label changes were `{"A": [{"final_success": false, "initial_success": true, "task_id": "r2_validate_02"}], "B": []}`.
The sole A/B discordance is r2_validate_02: the initial answer correctly retained all three invalid row labels, A dropped the row with an invalid status, and B retained the correct initial set. The favorable B comparison reflects avoidance of a generic-review regression, not repair of an initially wrong answer.
Initial-to-final improvement/regression counts: `{"A": {"improved": 0, "worsened": 1}, "B": {"improved": 0, "worsened": 0}}`.
This is a descriptive within-task observation, not an added independent sample
or a replacement primary endpoint. No improved diagnostic localization is
inferred from this one preserved answer.

| Task | Order | A success | B success | A substantive false completion | B substantive false completion |
| --- | --- | ---: | ---: | --- | --- |
| r2_integrate_01 | AB | 0 | 0 | True | True |
| r2_integrate_02 | BA | 0 | 0 | True | True |
| r2_integrate_03 | AB | 0 | 0 | True | True |
| r2_integrate_04 | BA | 0 | 0 | True | True |
| r2_policy_01 | AB | 1 | 1 | False | False |
| r2_policy_02 | AB | 1 | 1 | False | False |
| r2_policy_03 | BA | 1 | 1 | False | False |
| r2_policy_04 | AB | 0 | 0 | True | True |
| r2_evidence_01 | BA | 1 | 1 | False | False |
| r2_evidence_02 | AB | 1 | 1 | False | False |
| r2_evidence_03 | AB | 1 | 1 | False | False |
| r2_evidence_04 | BA | 0 | 0 | False | False |
| r2_validate_01 | BA | 0 | 0 | True | True |
| r2_validate_02 | BA | 0 | 1 | True | False |
| r2_validate_03 | BA | 1 | 1 | False | False |
| r2_validate_04 | AB | 1 | 1 | False | False |

| Family | A success | B success | A false completion | B false completion |
| --- | ---: | ---: | ---: | ---: |
| evidence | 3/4 | 3/4 | 0 | 0 |
| integration | 0/4 | 0/4 | 4 | 4 |
| policy | 3/4 | 3/4 | 1 | 1 |
| validation | 2/4 | 3/4 | 2 | 1 |

## Secondary diagnostic results

| Metric | A | B |
| --- | ---: | ---: |
| Semantic decision correct | 8/16 | 9/16 |
| Sufficient cited evidence | 15/16 | 15/16 |
| Format/type compliant | 16/16 | 16/16 |
| Evidence-incomplete completion | 1 | 1 |
| Correct supported abstention | 5/5 | 5/5 |
| Correct task obligation set | 15/16 | 15/16 |

PIC final B check state counts (true/false/unknown), with missing diagnoses
separately counted as 0:
`{"acceleration_metrics_certified": {"False": 0, "None": 16, "True": 0}, "accepted": {"False": 0, "None": 0, "True": 16}, "operationally_usable": {"False": 16, "None": 0, "True": 0}, "settled": {"False": 16, "None": 0, "True": 0}, "workflow_usable": {"False": 0, "None": 0, "True": 16}}`.
Across 60 observed initial/final diagnoses, obligation signatures:
`{('obligation:baseline-safety', 'proxy-target-grounding-proof'): 60}`; residual burden signatures `{'2.02': 60}`.
Generic framework obligations are not automatically task specific missing
evidence. Actual route/action fields remain available in private raw reports.
No independence or usefulness is inferred from their parseability alone.
PIC disappearance tracking is retained separately from independent task
obligations; no new external verifier evidence was produced by either arm.
Exact obligation sets on genuinely unresolved tasks: A 5/
5, B 5/5.
The separate obligation audit distinguishes lost obligations from extra labels;
accuracy of a whole set is not equated with disappearance of a missing fact.
Certification remains unknown/not applicable: the real resource-bound runtime
trajectory contract is absent and no modeled proxy gain is used as observation.

## Resource accounting

| Component | Input tokens | Output tokens | Model seconds | PIC seconds |
| --- | ---: | ---: | ---: | ---: |
| Shared initial | 7580 | 1019 | 134.072 | 50.767 |
| A revision | 10919 | 996 | 124.130 | 50.535 observational |
| B revision | 24815 | 1001 | 311.196 | 50.477 |

Half of initial generation is allocated to each arm; B also pays initial and
final PIC. A's final PIC is measurement overhead. Allocated totals A
191.167 s, B 479.477 s; B/A ratio
2.508. Allocated input+output token totals A 16214.500,
B 30115.500. These component sums omit identity-query/I/O/orchestration
overhead; observed confirmatory panel wall time is 726.440 s.
Joint-success cases 8/16: allocated A/B seconds
100.627/229.592.
Cache/load effects are recorded but not isolated. No claim of equal realized
compute or a time-to-success frontier follows from one matched revision.
Energy/monetary cost is missing. Raw timing/token metadata is retained.
Campaign span including between-panel work: 966.449 seconds, excluding
the earlier warmup. Actual observed input/output tokens across real calls:
54337/3784;
complete token metadata coverage: True; total tokens 58121.
PIC overhead charged to B is the shared-initial diagnosis plus B's final
diagnosis: 101.244 seconds.

## Full attempt ledger, negative and inconclusive outcomes

Actual real calls: 61 including one warmup; planned
task slots 60. Retained states: `{'OK': 60}`.
Pilot and confirmatory logs are separate. Failure/timeout/truncation/not-run
trials are not removed, retried or replaced. Completion status above concerns
execution, not a favorable efficacy result. The paired success interval does not establish incremental superiority.
Any lack of change is distinguished from proof of equivalence. Additional cost
without demonstrated endpoint improvement is not a measured efficiency benefit.
For the success endpoint: The paired success interval does not establish incremental superiority. Format-conformant answer counts are
16/16 and 16/16; surface
normalization usage counts are 0 and
0. These are reported separately rather than
hidden in task success labels. Joint-success and all-task costs above are the
resource comparison, not an inferred acceleration.

## Comparison with the earlier run and preservation

The old strict 2/12 versus 2/12 success and 5/12 versus 5/12 completion labels
remain untouched, along with their oracle-validity audit and incomplete
historical panel. R2's tasks, size, semantic scoring and evidence proofs differ;
across-run changes cannot be attributed to PIC or model improvement. The same
model digest is the controlled identity, not a license to pool distinct trials.
Prior preservation: **PASS**, 957
byte-identical protected files, including old raw data and private archive.

## Threats to validity, reproducibility and interpretation

Finite authored tasks; four shared families; one locally packaged model and
seed; stronger explicit rule/type instructions; no real external actions or
task bound PIC verifiers; finite-domain proof assumptions; small sample; no
cache or background-load isolation; one revision and unequal realized prompt
cost. The evaluator is independent of PIC/LLM but not an independently
institutionally validated benchmark. Prospective repair removes known scoring
artifacts, not every possible measurement or external-validity limitation.

See [REPRODUCIBILITY_PIC_1_1_0_R2.md](REPRODUCIBILITY_PIC_1_1_0_R2.md).
Frozen source/task/proof identities, saved rows, status ledger and validation
are provided with this report. Public arithmetic reanalysis needs only the
sanitized metrics; exact regrading requires private raw outputs or a new run.
The unchanged old experiment remains independently reproducible. No external
push, release or publication is performed.

Q1: prospective source-ID/type equivalence and formally minimized evidence
replace the old measurement artifacts; no PIC version change occurred.
Q2: success A 8/16, B 9/16, difference 6.2 pp,
CI [-23.9, 33.8] pp. The paired success interval does not establish incremental superiority.
Q3: substantive false completion A 7,
B 6, with uncertainty and missingness above.
Q4: task obligation correctness and generic PIC persistence are reported
separately; text repair is not evidence acquisition or verifier settlement.
Q5: assess those endpoints jointly with measured A/B cost ratio 2.508;
no certification or unmeasured cost saving is inferred.
Q6: external validation, multiple seeds/models, real verifier integration and
benefit under a controlled equal-time/token frontier remain unproven.
