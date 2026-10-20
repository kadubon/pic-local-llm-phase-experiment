"""Render R2 evidence and results from saved data; no inference or PIC calls."""

from __future__ import annotations

# Report tables intentionally use long source lines.
# ruff: noqa: E501
import argparse
import json
from collections import Counter
from datetime import datetime

from pic_local_llm_phase_experiment.pic110_runner import read, write
from pic_local_llm_phase_experiment.pic110r2_analysis import summarize
from pic_local_llm_phase_experiment.pic110r2_runner import OUT, ROOT, preservation


def ci(values):
    return "missing" if values is None else f"[{100 * values[0]:.1f}, {100 * values[1]:.1f}] pp"


def number(value):
    return "missing" if value is None else f"{value:.3f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-public", action="store_true")
    args = parser.parse_args()
    data = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R2.json")
    main_rows = [r for r in data["rows"] if r["panel"] == "confirmatory"]
    if args.check_public:
        recomputed = summarize(main_rows)
        for key in ("success_paired", "false_completion_paired", "families"):
            if recomputed[key] != data["panels"]["confirmatory"][key]:
                raise ValueError(f"public arithmetic differs: {key}")
        print(
            json.dumps(
                {k: recomputed[k] for k in ("success_paired", "false_completion_paired")}, indent=2
            )
        )
        return
    panel = data["panels"]["confirmatory"]
    arms = panel["arms"]
    a, b, initial = (arms[k] for k in ("A", "B", "initial"))
    success, fc = panel["success_paired"], panel["false_completion_paired"]
    costs = panel["costs"]
    count = a["planned"]
    environment = data["environment"]
    pilot = data["panels"]["pilot"]
    proof_audit = read(ROOT / "tasks/pic110r2/proof_audit.json")
    n_worlds = sum(x["world_count"] for x in proof_audit)
    n_proofs = sum(len(x["all_minimal_proofs"]) for x in proof_audit)
    diagnostic = [r for r in data["rows"] if r["pic"] is not None]
    signatures = Counter(
        (
            tuple(r["pic"]["intake"]["missing_obligations"])
            if r["pic"]["intake"]["missing_obligations"] is not None
            else None
        )
        for r in diagnostic
    )
    burdens = Counter(str(r["pic"]["intake"]["residual_burden"]) for r in diagnostic)
    states = Counter(r["attempt_status"] for r in data["rows"])
    transitions = {}
    for arm in ("A", "B"):
        changes = []
        for row in (r for r in main_rows if r["condition"] == arm):
            before = next(
                r
                for r in main_rows
                if r["task_id"] == row["task_id"] and r["condition"] == "initial"
            )
            if before["oracle"]["success"] != row["oracle"]["success"]:
                changes.append(
                    {
                        "task_id": row["task_id"],
                        "initial_success": before["oracle"]["success"],
                        "final_success": row["oracle"]["success"],
                    }
                )
        transitions[arm] = changes
    write(ROOT / "docs/PIC_1_1_0_R2_INITIAL_TRANSITIONS.json", transitions)
    observed_regression = transitions == {
        "A": [{"task_id": "r2_validate_02", "initial_success": True, "final_success": False}],
        "B": [],
    }
    transition_note = (
        "The sole A/B discordance is r2_validate_02: the initial answer correctly retained "
        "all three invalid row labels, A dropped the row with an invalid status, and B "
        "retained the correct initial set. The favorable B comparison reflects avoidance "
        "of a generic-review regression, not repair of an initially wrong answer."
        if observed_regression
        else "The saved transition table describes which initial success labels changed in each arm."
    )
    transition_counts = {
        arm: {
            "improved": sum(not r["initial_success"] and r["final_success"] for r in changes),
            "worsened": sum(r["initial_success"] and not r["final_success"] for r in changes),
        }
        for arm, changes in transitions.items()
    }
    unresolved_ok = {
        arm: sum(
            r["gold_requires_abstention"] and r["oracle"]["obligations_correct"] is True
            for r in main_rows
            if r["condition"] == arm
        )
        for arm in ("A", "B")
    }
    rows_table = []
    for ar in (r for r in main_rows if r["condition"] == "A"):
        br = next(r for r in main_rows if r["task_id"] == ar["task_id"] and r["condition"] == "B")
        rows_table.append(
            f"| {ar['task_id']} | {''.join(ar['order'])} | {int(ar['oracle']['success'])} | "
            f"{int(br['oracle']['success'])} | {ar['oracle']['substantive_false_completion']} | "
            f"{br['oracle']['substantive_false_completion']} |"
        )
    family_table = "\n".join(
        f"| {family} | {d['A']['success']}/{d['A']['n']} | {d['B']['success']}/{d['B']['n']} | {d['A']['false_completion']} | {d['B']['false_completion']} |"
        for family, d in panel["families"].items()
    )
    if success["difference_B_minus_A"] is None:
        interpretation = "The primary comparison was not estimable."
    elif success["conservative_exact_95_ci"][0] > 0:
        interpretation = "The conservative paired success interval favors B in this finite setting."
    elif success["conservative_exact_95_ci"][1] < 0:
        interpretation = "The conservative paired success interval favors A in this finite setting."
    else:
        interpretation = "The paired success interval does not establish incremental superiority."
    point = (
        "missing"
        if success["difference_B_minus_A"] is None
        else f"{100 * success['difference_B_minus_A']:.1f} pp"
    )
    fpoint = (
        "missing"
        if fc["difference_B_minus_A"] is None
        else f"{100 * fc['difference_B_minus_A']:.1f} pp"
    )
    runtime_ratio = (
        costs["B_seconds"] / costs["A_seconds"]
        if costs["A_seconds"] and costs["B_seconds"]
        else None
    )
    token_a = (
        0.5 * (initial["input_tokens"] + initial["output_tokens"])
        + a["input_tokens"]
        + a["output_tokens"]
        if all(
            x is not None
            for x in (
                initial["input_tokens"],
                initial["output_tokens"],
                a["input_tokens"],
                a["output_tokens"],
            )
        )
        else None
    )
    token_b = (
        0.5 * (initial["input_tokens"] + initial["output_tokens"])
        + b["input_tokens"]
        + b["output_tokens"]
        if all(
            x is not None
            for x in (
                initial["input_tokens"],
                initial["output_tokens"],
                b["input_tokens"],
                b["output_tokens"],
            )
        )
        else None
    )
    warm = read(OUT / "setup/warmup_response.json")
    model_records = [r for r in data["rows"] if r["attempt_status"] != "NOT_RUN"]
    resources = [
        r[k]
        for r in model_records
        for k in ("resource_before", "resource_after")
        if r[k] is not None
    ]
    all_usage_known = all(
        r["token_usage"] is not None
        and all(type(r["token_usage"].get(k)) is int for k in ("input", "output"))
        for r in model_records
    )
    total_tokens = (
        (data["campaign"]["input_tokens_observed"] + data["campaign"]["output_tokens_observed"])
        if all_usage_known
        else None
    )
    span = (
        (
            datetime.fromisoformat(panel["finished_utc"]).timestamp()
            - data["campaign"]["started_epoch"]
        )
        if panel.get("finished_utc")
        else None
    )
    allocations = [
        m.get("size_vram")
        for path in OUT.glob("*/*/ollama_ps.json")
        for m in read(path).get("models", [])
    ]
    pic_flags = b["pic_flags"]
    for phase in ("pilot", "main"):
        write(
            ROOT / f"docs/PIC_1_1_0_R2_PREREG_{phase.upper()}.json",
            read(OUT / f"prereg_{phase}.json"),
        )
    preservation_result = preservation()
    report = f"""# PIC 1.1.0 R2: prospective evidence-oracle experiment

Execution status: **{data["status"]}**; confirmatory panel **{panel["status"]}**.
Run date: 2026-10-20, Asia/Tokyo. Local execution; no external publication.

## Abstract

R2 prospectively repaired the earlier oracle's source-ID/type ambiguity and
overinclusive required evidence sets. Sixteen fresh confirmatory tasks used the
same installed local model, one common initial answer and one revision per arm.
Success was A {a["success"]}/{count}, B {b["success"]}/{count}; substantive false
completion was A {a["substantive_false_completion"]}/{a["completion_flag_observed"]},
B {b["substantive_false_completion"]}/{b["completion_flag_observed"]}.
Success difference B-A: {point}, conservative 95% CI
{ci(success["conservative_exact_95_ci"])}. {interpretation}
Allocated measured workflow seconds: A {number(costs["A_seconds"])},
B {number(costs["B_seconds"])}. The design tests this finite integration, not
general intelligence, external truth, ASI or universal PIC effectiveness.

## Research question and fixed hypotheses

Does unchanged PIC 1.1.0 add independently verified success or reduce substantive
false completion beyond a fixed generic review? H1 is structured diagnosis;
H2 task success; H3 substantive false completion; H4 measured resource efficiency;
H5 preservation of unresolved obligations. PIC's own acceptance cannot serve as
an independent correctness label. The original run and R2 are not pooled.

## Exact environment and identities

- Model: `{environment["model"]["name"]}`, digest
  `{environment["model"]["digest"]}`, {environment["model"]["details"]["parameter_size"]},
  {environment["model"]["details"]["quantization_level"]}, GGUF.
- Reported parent: `{environment["model"]["details"]["parent_model"]}`. This is
  an observed local package, not independent vendor authentication.
- PIC {environment["pic_version"]}, non-editable official wheel SHA-256
  `{environment["pic_distribution_hash"]}`. Imported from the isolated environment.
- Ollama {environment["ollama"]["version"]}; Python `{environment["python"]}`;
  platform `{environment["platform"]}`. The unchanged dependency lock was reused.
- CPU AMD Ryzen 7 8840HS, 8 cores/16 threads; RAM {environment["ram_bytes"]} bytes;
  Radeon 780M integrated graphics. GPU allocation snapshots are in raw Ollama
  process records. CPU snapshots {min(r["cpu_percent"] for r in resources):.1f}-
  {max(r["cpu_percent"] for r in resources):.1f}%; RAM snapshots
  {min(r["ram_percent"] for r in resources):.1f}-{max(r["ram_percent"] for r in resources):.1f}%.
  No continuous GPU/energy monitoring was available.
  Observed Ollama size_vram snapshots: {sorted(set(allocations), key=lambda x: str(x))} bytes;
  this is actual reported allocation, not nominal dedicated VRAM.

No model was downloaded, changed or silently substituted. The prior qwen3.5
reference remains unavailable; this is the same gemma4 digest used in the first
PIC 1.1.0 run. No cloud inference or external lookup was performed.

## Preregistration and pilot gate

Protocol: [PROTOCOL_PIC_1_1_0_R2.md](PROTOCOL_PIC_1_1_0_R2.md).
Pilot/main normalized-LF manifest SHA-256:
`{data["preregistration_hashes"]["pilot"]}` /
`{data["preregistration_hashes"]["main"]}`.
The protocol, prompts, tasks, all gold/proof data, evaluator, logic, runner,
analysis and tests were fixed before pilot inference and committed locally.
Main was frozen before any confirmatory inference. Any technical amendments,
if present, are listed in the pilot gate note; no effect-driven task selection
or primary-endpoint change is permitted.

Pilot status {pilot["status"]}; success initial/A/B
{pilot["arms"]["initial"]["success"]}/{pilot["arms"]["A"]["success"]}/{pilot["arms"]["B"]["success"]}
out of four each. Pilot is excluded from primary estimates. Warmup returned
{warm.get("eval_count")} output tokens in {warm["wall_seconds"]:.3f} s including
load; it is one real call, not a mock or task trial.

## Dataset and independent minimum-proof oracle

Four families, four new confirmatory tasks each; five require explicit unresolved
answers. Public rule/domain/source facts are separate from gold/proof files.
The runner never loads gold for generation, and neither Ollama nor PIC has
filesystem tools. PIC live connectors are disabled. No generated code executes.

Across all twenty new tasks, {n_worlds} finite worlds and {n_proofs} minimal
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
| Semantically verified task success | {a["success"]}/{count} | {b["success"]}/{count} | {point} | {ci(success["conservative_exact_95_ci"])} |
| Substantive false completion | {a["substantive_false_completion"]}/{a["completion_flag_observed"]} | {b["substantive_false_completion"]}/{b["completion_flag_observed"]} | {fpoint} | {ci(fc["conservative_exact_95_ci"])} |

Success B wins/ties/losses: {success.get("B_higher")}/{success.get("ties")}/{success.get("B_lower")}.
False-completion B increases/ties/decreases: {fc.get("B_higher")}/{fc.get("ties")}/{fc.get("B_lower")}.
Observed paired H3 denominator {fc["n"]}; unknown completion flags A
{a["completion_flag_unknown"]}, B {b["completion_flag_unknown"]}. Planned-denominator
H3 bounds: A {a["false_completion_planned_bounds"]}, B {b["false_completion_planned_bounds"]}.
Wilson success intervals: A {a["success_wilson_95_ci"]}, B {b["success_wilson_95_ci"]}.
Wilson false-completion intervals: A {a["false_completion_wilson_95_ci"]}, B {b["false_completion_wilson_95_ci"]}.
Exact McNemar p-values: success {success.get("exact_mcnemar_two_sided_p")},
false completion {fc.get("exact_mcnemar_two_sided_p")}. Paired 20000-replicate
bootstrap intervals: success {ci(success.get("paired_bootstrap_percentile_95_ci"))},
false completion {ci(fc.get("paired_bootstrap_percentile_95_ci"))}.
Degenerate bootstrap intervals do not prove equivalence. The conservative
intervals and synthetic family dependence limit population interpretation.
These intervals assume independent exchangeable task outcomes; nominal coverage
is not established for a broader population with dependent template clusters.

### Relation to the common initial answers

Initial success was {initial["success"]}/{count}, with
{initial["substantive_false_completion"]} substantive false completions. Initial-to-final
success-label changes were `{json.dumps(transitions, sort_keys=True)}`.
{transition_note}
Initial-to-final improvement/regression counts: `{json.dumps(transition_counts)}`.
This is a descriptive within-task observation, not an added independent sample
or a replacement primary endpoint. No improved diagnostic localization is
inferred from this one preserved answer.

| Task | Order | A success | B success | A substantive false completion | B substantive false completion |
| --- | --- | ---: | ---: | --- | --- |
{chr(10).join(rows_table)}

| Family | A success | B success | A false completion | B false completion |
| --- | ---: | ---: | ---: | ---: |
{family_table}

## Secondary diagnostic results

| Metric | A | B |
| --- | ---: | ---: |
| Semantic decision correct | {a["semantic_decision_correct"]}/{count} | {b["semantic_decision_correct"]}/{count} |
| Sufficient cited evidence | {a["evidence_sufficient"]}/{count} | {b["evidence_sufficient"]}/{count} |
| Format/type compliant | {a["format_conformant"]}/{count} | {b["format_conformant"]}/{count} |
| Evidence-incomplete completion | {a["evidence_incomplete_completion"]} | {b["evidence_incomplete_completion"]} |
| Correct supported abstention | {a["correct_abstention"]}/{a["abstention_denominator"]} | {b["correct_abstention"]}/{b["abstention_denominator"]} |
| Correct task obligation set | {a["obligations_correct"]}/{count} | {b["obligations_correct"]}/{count} |

PIC final B check state counts (true/false/unknown), with missing diagnoses
separately counted as {b["pic_diagnosis_missing"]}:
`{json.dumps(pic_flags, sort_keys=True)}`.
Across {len(diagnostic)} observed initial/final diagnoses, obligation signatures:
`{dict(signatures)}`; residual burden signatures `{dict(burdens)}`.
Generic framework obligations are not automatically task specific missing
evidence. Actual route/action fields remain available in private raw reports.
No independence or usefulness is inferred from their parseability alone.
PIC disappearance tracking is retained separately from independent task
obligations; no new external verifier evidence was produced by either arm.
Exact obligation sets on genuinely unresolved tasks: A {unresolved_ok["A"]}/
{a["abstention_denominator"]}, B {unresolved_ok["B"]}/{b["abstention_denominator"]}.
The separate obligation audit distinguishes lost obligations from extra labels;
accuracy of a whole set is not equated with disappearance of a missing fact.
Certification remains unknown/not applicable: the real resource-bound runtime
trajectory contract is absent and no modeled proxy gain is used as observation.

## Resource accounting

| Component | Input tokens | Output tokens | Model seconds | PIC seconds |
| --- | ---: | ---: | ---: | ---: |
| Shared initial | {initial["input_tokens"]} | {initial["output_tokens"]} | {number(initial["model_seconds"])} | {number(initial["pic_seconds"])} |
| A revision | {a["input_tokens"]} | {a["output_tokens"]} | {number(a["model_seconds"])} | {number(a["pic_seconds"])} observational |
| B revision | {b["input_tokens"]} | {b["output_tokens"]} | {number(b["model_seconds"])} | {number(b["pic_seconds"])} |

Half of initial generation is allocated to each arm; B also pays initial and
final PIC. A's final PIC is measurement overhead. Allocated totals A
{number(costs["A_seconds"])} s, B {number(costs["B_seconds"])} s; B/A ratio
{number(runtime_ratio)}. Allocated input+output token totals A {number(token_a)},
B {number(token_b)}. These component sums omit identity-query/I/O/orchestration
overhead; observed confirmatory panel wall time is {number(panel.get("elapsed_seconds"))} s.
Joint-success cases {costs["joint_success_tasks"]}/{count}: allocated A/B seconds
{number(costs["joint_success_A_seconds"])}/{number(costs["joint_success_B_seconds"])}.
Cache/load effects are recorded but not isolated. No claim of equal realized
compute or a time-to-success frontier follows from one matched revision.
Energy/monetary cost is missing. Raw timing/token metadata is retained.
Campaign span including between-panel work: {number(span)} seconds, excluding
the earlier warmup. Actual observed input/output tokens across real calls:
{data["campaign"]["input_tokens_observed"]}/{data["campaign"]["output_tokens_observed"]};
complete token metadata coverage: {all_usage_known}; total tokens {total_tokens}.
PIC overhead charged to B is the shared-initial diagnosis plus B's final
diagnosis: {number(initial["pic_seconds"] + b["pic_seconds"]) if initial["pic_seconds"] is not None and b["pic_seconds"] is not None else "missing"} seconds.

## Full attempt ledger, negative and inconclusive outcomes

Actual real calls: {data["campaign"]["calls"]} including one warmup; planned
task slots {len(data["rows"])}. Retained states: `{dict(states)}`.
Pilot and confirmatory logs are separate. Failure/timeout/truncation/not-run
trials are not removed, retried or replaced. Completion status above concerns
execution, not a favorable efficacy result. {interpretation}
Any lack of change is distinguished from proof of equivalence. Additional cost
without demonstrated endpoint improvement is not a measured efficiency benefit.
For the success endpoint: {interpretation} Format-conformant answer counts are
{a["format_conformant"]}/{count} and {b["format_conformant"]}/{count}; surface
normalization usage counts are {a["surface_normalization_used"]} and
{b["surface_normalization_used"]}. These are reported separately rather than
hidden in task success labels. Joint-success and all-task costs above are the
resource comparison, not an inferred acceleration.

## Comparison with the earlier run and preservation

The old strict 2/12 versus 2/12 success and 5/12 versus 5/12 completion labels
remain untouched, along with their oracle-validity audit and incomplete
historical panel. R2's tasks, size, semantic scoring and evidence proofs differ;
across-run changes cannot be attributed to PIC or model improvement. The same
model digest is the controlled identity, not a license to pool distinct trials.
Prior preservation: **{preservation_result["status"]}**, {preservation_result["protected_files"]}
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
Q2: success A {a["success"]}/{count}, B {b["success"]}/{count}, difference {point},
CI {ci(success["conservative_exact_95_ci"])}. {interpretation}
Q3: substantive false completion A {a["substantive_false_completion"]},
B {b["substantive_false_completion"]}, with uncertainty and missingness above.
Q4: task obligation correctness and generic PIC persistence are reported
separately; text repair is not evidence acquisition or verifier settlement.
Q5: assess those endpoints jointly with measured A/B cost ratio {number(runtime_ratio)};
no certification or unmeasured cost saving is inferred.
Q6: external validation, multiple seeds/models, real verifier integration and
benefit under a controlled equal-time/token frontier remain unproven.
"""
    (ROOT / "docs/EXPERIMENT_REPORT_PIC_1_1_0_R2.md").write_text(report, encoding="utf-8")
    print("Rendered R2 report and public preregistrations")


if __name__ == "__main__":
    main()
