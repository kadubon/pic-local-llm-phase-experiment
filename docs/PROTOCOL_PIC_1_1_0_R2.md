# PIC 1.1.0 R2: prospective semantic and evidence comparison

Protocol date: 2026-10-20 (Asia/Tokyo). R2 is a new experiment, not an amendment
or rescore of the earlier run. All previous tracked files, raw artifacts and
the private archive are protected by a 957-file byte-hash manifest. R2 writes
only new filenames and `results/pic110r2/`. No historical trial is resumed.

## Motivation and fixed hypotheses

The previous oracle conflated bracketed citation notation, integer strings and
overinclusive evidence requirements with substantive task failure. R2 fixes
those measurement problems prospectively. H1 concerns machine-readable PIC
diagnostics; H2 concerns independent success; H3 concerns substantive false
completion; H4 concerns resource cost; H5 concerns preservation of unresolved
task obligations. Structured PIC acceptance alone establishes none of H2-H5.
No ASI, collective-intelligence or external-world acceleration claim is tested.

## Exact identities and allowed resources

Reuse the existing independent `.venv-pic110` and unchanged hash-locked
`configs/requirements.pic110.lock`. PIC is non-editable 1.1.0, wheel SHA-256
`2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7`.
No dependency, PIC source, Ollama model or system permission is changed.
The model is exactly `gemma4:e4b`, digest
`dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`,
7.5B GGUF Q4_K_M, Ollama 0.35.0. Identity is checked before each generation.
The installed package has a local validation parent name; vendor authenticity
is not independently certified. No download, cloud API or external search is
used during the experiment. Only loopback Ollama receives model prompts.

CPU: AMD Ryzen 7 8840HS, 8 cores / 16 threads; RAM 66,363,183,104 bytes;
Radeon 780M integrated graphics. GPU allocation is observed via Ollama, not
inferred from nominal adapter RAM. CPU/RAM snapshots, raw token counts, model
load/prefill/generation timings and cache counters are retained. Continuous GPU
utilization, joules, FLOPs and monetary cost are unknown, never zero.

All task calls, both arms: temperature 0, top_p 1, seed 20261020,
num_ctx 16384, num_predict 768, think=false, keep_alive=10m, one revision.
These are the previous run's task inference settings. No model history is
shared between arms. Prefix caching is not experimentally isolated.

## Fresh dataset and prospective proof audit

Four pilot tasks: r2_pilot_integration, r2_pilot_policy, r2_pilot_evidence,
r2_pilot_validation. Sixteen confirmatory tasks: r2_integrate_01 through 04,
r2_policy_01 through 04, r2_evidence_01 through 04 and r2_validate_01 through 04.
Each family has four confirmatory tasks. All twenty tasks, their inputs,
oracles, proof audit and prompts are fixed before pilot inference. IDs and
prompts are disjoint from the earlier task set. Pilot results are excluded
from primary estimates; no task is substituted based on pilot outcomes.

Tasks cover arithmetic with conditional/duplicate records; effective-date
policies; absent/unsigned/conflicting evidence; and typed row/JSON/checksum
validation. Five confirmatory cases explicitly require an unresolved answer;
eleven permit a definite determination. These are synthetic closed-record
problems, not real approvals or external verifier actions.

Every task supplies a fixed rule, finite variable domains and authoritative
source facts with bare ID fields such as E01. Background rules and domain
definitions are axioms; they never require source citations. An explicit
availability ledger is evidence of a missing record, rather than an invented
observation of the unavailable artifact. Conflicting reports are separate
observed variables; disagreement has an explicit abstention rule, without
logical explosion from inconsistent axioms.

The independent finite-world solver enumerates every assignment consistent
with the public domains. It computes the decision, completion flag and
unresolved obligation set under the public rule. Full supplied records must
determine exactly one such epistemic result. It enumerates all source subsets
and retains every inclusion-minimal subset for which all compatible worlds
have that same result. For each member of a minimum proof, removing it must
admit a concrete world with a different result; deletion counterexamples are
saved in `tasks/pic110r2/proof_audit.json` before inference. This proves
sufficiency and necessity relative to the declared finite domain. It is not
a proof of unrestricted real-world necessity or external truth.

Inactive policies, unreceived shipment quantities and irrelevant local claims
are not mandatory evidence. Redundant mirror records can form alternative
minimum proofs. Answers may cite a proof or any superset of known records;
they need not find a minimum proof themselves. A metamorphic test adds an
irrelevant source and requires unchanged minima. Hand-calculated expected
answers separately check all twenty rule evaluations. This reduces tautological
testing but is not an independent human benchmark audit.

## Output interpretation and independent endpoints

Every prompt explicitly requests four fields: decision, complete, evidence,
unresolved. It specifies the decision type and the exact unresolved IDs in
the rule. Row answers are label arrays, not row objects. Complete must be a
JSON boolean. The whole JSON may be wrapped in one Markdown JSON fence;
duplicate object keys, non-finite numbers and trailing prose are rejected.

Predeclared semantic equivalences, applied identically to both arms:

- A bare source ID, surrounding whitespace, or one pair of square brackets
  around that same known ID refer to the identical record. Unknown IDs fail
  evidentiary support; no fuzzy matching or invented-source repair is allowed.
- For integer decisions only, a canonical decimal integer string has the same
  semantic value as that integer. Actual JSON integers are explicitly requested;
  boolean values are never integers. Type compliance is separately reported.
- Row-label and obligation arrays denote sets. Row labels are canonically
  sorted/deduplicated for semantic grading; canonical array/type compliance is
  reported separately. No case folding or synonym matching is performed.

Primary endpoints, confirmatory tasks only:

1. **Semantically verified task success**: decision matches the independent
   oracle, complete equals the expected boolean, unresolved obligations match,
   and cited known records contain at least one proved sufficient set. The
   generation must have status OK. Denominator is all sixteen planned tasks;
   missing, failed, truncated and uninterpretable outputs are unsuccessful.
2. **Substantive false completion**: explicit complete=true with a wrong
   semantic decision, intrinsically incomplete/conflicting evidence, or
   incorrect unresolved-obligation disclosure. Mere omission/notation/type
   variation of citations is not counted as a false factual decision. Missing
   or untyped completion flags remain unknown; report observed denominators,
   paired observable cases and planned-denominator best/worst bounds.

Secondary endpoints: decision correctness without citation requirements;
evidence sufficiency; evidence-incomplete completion (complete=true without a
sufficient citation set); format/type compliance; correct evidence-supported
abstention; obligation preservation; all actual resource and failure metrics.
The two false-completion definitions are not merged. No post hoc normalization
or alternate endpoint is substituted after observing model outputs.

The runner loads only public tasks. Gold and proof-audit files are hashed for
provenance but not parsed or passed to Ollama/PIC. Neither system has filesystem
tools or oracle access. PIC receives candidate answer files only, with live
connectors disabled. Model-generated code and shell text are never executed.
Independent grading occurs after each panel has finished, never during it.

## Matched arms and fairness

One initial generation is shared byte-for-byte. A receives a fixed generic
review checklist, B the actual field selection from PIC 1.1.0 compact check
and intake. The wrapper and original task records are identical. The checklist
and lossless PIC serialization are frozen before the pilot. General PIC
framework obligations are not rewritten into task aware advice. No oracle
information, manual repair, browsing or extra model call is supplied to B.
Final outputs of both arms receive identical PIC diagnostics for comparison.

Order seed 11022026 counterbalances 2/2 pilot and 8/8 confirmatory A-first
versus B-first. Full task order and arm order are saved before inference.
The model-call count, context/output caps, model identity, seed and task access
are equal. Prompt tokens and PIC process overhead can differ and are measured.
This is equality of resource allowances and call counts, not a claim of equal
realized compute/time. No padding is introduced. Any efficiency claim must
include the observed extra input and PIC cost.

## Resource accounting and finite stopping

New campaign: at most 62 actual model attempts, including one 64-token warmup
and sixty scheduled task calls (4 pilot + 16 confirmatory, three calls each).
One unused reserve does not authorize retries. Maximum task prompt UTF-8 bytes:
14000; maximum campaign input reservation: 868000 tokens (a conservative byte
allowance), output reservation 47680 tokens. Maximum task output 768, context
16384. Oversize prompts are not silently truncated.

Campaign wall limit 3600 seconds from pilot start, including between-panel work.
Per-request read timeout 180 seconds plus bounded connection timeout 10 seconds;
PIC timeout 30 seconds per process. Retries: zero. Stop before another model
call at any budget boundary, model/frozen-file identity change, RAM above 92%,
three consecutive ERROR/TIMEOUT/EMPTY/TRUNCATED generations, or interruption.
Retain every scheduled slot and every attempt. Post-answer PIC diagnostics are
retained even if that answer triggers the generation-failure stop. Model-free
diagnostics never count as real inference. Blocked and partial runs remain
ENVIRONMENT_BLOCKED or INCOMPLETE; no favorable-case-only reporting is allowed.

One real warmup checks present viability and throughput before task inference.
Previous comparable measurements suggest this 60-call structured-output design
is feasible within one hour; actual warmup/load estimates are recorded as
estimates, not observed campaign cost or guaranteed completion.

Allocate half the shared initial model time to each arm. A workflow cost adds
its revision and independent grading. B additionally incurs initial and final
PIC check/intake. A's final PIC is separate observational research overhead.
Also report full panel and campaign wall time, actual input/output tokens,
same-task joint-success costs, cache/load effects and missing cost coverage.
Allocated component sums omit orchestration/I/O overhead; full wall time
includes it. Equal maximum calls do not imply equal realized cost.

## Statistics and interpretation

Task is the statistical unit. Pair A/B by task ID. Report successes and
substantive false completions with Wilson 95% intervals; paired B-minus-A
differences, wins/ties/losses, exact McNemar p-values and 20000 paired bootstrap
replicates (seed 11022027). Headline paired 95% intervals use the conservative
Bonferroni construction from two 97.5% Clopper-Pearson discordance intervals.
Degenerate zero-width bootstrap intervals never establish equivalence. H3 uses
only paired observable completion claims; unknown-case bounds are also shown.
Family results (n=4) are descriptive. Family/template dependence and purposive
synthetic sampling constrain population interpretation of all intervals.

Directional H2/H3 support requires the corresponding conservative interval to
exclude zero in the favorable direction; two endpoints are reported without a
joint multiplicity-adjusted discovery claim. No improvement, harm, ceiling,
floor or low precision is reported directly. R2 is not pooled with the old run,
and changed tasks/scoring preclude a causal across-run performance comparison.

H1 retains all five PIC states separately; absent certification remains null.
H5 distinguishes task obligation preservation from generic PIC label persistence.
No task sensitive diagnosis is inferred merely from stable framework warnings.
Runtime acceleration certification remains unavailable without the real
trajectory/resource measurement contract; demonstration proxy scores are not
observed LLM improvements. Practical value must combine success, false completion
and measured extra cost, with limitations stated rather than forced Go/No-Go.

## Freeze, pilot gate and preservation

Before pilot: syntax/type checks, old and new tests, finite-proof completeness,
positive/negative oracle cases, notation/type tests, matched harness mock,
source/gold separation, old-file hash check and real warmup. A manifest hashes
protocol, task IDs, all inputs/gold/proofs, prompts, runner, oracle, logic,
analysis, reused core modules, tests and dependency lock. Hashes normalize CRLF
to LF for repository portability; raw text/artifact identities are retained
separately. A local preregistration commit precedes main inference.

The four-task pilot gates only technical viability and resource feasibility.
Ceiling/floor or disappointing PIC actionability cannot motivate task, oracle
or prompt selection. Any necessary technical amendment must retain old failures,
record before/after hashes and not pool incompatible runs. No task inference is
performed before its applicable freeze. Existing result bytes are checked again
after the campaign. No push, release, publication or external message is made.
