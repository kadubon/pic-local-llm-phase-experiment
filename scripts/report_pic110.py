"""Render the English report from frozen-data analysis, without additional inference."""
# Markdown tables in the report template intentionally have long source lines.
# ruff: noqa: E501

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime

from pic_local_llm_phase_experiment.pic110_runner import OUT, ROOT, read, sha, write


def fmt(value, digits=3):
    return "missing" if value is None else f"{value:.{digits}f}"


def interval(value):
    return "missing" if value is None else f"[{100 * value[0]:.1f}, {100 * value[1]:.1f}] pp"


def main() -> None:
    data = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0.json")
    p = data["panels"]["confirmatory"]
    pilot = data["panels"]["pilot"]
    historical = data["panels"]["historical"]
    arms = p["arms"]
    a, b, initial = (arms[k] for k in ("A", "B", "initial"))
    success, fc = p["success_paired"], p["false_completion_paired"]
    rows = [r for r in data["rows"] if r["panel"] == "confirmatory"]
    call_count = data["campaign"]["calls"]
    campaign_span = (
        datetime.fromisoformat(historical["finished_utc"]).timestamp()
        - data["campaign"]["started_epoch"]
    )
    task_ids = [r["task_id"] for r in rows if r["condition"] == "initial"]
    lookup = {(r["task_id"], r["condition"]): r for r in rows}
    table = []
    for tid in task_ids:
        i, aa, bb = (lookup[(tid, c)] for c in ("initial", "A", "B"))
        table.append(
            f"| {tid} | {''.join(aa['order'])} | "
            f"{int(i['independent_oracle_result']['success'])} | "
            f"{int(aa['independent_oracle_result']['success'])} | "
            f"{int(bb['independent_oracle_result']['success'])} | "
            f"{aa['independent_oracle_result']['false_completion']} | "
            f"{bb['independent_oracle_result']['false_completion']} |"
        )
    family_table = []
    for family, result in p["families"].items():
        family_table.append(
            f"| {family} | {result['A']['success']}/{result['A']['n']} | "
            f"{result['B']['success']}/{result['B']['n']} | "
            f"{result['A']['false_completion']} | "
            f"{result['B']['false_completion']} |"
        )
    all_success = success["difference_B_minus_A"] == 0
    direction = (
        "No incremental task success benefit was observed"
        if all_success
        else (
            "The PIC arm had higher observed success"
            if success["difference_B_minus_A"] > 0
            else "The PIC arm had lower observed success"
        )
    )
    cost_a = 0.5 * initial["model_wall_seconds"] + a["model_wall_seconds"] + a["evaluator_seconds"]
    cost_b = (
        0.5 * initial["model_wall_seconds"]
        + b["model_wall_seconds"]
        + initial["pic_wall_seconds"]
        + b["pic_wall_seconds"]
        + b["evaluator_seconds"]
    )
    common_tokens = 0.5 * (initial["input_tokens"] + initial["output_tokens"])
    tokens_a = common_tokens + a["input_tokens"] + a["output_tokens"]
    tokens_b = common_tokens + b["input_tokens"] + b["output_tokens"]
    burdens = Counter(
        str(r["intake_status"]["residual_burden"]) for r in data["rows"] if r["intake_status"]
    )
    missing_sets = Counter(
        tuple(r["missing_obligations"])
        for r in data["rows"]
        if r["missing_obligations"] is not None
    )
    disappeared = [
        item
        for panel in data["panels"].values()
        for item in panel["pic_obligation_persistence"]
        if item["disappeared"]
    ]
    not_run = [r for r in data["rows"] if r["attempt_status"] != "OK"]
    total_pic = sum(r["pic_seconds"] for r in data["rows"] if r["pic_seconds"] is not None)
    total_model = sum(r["elapsed_time"] for r in data["rows"] if r["elapsed_time"] is not None)
    status_table = "\n".join(
        f"| {name} | {panel['status']} | {panel['planned_tasks']} | "
        f"{sum(v['attempts'] for v in panel['arms'].values())} | "
        f"{fmt(panel.get('elapsed_seconds'))} |"
        for name, panel in data["panels"].items()
    )
    flags = b["pic_flags"]
    resources = [
        r[k]
        for r in data["rows"]
        for k in ("resource_before", "resource_after")
        if r[k] is not None
    ]
    ram = [r["ram_percent"] for r in resources]
    cpu = [r["cpu_percent"] for r in resources]
    all_ps = [read(f) for f in OUT.glob("*/*/ollama_ps.json")]
    vram = [m["size_vram"] for d in all_ps for m in d.get("models", []) if "size_vram" in m]
    recorded_ns = {
        arm: {
            k: sum(
                r["ollama_timing_ns"][k]
                for r in rows
                if r["condition"] == arm and r.get("ollama_timing_ns", {}).get(k) is not None
            )
            / 1e9
            for k in ("load_duration", "prompt_eval_duration", "eval_duration")
        }
        for arm in ("initial", "A", "B")
    }
    source_preserved = (
        subprocess.run(
            [
                "git",
                "diff",
                "--exit-code",
                data["base_commit"],
                "--",
                "tasks/task_*.yaml",
                "configs/experiment.default.yaml",
                "configs/experiment.shared_initial.yaml",
                "docs/EXPERIMENT_REPORT_v0.1.0.md",
                "docs/EXPERIMENT_REPORT_v0.2.0.md",
                "docs/REPRODUCIBILITY.md",
                "uv.lock",
                "pyproject.toml",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).returncode
        == 0
    )
    probes = read(OUT / "boundary_probes/summary.json")
    oracle_audit = read(ROOT / "docs/PIC_1_1_0_ORACLE_AUDIT.json")
    probe_table = "\n".join(
        f"| {name} | {d['check']['accepted']} | {d['check']['workflow_usable']} | "
        f"{d['check']['operationally_usable']} | {d['check']['settled']} | "
        f"{d['check']['missing_obligation_count']} |"
        for name, d in probes.items()
    )
    # Save the original manifests plus byte-normalization evidence for Git readers.
    prereg_identities = {}
    for phase in ("pilot", "main"):
        manifest = read(OUT / f"prereg_{phase}.json")
        write(ROOT / f"docs/PIC_1_1_0_PREREG_{phase.upper()}.json", manifest)
        raw_manifest = (OUT / f"prereg_{phase}.json").read_bytes()
        prereg_identities[phase] = {
            "frozen_manifest_sha256": sha(raw_manifest),
            "normalized_lf_sha256": sha(raw_manifest.replace(b"\r\n", b"\n")),
        }
    write(ROOT / "docs/PIC_1_1_0_PREREG_IDENTITIES.json", prereg_identities)
    line_endings = {}
    manifest = read(OUT / "prereg_main.json")
    for name, digest in manifest["hashes"].items():
        blob = subprocess.check_output(["git", "show", f"{manifest['git_head']}:{name}"], cwd=ROOT)
        line_endings[name] = {
            "frozen_worktree_sha256": digest,
            "git_blob_sha256": sha(blob),
            "normalized_lf_sha256": sha((ROOT / name).read_bytes().replace(b"\r\n", b"\n")),
        }
    write(ROOT / "docs/PIC_1_1_0_SOURCE_IDENTITIES.json", line_endings)
    runtime = read(OUT / "setup/runtime_compatibility.json")
    report = f"""# PIC 1.1.0 local LLM matched comparison

Status: **{data["status"]}**. Confirmatory panel: **{p["status"]}**.
Run date: 2026-10-20 (Asia/Tokyo). Local execution only; no push or publication.

## 1. Abstract

Twelve new, independently graded synthetic tasks compared a fixed generic
review (A) with PIC-guided review (B), using a single shared initial answer and
one revision call per arm. Independent success was {a["success_count"]}/12 for A
and {b["success_count"]}/12 for B; unsupported completion was
{a["false_completion_count"]}/{a["false_completion_observed_denominator"]} and
{b["false_completion_count"]}/{b["false_completion_observed_denominator"]}.
The paired success difference was {100 * success["difference_B_minus_A"]:.1f}
percentage points (conservative exact 95% CI
{interval(success["conservative_exact_95_ci"])}). {direction}.
PIC produced structured status and residual records, but these remained general
framework obligations. The PIC workflow cost {cost_b:.3f} measured seconds versus
{cost_a:.3f} for A under the allocation defined below. A post hoc audit found
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
  `{data["pic_distribution_hash"]}`. PyPI JSON confirmed 1.1.0 as latest stable
  at preparation. Import was verified under the independent environment.
- Model: **{data["model"]["name"]}**, digest
  `{data["model"]["digest"]}`, {data["model"]["details"]["parameter_size"]},
  {data["model"]["details"]["quantization_level"]}, GGUF. Reported parent model:
  `{data["model"]["details"]["parent_model"]}`. This identity is an observed
  local Ollama package; it is not an independently authenticated vendor model.
- Ollama: {data["ollama"]["version"]}; Python: `{data["python"]}`;
  uv: `{data["uv"]}`; platform: `{data["platform"]}`.
- CPU: AMD Ryzen 7 8840HS, 8 cores / 16 logical CPUs; RAM:
  66,363,183,104 bytes. GPU: Radeon 780M integrated graphics. Windows adapter
  RAM reports 2 GiB, which is not a measured dedicated VRAM allowance.
- Observed Ollama `size_vram`: {sorted(set(vram))} bytes. CPU snapshots ranged
  {min(cpu):.1f}-{max(cpu):.1f}%; RAM snapshots {min(ram):.1f}-{max(ram):.1f}%.
  Snapshots do not measure peaks; GPU utilization is missing.
- Base experiment commit: `{data["base_commit"]}`. Preregistration commit:
  `{manifest["git_head"]}`. No changes to PIC source, models or other servers.

The historical `qwen3.5:35b-a3b` was absent. Existing `gemma4:e4b` was selected
for a finite local workload; the installed `qwen3.6:35b-a3b` was unused. No model
download occurred. Results cannot be attributed causally to PIC version changes.

## 4. Preregistered protocol and pilot

The full design is [PROTOCOL_PIC_1_1_0.md](PROTOCOL_PIC_1_1_0.md).
Main manifest SHA-256: `{data["preregistration_hashes"]["main"]}`.
Pilot manifest SHA-256: `{data["preregistration_hashes"]["pilot"]}`.
Both manifests and Git/worktree byte identities are provided alongside this
report. Windows CRLF worktree hashes can differ from normalized Git blobs;
SOURCE_IDENTITIES records both. Frozen sources were unchanged during inference.
PREREG_IDENTITIES additionally records normalized LF hashes for the manifests.

Pilot results: initial {pilot["arms"]["initial"]["success_count"]}/4,
A {pilot["arms"]["A"]["success_count"]}/4, B {pilot["arms"]["B"]["success_count"]}/4;
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
| Common initial | 12 | {initial["input_tokens"]} | {initial["output_tokens"]} | {initial["model_wall_seconds"]:.3f} | {initial["pic_wall_seconds"]:.3f} |
| A revision | 12 | {a["input_tokens"]} | {a["output_tokens"]} | {a["model_wall_seconds"]:.3f} | {a["pic_wall_seconds"]:.3f} observational |
| B revision | 12 | {b["input_tokens"]} | {b["output_tokens"]} | {b["model_wall_seconds"]:.3f} | {b["pic_wall_seconds"]:.3f} |

Half of common initial generation is charged to each arm. B additionally bears
initial plus final PIC diagnosis; A's final PIC diagnosis is research overhead.
Independent evaluator time is {a["evaluator_seconds"]:.6f} seconds for A and
{b["evaluator_seconds"]:.6f} for B, measured on this analysis pass. Allocated
workflow totals are **A {cost_a:.3f} s, B {cost_b:.3f} s** (B/A {cost_b / cost_a:.2f}).
These allocated totals sum timed generation, grading and required PIC processes;
they omit identity-query, file I/O and orchestration costs. The actual panel
wall time below includes that work and is reported separately.
Allocated token totals are A {tokens_a:.1f}, B {tokens_b:.1f}
(B/A {tokens_b / tokens_a:.2f}). PIC B-path overhead alone is
{initial["pic_wall_seconds"] + b["pic_wall_seconds"]:.3f} seconds.

Same-success matched cases: {len(p["both_success_costs"])}/12. Their exact per-task
revision and PIC costs are in the JSON summary; this comparison is descriptive,
conditioned on joint success. Unconditional all-task totals above remain primary
resource reporting. In those two joint-success cases, A revision time totals
{sum(c["A_revision_model_seconds"] for c in p["both_success_costs"]):.3f} seconds;
B revision time totals
{sum(c["B_revision_model_seconds"] for c in p["both_success_costs"]):.3f} seconds,
plus {sum(c["B_intervention_and_post_pic_seconds"] for c in p["both_success_costs"]):.3f}
seconds of required PIC work. These figures omit the equally shared initial
generation. Recorded Ollama timing components in seconds:
`{json.dumps(recorded_ns, sort_keys=True)}`.

Complete panel wall time is {p["elapsed_seconds"]:.3f} seconds, including both
arms and all diagnostic collection. Across all panels, model calls took
{total_model:.3f} measured seconds and check/intake collection {total_pic:.3f}
seconds, excluding warmup and auxiliary fixed-text probes. Prefix caching and
model load can influence timing. Raw cache counters and load durations are saved;
there was no cache isolation or controlled hardware utilization. Monetary cost,
energy, continuous GPU utilization and true total compute FLOPs are missing.
The elapsed campaign span from pilot start to the historical stopping event was
{campaign_span:.3f} seconds, including inter-panel protocol/report work. The
earlier warmup took 28.194 seconds. Across all 58 real calls, input/output/total
tokens were {data["campaign"]["input_tokens_observed"]}/
{data["campaign"]["output_tokens_observed"]}/
{data["campaign"]["input_tokens_observed"] + data["campaign"]["output_tokens_observed"]}.

## 8. Primary results

| Endpoint | A | B | B minus A | Conservative exact 95% CI |
| --- | ---: | ---: | ---: | --- |
| Independently verified success | {a["success_count"]}/12 | {b["success_count"]}/12 | {100 * success["difference_B_minus_A"]:.1f} pp | {interval(success["conservative_exact_95_ci"])} |
| Unsupported completion | {a["false_completion_count"]}/{a["false_completion_observed_denominator"]} | {b["false_completion_count"]}/{b["false_completion_observed_denominator"]} | {100 * fc["difference_B_minus_A"]:.1f} pp | {interval(fc["conservative_exact_95_ci"])} |

Success wins/ties/losses for B: {success["B_higher"]}/{success["ties"]}/{success["B_lower"]}.
False-completion increases/ties/decreases for B:
{fc["B_higher"]}/{fc["ties"]}/{fc["B_lower"]}. Exact McNemar p-values:
success {success["exact_mcnemar_two_sided_p"]:.3f}, false completion
{fc["exact_mcnemar_two_sided_p"]:.3f}. These do not establish equivalence.

Per-arm success Wilson 95% intervals: A {a["success_wilson_95_ci"]},
B {b["success_wilson_95_ci"]}. False-completion intervals:
A {a["false_completion_wilson_95_ci"]}, B {b["false_completion_wilson_95_ci"]}.
Unknown completion flags: A {a["false_completion_unknown"]},
B {b["false_completion_unknown"]}; paired observable denominator {fc["n"]}.
Planned-denominator false-completion bounds: A
{a["false_completion_planned_bounds"]}, B {b["false_completion_planned_bounds"]}.

The paired bootstrap success interval is
{interval(success["paired_bootstrap_percentile_95_ci"])}; false completion is
{interval(fc["paired_bootstrap_percentile_95_ci"])}. With no discordance these
intervals degenerate; the nonzero conservative exact bounds above are emphasized.
The exact construction assumes exchangeable independent tasks for population
interpretation. Template dependence further limits generalization.

| Task | Order | Initial success | A success | B success | A false completion | B false completion |
| --- | --- | ---: | ---: | ---: | --- | --- |
{chr(10).join(table)}

| Family | A success | B success | A false completion | B false completion |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(family_table)}

## 9. Secondary diagnostic results

Initial success was {initial["success_count"]}/12. Valid evidence:
A {a["valid_evidence_count"]}/12, B {b["valid_evidence_count"]}/12.
Evidence-complete abstention under the strict oracle:
A {a["correct_abstention_count"]}/{a["abstention_denominator"]},
B {b["correct_abstention_count"]}/{b["abstention_denominator"]}.
Exact task obligation disclosure: A {a["unresolved_preserved_count"]}/12,
B {b["unresolved_preserved_count"]}/12, including empty sets on resolved tasks.
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
{oracle_audit["arms"]["A"]["exact_typed_decision_correct"]}/12 for A and
{oracle_audit["arms"]["B"]["exact_typed_decision_correct"]}/12 for B. Allowing
numeric strings only for integer-valued decisions gives
{oracle_audit["arms"]["A"]["decision_correct_allowing_numeric_string"]}/12 in
each arm. Of each arm's five strict unsupported completions, two contain an
incorrect substantive decision; three have the intended decision but fail the
predeclared evidence/type contract. All five intrinsically incomplete-evidence
tasks have complete=false in both arms; their missing evidence was not claimed
verified. Fully evidence-complete abstention nevertheless passes only 2/5.

An explicitly exploratory surface-normalization sensitivity unwraps known
bracketed source IDs and converts decimal integer strings when gold is integer.
It preserves required evidence sets and yields A
{oracle_audit["arms"]["A"]["exploratory_normalized_success"]}/12 versus B
{oracle_audit["arms"]["B"]["exploratory_normalized_success"]}/12 successes, and
{oracle_audit["arms"]["A"]["exploratory_normalized_false_completion"]}/12 versus
{oracle_audit["arms"]["B"]["exploratory_normalized_false_completion"]}/12
unsupported completions. The one-task difference reflects mirror-record
citation retention; this post hoc rule cannot support a confirmatory benefit
claim. This sensitivity is disclosed to show measurement dependence, not
substituted for the preregistered endpoints. Efficacy judgment is held pending
prospectively validated, unambiguous scoring.

B final compact check flags: accepted {flags["accepted"]["true"]}/12,
workflow_usable {flags["workflow_usable"]["true"]}/12,
operationally_usable {flags["operationally_usable"]["true"]}/12,
settled {flags["settled"]["true"]}/12. `acceleration_metrics_certified` was
missing in {flags["acceleration_metrics_certified"]["unknown"]}/12. A and common
initial flags are separately preserved in the JSON; no missing flag became false.

Across the {sum(r["pic_status"] is not None for r in data["rows"])} observed
answer diagnostics ({len(data["rows"])} answer slots planned), missing-obligation set counts
were `{dict(missing_sets)}` and residual-burden counts `{dict(burdens)}`.
Unsupported PIC obligation disappearances observed: {len(disappeared)}.
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
{probe_table}

These probes assess status behavior on self-assertions and missing evidence.
Acceptance remains a structural result, not detection of answer correctness.
No external truth or approval was verified. The repeated identical probe checks
diagnostic stability, not a new statistical unit.

Runtime comparison applicability: **{runtime["status"]}**. Actual saved model
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

The ten old prompts were scheduled unchanged: status {historical["status"]},
{sum(v["attempts"] for v in historical["arms"].values())} actual calls. Their
current observed compact B checks show accepted
{historical["arms"]["B"]["pic_flags"]["accepted"]["true"]}/{historical["arms"]["B"]["pic_status_denominator"]}, workflow usable
{historical["arms"]["B"]["pic_flags"]["workflow_usable"]["true"]}/{historical["arms"]["B"]["pic_status_denominator"]},
operationally usable
{historical["arms"]["B"]["pic_flags"]["operationally_usable"]["true"]}/{historical["arms"]["B"]["pic_status_denominator"]} and
settled {historical["arms"]["B"]["pic_flags"]["settled"]["true"]}/{historical["arms"]["B"]["pic_status_denominator"]}.
The other {10 - historical["arms"]["B"]["pic_status_denominator"]} planned B
diagnostics are unavailable and remain unknown. Independent
success and false-completion labels for these subjective historical tasks are
null. They are not counted as correct or failed tasks. Only the first two tasks
finished without truncation. The third task's initial and both revisions reached
the 768-token ceiling, triggering the fixed three-consecutive-failure rule after
its B revision. That final B diagnosis was not run. Tasks 004-010 and their 21
generations were not run. This panel is incomplete and cannot support an
across-ten-task diagnostic comparison. No token limit was raised or rerun made.
Original configurations,
tasks, lockfile, project metadata and reports preserved: {source_preserved}.

## 11. Negative and inconclusive findings

{direction}. No measured false-completion reduction was demonstrated, and
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
{status_table}

Actual model calls: {call_count} = 1 warmup + scheduled task attempts.
Non-OK scheduled outcomes: {len(not_run)}. Retained planned initial/A/B states
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
Observed A {a["success_count"]}/12 versus B {b["success_count"]}/12,
difference {100 * success["difference_B_minus_A"]:.1f} pp,
95% CI {interval(success["conservative_exact_95_ci"])}. {direction}.
Measurement validity and small sample size preclude equivalence or efficacy claims.

**Q3. Did false completion decline?**
A {a["false_completion_count"]}/{a["false_completion_observed_denominator"]}
versus B {b["false_completion_count"]}/{b["false_completion_observed_denominator"]}.
There was no reduction under the fixed endpoint. Three labels per arm are
contract failures despite the intended decision; two are substantive decision
errors. The paired interval is
{interval(fc["conservative_exact_95_ci"])}.

**Q4. Were unresolved issues accurately preserved?**
PIC's general labels persisted without observed disappearance. Required task
obligations on all five incomplete tasks were retained by both arms; PIC labels did not represent
the specific missing task evidence. General residual persistence alone does
not establish task sensitive H5 superiority.

**Q5. Is there benefit after PIC's added costs?**
No incremental independently verified benefit was demonstrated at these measured
costs. Allocated B cost was {cost_b / cost_a:.2f} times A in measured seconds and
{tokens_b / tokens_a:.2f} times A in tokens. These conditional local timings cannot
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
"""
    (ROOT / "docs/EXPERIMENT_REPORT_PIC_1_1_0.md").write_text(report, encoding="utf-8")
    print("English report and source/preregistration identities generated from saved analysis")


if __name__ == "__main__":
    main()
