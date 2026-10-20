# PIC 1.1.0 preregistered local comparison

Protocol date: 2026-10-20 (Asia/Tokyo). This protocol fixes both the pilot and
confirmatory design before task inference. The final main preregistration is
created after technical pilot checks and committed locally before confirmatory
inference. The protocol file's SHA-256 and all frozen source/data hashes are
stored in the preregistration manifests, not self-embedded in this file.

## Question and hypotheses

Does adding the published PIC checker to one local model revision improve
independently verified task success or reduce unsupported completion relative
to a generic review? H1 concerns stable structured diagnostics; H2 concerns
independent success; H3 concerns unsupported completion; H4 concerns measured
resource efficiency; H5 concerns preservation of unresolved obligations.
H1 alone cannot support H2-H5. None of these tests measures ASI or collective
intelligence. Negative, null, blocked, and incomplete outcomes are retained.

## Versions and environment

Use the non-editable PyPI PIC 1.1.0 wheel, SHA-256
`2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7`.
The isolated environment is `.venv-pic110`; the old setup and configurations
remain available. The imported PIC must be under this environment's prefix.
The pinned dependency profile is `configs/requirements.pic110.lock`.

Ollama 0.35.0 is reachable on loopback. The historical model
`qwen3.5:35b-a3b` is absent. Choose existing `gemma4:e4b` for bounded local
runtime on this machine; no model is downloaded or modified. Its digest is
`dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`,
GGUF, 7.5B, Q4_K_M. Another installed model is `qwen3.6:35b-a3b`; it is
not used. This is not a direct replication of historical model performance.

Observed hardware: AMD Ryzen 7 8840HS, 8 cores / 16 logical CPUs,
66,363,183,104 bytes RAM, Radeon 780M integrated graphics. Windows reports
2,147,483,648 bytes adapter RAM; this is not a measured dedicated VRAM budget.
Actual Ollama GPU allocation, where provided, is recorded separately. GPU
utilization, energy use and financial cost are unavailable and remain null.

One bounded warmup precedes the pilot: 64 output tokens maximum, 180-second
timeout, context 8192, arithmetic JSON prompt. It returned 17 output tokens
and 32 input tokens in 28.194 seconds including 27.012 seconds loading;
generation took 0.626 seconds (about 27.2 tokens/s). The warmed generation-only
projection for 78 calls at 768 output tokens is approximately 2,206 seconds,
excluding prompt processing, loads and diagnostics. This is an estimate, not a
guarantee. A 5,400-second campaign cap allows finite overhead.

## Tasks, inputs and independent oracle

The four pilot task IDs are `pilot_integrate`, `pilot_version`,
`pilot_conflict`, `pilot_validate`. They are excluded from primary estimates.

Panel 2 has twelve fixed task IDs:

| Family | IDs |
| --- | --- |
| integration | integrate_01, integrate_02, integrate_03 |
| versioning | version_01, version_02, version_03 |
| uncertainty | conflict_01, conflict_02, conflict_03 |
| validation | validate_01, validate_02, validate_03 |

Five confirmatory tasks require abstention for unavailable evidence or
unresolved conflict; seven permit a definite decision. All records are
synthetic and self-contained. Version tasks use dates inside their records,
not contemporary real-world legal or regulatory claims. Family reuse limits
statistical independence and external generalization.

`tasks/pic110/public.json` contains only task inputs and source ID metadata.
`tasks/pic110/oracles.json` separately fixes typed decisions, completion status,
minimal evidence sets, allowed evidence IDs and outstanding obligation IDs.
The runner never loads the gold file. Neither Ollama nor PIC is offered a tool
to read it; PIC receives only the candidate answer file and live connectors
are explicitly disabled. No model-generated code or shell text is executed.

The independent evaluator `pic110_oracle.py` imports neither PIC nor any model.
It parses a whole JSON object, optionally one whole Markdown JSON fence.
It rejects duplicate keys, non-finite constants, extra/missing schema keys,
incorrect JSON types (including booleans masquerading as integers), invented
evidence IDs, duplicate evidence/obligation entries and incorrect decisions.
Evidence must contain at least one predeclared minimal supporting set and no
invented source. Unresolved obligation sets must exactly match the oracle.
List-valued decisions must be sorted and exact. Fluency, length, keyword
coverage and PIC acceptance do not determine task success.

Panel 1 uses all ten original YAML task prompts unchanged, in their original
order. It is diagnostic only: those tasks have no new independent gold labels.
Historical heuristic scores cannot be promoted to independent correctness.

## Matched arms and order

Each task has one initial generation and two isolated one-call revisions.
Arm A receives the fixed generic checklist in `pic110_prompts.py`. Arm B
receives actual PIC 1.1.0 report fields from initial `agent check --compact`
and `agent intake`. Selected fields are serialized without inventing,
reinterpreting, translating or replacing obligations. Selection is fixed in
`pic110_adapter.feedback`; full raw reports are saved. Both revision prompts
use the same wrapper and original records, with no conversation history.
Review materials are advisory, not new evidence; general framework obligations
need not be included in a task specific answer. No external sources are fetched.

Both arms use temperature 0, top_p 1, seed 20261020, context 16384, output
limit 768, thinking disabled, keep_alive 10m, and the same exact model digest.
There is no manual repair and no outcome-driven retry. Initial-answer hash
equality must hold. Prompt lengths are allowed to differ; actual input tokens
and cache counters are reported. No artificial padding is used.

Seed 20261020 assigns exactly half of each panel to A-first and half to B-first
using the deterministic `schedule` function: pilot 2/2, confirmatory 6/6,
historical 5/5. Task order is fixed. The complete schedule is saved before any
task inference. Histories are never shared; Ollama's internal prefix cache is
not assumed disabled. Warm loads, timing order and caching limit causal timing
interpretation. Final PIC checks on both arms are observational diagnostics;
the A diagnostics are not shown to either model revision.

## Primary endpoints and missingness

The statistical unit is the task, not calls, tokens or intermediate revisions.
The confirmatory primary endpoints are:

1. Independently verified success: correct typed decision, completion status,
   supporting evidence and unresolved obligations. Denominator is all twelve
   planned tasks per arm; missing, failed or malformed answers are unsuccessful.
2. False completion: explicit `complete=true` when the independent decision,
   required support or obligation disclosure is wrong, or completion is
   intrinsically impossible given missing evidence. This is not PIC accepted.
   A parseable explicit `complete=false` is not a completion claim. Missing,
   unreadable, or untyped completion claims are unknown, not false or zero.
   Report known denominators and planned-denominator best/worst bounds.

H3 estimates use paired tasks with observable completion flags in both arms;
the count of excluded unknown pairs is reported. Success counts always include
the planned denominator. No primary endpoint is changed after observation.

## Secondary analyses

Report initial/final success, valid evidence, correct abstention, task obligation
preservation, PIC obligation identities/counts and residual burden, status
separation, calls, tokens, model wall time, PIC wall time, evaluator time,
resource snapshots, failures, truncations, timeouts and not-run trials.
PIC fields absent or of the wrong type remain null. `accepted`,
`workflow_usable`, `operationally_usable`, `settled` and
`acceleration_metrics_certified` are kept separate. Nested agent-task usability
does not promote the parent report. A missing certification field is unknown.

Track before/after PIC obligation identities per arm. Any disappearance without
new verifier evidence is flagged; unchanged generic obligations establish only
generic persistence. Independently evaluate required task obligation disclosure
in the answer. Manually audit actual PIC labels against source IDs and task
requirements, reporting general warnings, task specific actions, unrelated
framework actions and requirements needing external evidence. This audit is
descriptive, not a post hoc primary score.

Record both check and intake process times (including CLI startup). Arm A's
workflow cost is half the common initial generation plus its revision and
independent grading. Arm B additionally incurs initial and final PIC diagnosis.
A's final PIC measurement is separate research overhead. Also report the
complete measured campaign wall time, which includes both arms and diagnostic
work. Monetary cost and joules are missing, not zero. Compare costs within the
same tasks where both arms achieve success; no claim of matching total cost
follows merely from equal call limits. Equal maximum tokens do not imply equal
actual tokens. A fixed one-round design does not estimate a general
time-to-success frontier or optimal stopping policy.

The runtime compare/certify-acceleration interfaces require actual
RuntimeRunReport trajectories and an evidence-backed resource measurement
contract, including comparability identifiers, resource envelopes and metrics
such as receiver reuse or residual half-life. The generic intake demonstration
state and its modeled proxy numbers are not observed LLM speed measurements.
Do not manufacture RuntimeRunReports or fill missing metrics to obtain a
certificate. Inspect API/schema compatibility and report certification as
unavailable when its contract is not met.

## Statistical methods

Report per-arm successes and false completions with denominators and Wilson
95% binomial intervals. Pair by task ID. Report B-minus-A risk differences,
B wins/ties/losses for success, and increases/ties/decreases for false completion.
Use 20,000 paired task bootstrap replicates, seed 1102026, percentile 95%
intervals. Bootstrap intervals can degenerate with zero discordance; they are
not proof of equivalence. The headline paired interval is a conservative
exact 95% construction: take 97.5% Clopper-Pearson intervals for the two
discordant-cell probabilities, subtract their opposite endpoints and clip to
[-1,1] (Bonferroni coverage). Report exact two-sided McNemar/binomial p-values
as descriptive, with no multiplicity-adjusted discovery claim. Report results
by four families (three tasks each), explicitly descriptive. Shared templates
and source construction constrain inference beyond these twelve tasks.

## Bounds, failures and stopping

The campaign includes at most 80 actual inference attempts (one warmup +
78 scheduled generations + one unused reserve). No retries are allowed.
Reserve at most 14,000 prompt UTF-8 bytes per scheduled request as a conservative
input allowance, 1,120,000 campaign input tokens and 61,440 output tokens;
actual model token counts are separately recorded, never inferred from text
length. A context of 16384 leaves space above prompt and generation bounds.
Requests exceeding the prompt byte limit are not truncated; stop and retain
not-run trials. Maximum scheduled output is 59,904 tokens plus warmup 64.

Campaign wall budget is 5400 seconds from pilot start, including inter-panel
work; one generation timeout is 180 seconds (plus a bounded connection timeout
up to 10 seconds), each PIC process timeout 30 seconds, and maximum consecutive
generation failures is three. Stop before starting a new call if its timeout
would exceed remaining wall budget, if total reservation/call bounds are hit,
if system RAM exceeds 92%, if model identity changes, if a frozen hash changes,
or if manually interrupted. The runner does not stop other Ollama processes,
unload other models, change model weights or alter system permissions.
CPU/RAM are sampled before and after calls; GPU allocation is sampled from
Ollama /api/ps after tasks. These are snapshots, not peak-utilization telemetry.

Every planned initial/A/B attempt receives a retained schedule entry. Requests
and STARTED records are saved before inference; timeout/error/empty/truncated
outcomes are retained without rerun. A failed PIC diagnostic cannot silently
become another intervention. If Ollama is unavailable before real task
inference, report ENVIRONMENT_BLOCKED and perform model-free diagnostics.
Partial panels are INCOMPLETE. Confirmatory goes before historical; pilot
precedes both. Historical runs only within remaining campaign budget.

## Pilot gate and provenance

Before the pilot: compile/type checks, old tests, new parser/oracle/harness
tests, actual check/intake probes and the real warmup. A 4-task pilot checks
nonempty responses, parsing, matched counts, evaluator sensitivity, load and
actionability. Ceiling/floor observations are reported without outcome-driven
task, oracle or prompt changes. A ceiling pilot does not justify selecting
harder confirmatory tasks. Technical repairs must preserve prior failures and
document before/after hashes; incompatible results are not pooled.

Freeze manifests contain task IDs, schedule, config, this protocol, prompts,
adapter, runner, independent evaluator, analysis code, original task files,
public data, gold data and dependency lock hashes. A local commit fixes the
final main protocol before confirmatory generation. Saved run files suffice
for offline analysis. Raw texts, absolute paths and environment records remain
under ignored `results/pic110/`; only safety-audited summaries, manifests,
reports and reproduction instructions are candidates for tracking. No push,
release, package publication or external messaging is authorized.
