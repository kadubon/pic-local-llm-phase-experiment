# PIC 1.1.0 R4: mechanism isolation without changing PIC

This new experiment follows R3. Baseline is main
`b5275dff85d0c73024e0995d0b273d72f27795c0`. PIC source, installed distribution,
model weights and all prior tracked/raw/archive files remain unchanged.
The pre-code snapshot protects 2,884 available files. No result is pooled with
R1/R2/R3. No cloud inference, external lookup, installation, model download or
PIC update occurs during the campaign.

## Questions and interventions

R3 changed backend processing and feedback representation together. R4 asks:

1. Holding the exact model prompt and answer fixed, does PIC change protected
   admission, supported yield or verification overhead relative to a strong
   generic ledger implementing the same proof/trust policy?
2. Holding acquired receipt facts and PIC backend fixed, does detailed native
   PIC feedback change evidence-supported decisions relative to a minimal
   task facing summary?
3. With real verification work and separate producer/consumer processes, when
   does reuse reduce end-to-end cost, and is it better than generic caching?

Conditions are G_minimal, P_minimal and P_full. There are only TWO model calls
per case: the minimal answer is replayed to generic and PIC gates. This removes
model randomness from the backend comparison and does not create independent
samples. P_full contains the exact same minimal receipt object plus actual PIC
resolution/native-check/runtime/packet detail, using the frozen R3 formatter.
It has no extra authoritative observations. This tests a feedback package,
including auxiliary runtime information and length, not pure wording or token
length. No padding or deliberately weakened generic control is used.

The generic gate already implements the required proof rule. Backend parity
under these rules is a conformance observation, not evidence of equivalence
over arbitrary tasks. The experiment does not assume PIC can improve a fully
specified deterministic predicate. Its potential contribution must be located
in admission behavior, feedback effects, reuse or costs and bounded accordingly.

## Fixed environment and budgets

Use the unchanged isolated Python 3.14 environment, PIC noneditable 1.1.0
wheel SHA256 `2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7`,
617 matching installed payload files, and local `gemma4:e4b` digest
`dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`.
Identity checks occur before/after execution. This does not authenticate vendor
model provenance. Settings: temperature 0, top_p 1, seed 20261020, context 16384,
output cap 768, think false, keep_alive 10m; no retries.

Four pilot and 32 main cases yield 72 task generations plus one 64-token
warmup: maximum 73 calls, 1,752,032 input-token reservations and 55,360 output
token reservations. Maximum prompt is 24,000 UTF-8 bytes, with no truncation.
The same allowed limits apply to both feedback variants. One-hour inference
clock starts at pilot and includes between-panel work; warmup is separate.
Timeout is 180 seconds. Stop before a call if its full timeout or reservation
cannot fit, RAM exceeds 92%, identities/hashes change, or three consecutive
attempts fail. Every planned row remains in denominators after stopping.
Panels and warmup refuse overwriting or automatic resume. Realized tokens and
time may differ; equal caps do not imply equal compute.
The observed input count is checked against context minus the output reservation;
an exhausted boundary is retained as a failed attempt and stops further calls.
Missing token metadata remains unknown. Preflight measures all actual prompt
byte lengths without generating model text.

Reuse has a separate 1,200-second clock, at most 72 child processes and a
90-second timeout each, no retries. All attempts and incomplete grid cells are
retained. No model calls occur in the reuse benchmark.

## Fresh sources and task contract

Eight confirmatory episodes each contain four ordered context snapshots and
three independent source predicates: numerical bound, telemetry tolerance and
exact event trace. A separate four-step pilot episode is excluded from primary
estimates. Main has 23 determinable and nine holding cases, including nine
positive and fourteen negative determinations, fixed by independent hand tests.

Each task asks whether ALL THREE predicates hold. All PASS observations are
needed for COMPLIANT. Any single verified FAIL is a sufficient NONCOMPLIANT
witness, even if other sources are absent. Without a FAIL, any UNKNOWN prevents
a definite result. Receipts give per-source verdicts, never the aggregate
answer. True negative determinations count as complete supported outcomes.

Snapshots cover initial states, one missing source, recipient/scope/TTL/task
grant failures, rehashed unauthorized replacement, changed source data,
changed verification parameters, contradictory telemetry and recovery through
new valid source versions. Each snapshot is a synthetic policy context at fixed
as_of `2026-10-20T00:00:00+00:00`, not an assertion of past execution or elapsed
real-world expiry. Cache state flows through ordered steps within each episode.
Episodes are shuffled. Minimal/full first-position counts are balanced at each
main step across episodes; no conversation history crosses cases or arms.

Source observations, delivery faults and pinned trust manifests are distinct
fields. Independent exact-rational/event-index gold is prepared privately and
hashed; model prompts and normal PIC inputs never receive it. The runner hashes
opaque gold bytes for freeze integrity but never parses gold. The independent
oracle, hand outcomes, boundary and metamorphic tests are fixed before inference.

## Backend and scope

Reuse the exact frozen R3 independent verifier and actual PIC adapter without
modifying either. PIC executes real numerical, telemetry and trace functions,
content-reference envelope resolution, task obligation hooks, packet promotion
and runtime. A final merged runtime receives each actual model answer.
Mappings from tasks to routes are orchestrator-selected, not discovered by PIC.

Both workflows recheck pinned source digest, issuer, task grants, scope,
recipient and TTL on every cache lookup. The generic cache binds source/digest,
parameters and scope. PIC shares that verified receipt and may reuse the real
cached native check and producer packet reference, but still runs route,
promotion and runtime processing. An agreement failure in the unchanged adapter
is recorded as an integration failure; it is not repaired with fabricated output.

Raw resolution, protected task readiness and global runtime state are separate.
Envelope profile is production content-reference validation; packet/runtime
identity uses development policy. This does not test cryptographic issuer
authentication, production identity bypass, autonomous agents or external truth.
Common external gates remain common: their protection is not attributed to PIC.

## Endpoints and analysis

Primary: P_full minus P_minimal evidence-supported success over all 32 planned
main pairs. Success requires valid schema, correct aggregate decision and boolean
flag, and sufficient authorized evidence. Canonical obligation-ID adherence is
a SECONDARY contract endpoint, so free-text uncertainty is not silently scored
as a substantive reasoning failure. Output schema and normalization rules are
frozen in the task prompt. Invalid references, absent proof, wrong decisions,
lost/extra obligations, unsupported completion and gate unsafe admission are
reported separately. Missing or untyped flags are unknown, not safe zeros.

Supported yield is correct, sufficiently supported results actually admitted
divided by the fixed 23 determinable main cases. Complete declarations need
empty unresolved arrays at the gate. A holding answer can succeed without a
definite admission. Gate probes use acquired actual PIC states with canonical
correct declarations, alternative decisions, empty/all/draft references. They
are deterministic conformance probes, not additional independent task samples.

Eight episodes, not 32 snapshots, are the primary independent blocks under the
working model. Report per-episode mean differences, all 256 sign flips with a
two-sided p value under blockwise null exchangeability, and 20,000 whole-episode
bootstrap replicates (seed 11042027). The bootstrap interval is descriptive with
only eight authored blocks. A degenerate interval does not establish equivalence.
The prior task independent paired exact interval/McNemar procedure is reported
only as a sensitivity analysis (seed 11042028). No population or joint
multiplicity-adjusted superiority claim is made from secondary endpoints.

Interpret a positive primary point effect with favorable episode interval and
sign-flip p<=0.05, without contrary unsafe admission or supported yield, as
support on these authored episodes only. Otherwise report unchanged, observed
decline, or uncertain point improvement with its uncertainty; never rename
an endpoint or extend sampling in response to results. An incomplete run remains
incomplete, not a negative efficacy finding.

## Reuse and resources

Real telemetry arrays have 16, 4,096 or 65,536 samples. Fanout is 1 or 8,
with two repeats per cell for generic/PIC and cached/no-cache. No sleeps or
synthetic delays stand in for verification. A fresh producer process persists
its actual cache/native result; fresh consumer processes load a parent-pinned
record and recheck current authority. Producer is a distinct task/receipt ID.
Each consumer repeats the declared workload in one process. This is cross-process
reuse with fixed roles, not independent agent coordination.

The fixed randomized grid has 24 backend/cell/repeat conditions: one producer
and two consumer processes each. Both cached and no-cache totals include the
same producer cost. Parent wall time includes interpreter startup and persisted
I/O; worker core time is reported separately. Compare PIC with its own no-cache
path and separately with the generic cache. Two repeats cannot support a robust
general break-even threshold. All correctness, domain/native call counts and
packet dependency references are retained.

For inference, record actual physical attempts, tokens and panel wall time.
Standalone workflow estimates assign the full shared minimal generation to
each hypothetical backend; do not sum them as physical campaign compute.
Shared evidence acquisition is measured once; P variants share the actual
PIC setup and receive separate final runtime calls. Energy, continuous GPU
utilization, FLOPs, money, engineering effort and auditability benefit are unknown.

## Registration, preservation and reporting

Freeze code, tests, protocol, reproduction guide, fixtures, private gold,
schedule, settings and preservation/installed-PIC maps; commit before warmup
and pilot. Pilot gate is technical only (transmission, parsing, budget,
runtime/artifact recording), without inspecting effect scores to select methods.
Freeze/commit unchanged main before confirmatory inference. Any incompatible
method amendment requires a separately named experiment and retained failures.

All existing files remain byte-identical; new documentation is separate from
R3 and prior publication. Do not overwrite old summaries, validations or raw
archives. Save raw requests/responses/PIC records privately; publish sanitized
rows, identities and model-free arithmetic. Local commits are not independently
public timestamped preregistration. No PIC source modifications or package
release are part of this experiment.
