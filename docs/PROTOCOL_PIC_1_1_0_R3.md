# PIC 1.1.0 R3: evidence-bound closed-loop protocol

Date: 2026-10-20, Asia/Tokyo. This is a new locally preregistered experiment.
The baseline is main `ca788ca800b58b00995e056ecde05b389e18077c`. All 1,832
existing tracked/raw/archive files are protected by byte SHA-256 before code
changes. R2 and earlier sources, settings, reports, results and private archives
are not amended. No external network access, publication or model download is
part of R3. Loopback Ollama is the only inference service.

## Questions, hypotheses and scope

RQ1 asks whether independently acquired evidence improves outcomes over generic
review. RQ2, the primary causal contrast, asks whether PIC adds value beyond
the same verifier and a competent generic evidence ledger. RQ3 concerns false
completion and final promotion. RQ4 concerns valid evidence reuse and cost.
RQ5 concerns missing, invalid, stale, conflicting and incompatible evidence.
Hypotheses concern finite synthetic outcomes, not ASI or collective intelligence.

The PIC contrast C-B adds explicit native semantic calls, evidence resolutions,
hooks, packet promotion and runtime feedback to the same evidence receipt.
This combined intervention cannot separately identify effects of each PIC
component or distinguish an information-format effect from extra prompt cost.
B-A adds both evidence acquisition and its management; it is not a change in
intrinsic model reasoning. A has no authoritative observations. An unsupported
guess is not an independently verified completion even when its label is right.

## Phase 0 identities and capability boundary

Use the unchanged `.venv-pic110`, Python 3.14.7, Ollama 0.35.0, PIC 1.1.0,
and non-editable official wheel SHA-256
`2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7`.
All 617 installed wheel payload files match that wheel; their aggregate
JSON-map SHA-256 is
`c317caa37d63f5769d813785711dcc537be0ca4afddd110dc7375863497f0794`.
Model: `gemma4:e4b`, digest
`dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`,
7.5B GGUF Q4_K_M. Its reported parent is a local validation package; vendor
authenticity is not independently established. No substitutions or updates.
CPU: AMD Ryzen 7 8840HS, 8 cores/16 threads, RAM 66,363,183,104 bytes, Radeon
780M. Record actual Ollama allocation rather than inferring GPU use from the
adapter name. Energy, continuous GPU usage, FLOPs and monetary cost remain null.

The actual installed wheel, SDK signatures, schemas, sources and CLI help were
inspected before code changes. No upstream main feature is assumed present.
The [integration record](PIC_1_1_0_R3_INTEGRATION.json) includes actual calls,
ten adversarial cases and the capability matrix. No mock is used in that gate.

Native numerical/calibration/trace/archive functions perform finite predicates.
`resolve_adapter_route` does not invoke them: evidence verification/discharge
checks metadata and content hashes. A route can accept and discharge a declared
obligation despite semantic noncompliance or an attacker-rehashed artifact.
Packet promotion checks expiration but its receiver policy only requires a
nonempty receiver list. Trusted authority, exact recipient, task scope and
envelope TTL require the common external gate. A hash is not issuer identity.
An explicit orchestrator selects routes and binds conclusions to obligations.

Envelope validation uses the production content-reference policy. Packet
promotion and the full runtime use the explicit development identity profile;
no signatures, production identity attestation or full framework settlement
are invented. These settings apply to the finite integration only. The native
function's local `settled`, route `finite_scope_usable`, packet usability and
global runtime `operationally_usable`/`settled` are separate observations.

## Four separated layers and isolation

1. Authoritative source objects, delivered variants, and a pinned trusted
   provenance manifest are separate deterministic artifacts. Synthetic source
   values are read-only during the campaign. The trusted manifest predates
   inference and pins content, issuer, scope and permitted task IDs.
2. A standard-library verifier checks actual content bytes, pinned digest,
   issuer, source ID, task/scope, receiver, validity window, schema, finite
   numbers, observations and conflicts. A confirmed violation is sufficient
   evidence for NONCOMPLIANT. Missing/untrusted/conflicting data gives UNKNOWN.
3. C explicitly calls real PIC native predicates, raw envelope resolution and
   discharge, protected evidence resolution, packet promotion and runtime
   steps. Save raw and protected results separately. Native rejection of a
   compliance predicate is not necessarily failure to determine noncompliance.
   The common external gate supplies the trusted finite-conclusion boundary.
4. The independent oracle separately validates source/provenance and computes
   exact rational differences and indexed event equality. It never adopts a
   verifier/PIC verdict as gold. Hand-calculated outcomes, boundary, negative
   and metamorphic tests check independent implementations before inference.

Private gold is saved under ignored R3 setup and hashed before inference. The
runner never reads gold or imports the oracle. Models receive only public
specifications and their authorized review material; neither model nor PIC
has a filesystem tool or live connector. A PIC artifact holds the same source
facts that B receives, with actual local content references confined to private
raw records. No shell/model-generated code or external site action executes.

## Fixed fresh task set

Pilot: one task per family. Confirmation: four per family, sixteen total.
IDs `r3_numerical_01..04`, `r3_telemetry_01..04`, `r3_trace_01..04`,
`r3_reuse_01..04` are disjoint from R2. All twenty are fixed before pilot.

| Family | Confirmatory cases 01 / 02 / 03 / 04 |
| --- | --- |
| Numerical | Within bound / proved violation / missing / modified then rehashed |
| Telemetry | Boundary pass / proved violation / missing / conflicting observations |
| Trace | Exact match / order violation / missing / unknown source identity |
| Provenance/reuse | Valid reuse of a proved negative / expired / hash mismatch / receiver mismatch |

There are seven determinable confirmatory cases (three compliant, four proved
noncompliant) and nine that require holding. The provenance family's valid
case deliberately reuses a negative determination: proving a violation is a
completed task. Its pilot demonstrates compliant reuse. The ten-case integration
suite supplies additional swap/missing/self-claim counterexamples without
expanding the sixteen-task confirmatory sample. Cases are purposive, not random
samples from real workloads. No pilot effect can change their selection.

Public task specifications contain rules, bounds, IDs, scope, recipient and an
explicitly untrusted constant draft claim; they do not reveal measured values,
delivery state or gold. Source objects and delivery fixtures are separate from
public prompts. The model cannot query either file. Public source publication
later does not imply that source values were visible to A during inference.

## Arms, prompts and final gates

One common initial answer is copied byte-for-byte to A/B/C; one revision per
arm. A gets a fixed generic checklist without verifier observations. B gets
the actual independent receipt (facts, decision, reasons, unresolved IDs and
evidence ID) and a typed, context-aware generic ledger. C receives exactly
the same receipt plus a frozen compact selection of actual PIC fields. Receipt
timings/cache counters are excluded from model input in both B/C. No gold,
manual advice, extra model call or different verifier response is supplied to C.

All outputs have decision, boolean complete, evidence and unresolved fields.
Definite results use COMPLIANT or NONCOMPLIANT, complete=true, the received
receipt ID and no unresolved obligation. UNKNOWN uses complete=false and the
declared evidence obligation; it permits an empty citation list or the received
status receipt. Bare IDs, whitespace and one enclosing bracket pair denote
the same citation; canonical notation is reported separately. Unknown IDs and
invented observations never establish proof. JSON fences are parsed as in R2;
duplicate keys, nonfinite JSON and extra prose are rejected.

A's final gate is only a schema-level admission of its declaration. It has no
evidence certification and is labeled as such. B's final gate requires a real
trusted/sufficient receipt, matching decision, complete flag, citations and
obligations. C applies the same checks plus actual protected PIC readiness.
Raw PIC acceptance/promotion is reported before this common outer protection.
No protection implemented by the outer gate is attributed to PIC alone. All
C final answers also enter the real runtime with the protected envelope and
candidate; that global report does not replace independent grading.

## Producer/consumer and cache experiment

Producer/consumer are logical roles in one process, not autonomous agents.
They have distinct task IDs and obligation/receipt IDs; the pinned authority
explicitly grants both tasks access to the shared source and scope.
For each reuse task, produce the canonical source determination, then check
the delivered consumer artifact. An explicit prior-date validity query models
the archived producer; it is not a claim that an agent actually ran then.
PIC's native expiration still uses actual wall time and can reject an already
expired producer packet. Consumer validity is fixed at 2026-10-20 00:00 UTC.
Far-future/currently-expired fixtures avoid wall-clock boundary races.

B's cache key binds source/digest, parameters and scope. Every lookup rechecks
current pinned digest, issuer, permitted task, recipient and TTL. C reuses the
same receipt; when valid it also reuses recorded native checks and links the
actual producer verified packet as a dependency. PIC does not independently
prove that dependency's domain semantics or exact receiving context. Invalid
cache entries do not suppress current verification failures or renew TTL.

For reuse consumers, execute a real no-cache independent check and a real
no-cache PIC path as deterministic comparators, with no extra LLM call. Save
valid hits, skipped domain/native calls, packet references, false admissions,
correct post-reuse outcomes, verification timings and no-cache timings.
Do not infer time savings merely from fewer calls: these predicates are cheap,
timings have one observation per case and lookup overhead can exceed savings.

## Endpoints and denominators

Primary contrasts are C-B, confirmation only. B-A is secondary. Report:

- Independently verified success: correct finite/epistemic decision, boolean
  flag, sufficient authorized citation and exact obligation set, with a valid
  schema and OK generation. A's label guess cannot substitute for an acquired
  receipt. Correct holding can succeed without acquiring absent evidence.
- Unsupported model completion: explicit true flag despite a wrong decision,
  intrinsically insufficient/conflicting evidence, wrong obligations or no
  access to verified evidence. Citation-only failure with otherwise adequate
  B/C observations is separate. Unknown flags are missing, not zero.
- Supported completion yield: correctly supported results admitted by the final
  gate divided by the seven determinable tasks. This prevents universal holding
  from being scored as useful supported output. Confirmed violations count.

Also report false completions passing the gate, correct holding, format and
citation compliance, lost obligations, native semantic calls, metadata-only
acceptance, verified reuse, invalid raw/protected promotions, failures and all
costs. Success uses all sixteen planned pairs; missing/error/truncated outputs
fail success and yield. For false completion report observed and unknown
denominators, paired observable cases and planned-pair best/worst bounds.
Never drop failures or substitute an endpoint after observing outcomes.

## Schedule, model limits and stopping

Fixed seed 11032026 shuffles tasks within each panel. Two balanced Latin
triplets of arm permutations are randomized internally and cycled. With 16
and 4 not divisible by 6, each arm/position
count differs by at most one. Save the entire schedule before inference.
Producer preparation precedes its consumer, independent of arm order.

All calls: identical model/digest; temperature=0, top_p=1, seed=20261020,
num_ctx=16384, num_predict=768, think=false, keep_alive=10m. No history crosses
arms. Actual prompt tokens/time and cache effects differ and are measured;
there is no assertion of equal realized compute. Prefix/background load is
not experimentally isolated.

Planned task generations: 80 (20 common initials plus 60 revisions). One
64-token real warmup is separate and counted: maximum 81 total attempts.
No retries or reserve attempts. Prompt cap 14,000 UTF-8 bytes, input token
reservation 1,134,032, output reservation 61,504. Oversize prompts are not
truncated. Per-generation read timeout 180 s, connection timeout 10 s.
One-hour campaign clock begins at pilot and includes between-panel work;
warmup/load cost is reported separately. Stop before a new request if a
full timeout cannot fit remaining time, resource reservation would overflow,
RAM exceeds 92%, model/frozen/PIC identity changes, or three consecutive
ERROR/TIMEOUT/EMPTY/TRUNCATED attempts occur. Retain every planned slot,
attempt and failure. The final answer already returned is still recorded.

CLI integration calls have 30 s limits; SDK operations are local bounded finite
fixtures. Native data sizes are tiny and fixed, with no arbitrary code/route
selection from model text. A missing model gives ENVIRONMENT_BLOCKED; an
unfinished campaign is INCOMPLETE; failed required integration is
INTEGRATION_BLOCKED. No emulation fills an unsupported feature.

## Analysis, costs and decision rules

Task is the paired unit. Report numerators/denominators, wins/ties/losses,
risk differences, Wilson arm intervals, conservative paired 95% intervals
from Bonferroni 97.5% Clopper-Pearson discordance intervals, exact two-sided
McNemar and 20,000 paired bootstrap replicates (seed 11032027). Use whole-family
bootstrap (20,000, seed 11032028) as a descriptive dependence sensitivity.
Each confirmatory task has a distinct source group; its producer is not another
independent outcome row. Four related families and authored fixtures limit
all population claims. A degenerate bootstrap interval is not equivalence.

Allocated model cost: one third common initial plus the arm's revision. Split
the one actually shared verifier/producer cost equally between B and C.
C additionally pays producer/consumer/final PIC operations. The separate
no-cache comparator and integration tests are observational overhead. Also
report actual campaign/panel wall time, total actual tokens, verifier/PIC calls,
cache metadata, same-task joint-success costs and missing timing coverage.
Allocated sums omit orchestration/I/O and do not equal physical campaign wall
time. No energy or financial saving is inferred from token/call counts.

Use SUPPORTED only if the conservative C-B success interval excludes zero
favorably or the unsupported-completion interval excludes zero favorably,
with no contrary yield/safety observation. This is endpoint evidence, not a
joint multiplicity-adjusted discovery or a resource-efficiency certificate.
Use HARM_OBSERVED for observed C degradation on success, unsafe promotion or
supported yield (state uncertainty); NOT_DEMONSTRATED for completed but
unsupported improvement; INCONCLUSIVE for missing data/insufficient precision;
INTEGRATION_BLOCKED if the required actual connection fails. Extra cost counts
against a practical utility claim. Statistical non-significance never proves
equivalence. No task additions, exclusions, stopping extensions or scoring
changes respond to effect size.

## Execution and preservation

First run real deterministic integration and all tests; freeze code, tasks,
sources, private gold, provenance, schema, prompts, schedule, endpoints,
analysis, limits, integration results, protocol and reproduction instructions.
Commit locally before warmup/pilot. Pilot tests only technical transmission,
identity, source/gold isolation and feasibility. Its results are excluded from
the main estimates. Record any unavoidable technical amendment and never
overwrite a failed attempt; incompatible changes require a separate experiment.
Freeze/commit main before confirmatory inference, with identical methods if
pilot has no technical defect. Reanalyze saved data without model calls.
Check byte preservation at registration and end; report any later README
navigation edits separately. No push, merge or release is authorized by R3.
