from __future__ import annotations

from statistics import mean
from typing import Any

NON_CLAIMS = [
    (
        "PIC did not prove real ASI, truth, physical outcomes, oracle outcomes, "
        "or autonomous superintelligence."
    ),
    "The local LLM did not become superintelligent.",
    "The experiment did not prove external adoption or autonomous agent society formation.",
    "The score is a local workflow diagnostic, not a measure of real ASI.",
    "`accepted` is not equivalent to `settled`.",
]

THREATS_TO_VALIDITY = [
    "one model only",
    "small synthetic task set",
    "local Ollama behavior may vary",
    "PIC metrics are protocol-relative",
    "no human expert grading unless explicitly added later",
    "no external task execution",
    "no real-world tool-use validation",
    "baseline prompt sensitivity",
    "possible parser/schema drift if PIC changes",
]


def _to_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _avg(rows: list[dict[str, Any]], key: str) -> float:
    values = [_to_float(row.get(key)) for row in rows if row.get(key) is not None]
    return mean(values) if values else 0.0


def _ratio(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if bool(row.get(key))) / len(rows)


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    columns = [
        "task_id",
        "baseline_heuristic_obligation_coverage",
        "pic_heuristic_obligation_coverage",
        "pic_missing_obligation_delta",
        "pic_pic_operationally_usable_after",
        "pic_pic_settled_after",
        "pic_local_phase_score",
    ]
    labels = [
        "task",
        "baseline coverage",
        "PIC coverage",
        "missing obligation delta",
        "PIC usable after",
        "PIC settled after",
        "local phase score",
    ]
    header = "| " + " | ".join(labels) + " |"
    separator = "| " + " | ".join("---" for _ in labels) + " |"
    body = []
    for row in rows:
        body.append(
            "| " + " | ".join(_format_value(row.get(column, "")) for column in columns) + " |"
        )
    return "\n".join([header, separator, *body])


def _interpret_missing_obligations(avg_delta: float) -> str:
    if avg_delta > 0:
        return "PIC-assisted repairs reduced missing-obligation counts on average in this run."
    if avg_delta < 0:
        return "PIC-assisted repairs increased missing-obligation counts on average in this run."
    return "PIC-assisted repairs did not change missing-obligation counts on average in this run."


def _interpret_residuals(rows: list[dict[str, Any]]) -> str:
    summary_seen = _avg(rows, "pic_residual_summary_length_before") > 0
    charge_seen = _avg(rows, "pic_residual_charge_total_before") > 0
    if summary_seen and charge_seen:
        return "PIC exposed residual summaries and residual charge totals for this run."
    if summary_seen:
        return "PIC exposed residual summaries, but numeric residual charge was not observed."
    return "PIC residual summaries were absent or empty in the collected metrics."


def _interpret_schema_fields(schema_ratio: float) -> str:
    if schema_ratio == 1.0:
        return "All parsed PIC reports contained the expected runtime report fields."
    if schema_ratio > 0.0:
        return "Some parsed PIC reports contained the expected runtime report fields."
    return "The expected PIC runtime report fields were not available in the parsed metrics."


def render_report(
    *,
    rows: list[dict[str, Any]],
    manifest: dict[str, Any] | None = None,
    setup_manifest: dict[str, Any] | None = None,
) -> str:
    manifest = manifest or {}
    setup_manifest = setup_manifest or {}
    avg_delta = _avg(rows, "pic_missing_obligation_delta")
    avg_phase = _avg(rows, "pic_local_phase_score")
    avg_baseline_coverage = _avg(rows, "baseline_heuristic_obligation_coverage")
    avg_pic_coverage = _avg(rows, "pic_heuristic_obligation_coverage")
    avg_residual_charge_delta = _avg(rows, "pic_residual_charge_delta")
    accepted_after_ratio = _ratio(rows, "pic_pic_accepted_after")
    usable_after_ratio = _ratio(rows, "pic_pic_operationally_usable_after")
    settled_after_ratio = _ratio(rows, "pic_pic_settled_after")
    schema_ratio = _ratio(rows, "pic_pic_schema_fields_usable")

    missing_obligation_observation = _interpret_missing_obligations(avg_delta)
    residual_observation = _interpret_residuals(rows)
    schema_observation = _interpret_schema_fields(schema_ratio)

    task_count = len(rows)
    model = manifest.get("model", "unknown")
    run_id = manifest.get("run_id", rows[0].get("run_id", "unknown") if rows else "unknown")
    pic_commit = setup_manifest.get("pic_commit", "not recorded")

    non_claims = "\n".join(f"- {item}" for item in NON_CLAIMS)
    threats = "\n".join(f"- {item}" for item in THREATS_TO_VALIDITY)

    return f"""# PIC Local LLM Phase Experiment Report

## Abstract

This report summarizes a bounded local experiment comparing a baseline local LLM
self-review workflow with a PIC-assisted residual-preserving repair workflow.
The experiment evaluates finite, protocol-relative workflow indicators:
missing-obligation tracking, residual visibility, repair completion, and
candidate reuse signals.

The report is diagnostic. It does not measure real ASI, intelligence, truth, or
external-world capability.

## What Is PIC?

Percolation Inversion Compiler (PIC) is a finite certificate, verifier-routing,
and residual-ledger runtime for protocol-relative ASI-proxy research. In this
experiment, PIC is used as an agent-output checker: it converts local LLM
candidate answers into deterministic JSON fields such as `accepted`,
`operationally_usable`, `settled`, `runtime_report.missing_obligations`,
`runtime_report.residual_ledger`, and `residual_summary`.

PIC is fail-closed. A useful diagnostic output may still have `settled=false`;
unresolved obligations are expected to remain visible until finite verifier
rules discharge them.

## Research Question

Does adding PIC as a residual-preserving agent-output checker improve local LLM
workflow diagnostics compared with a baseline local LLM loop without PIC?

## Experimental Hypothesis

If PIC is useful in this local workflow, then PIC-assisted repair attempts should
make residuals and missing obligations more visible, preserve unresolved
obligations more explicitly, or reduce missing-obligation counts relative to the
initial PIC intake report.

## Scope And Non-Claims

{non_claims}

## Experimental Setup

- Run id: `{run_id}`
- Task count: {task_count}
- Conditions: baseline LLM-only and PIC-assisted closed loop
- Repair rounds: {manifest.get("repair_rounds", "unknown")}
- Temperature: {manifest.get("temperature", "unknown")}
- Top-p: {manifest.get("top_p", "unknown")}
- Seed: {manifest.get("seed", "unknown")}
- Max generated tokens: {manifest.get("num_predict", "unknown")}

## Model And Environment

- Ollama model: `{model}`
- Ollama endpoint: `{manifest.get("ollama_url", "local endpoint not recorded")}`
- Local-only execution boundary: no cloud LLM APIs, no browsing during experiment

## PIC Version / Commit Hash

- PIC repository: `https://github.com/kadubon/percolation-inversion-compiler`
- PIC commit: `{pic_commit}`
- PIC profile: `{manifest.get("pic_profile", "unknown")}`

## Conditions

Baseline condition:

- Ask the local LLM to answer the task.
- Ask the same local LLM to self-review once.
- Ask it to produce a final answer.

PIC-assisted condition:

- Ask the local LLM to answer the same task.
- Run `pic agent intake` on the candidate.
- Feed residual summary and missing obligations back to the local LLM.
- Ask for one repair attempt.
- Run `pic agent intake` again.

## Operational Definitions

- `accepted`: PIC accepted the finite checker path for this report shape. It is
  not treated as settlement.
- `operationally_usable`: PIC indicated the result may be useful for routing
  under the current protocol.
- `settled`: scoped finite obligations were discharged. This is stricter than
  `accepted`.
- `missing_obligations`: obligations PIC says remain unresolved.
- `residual_summary`: PIC residual coordinate summary, normalized for this
  report.
- `local_phase_score`: this repository's bounded heuristic score over finite
  observables. It is not a PIC theorem and not a real ASI metric.

## Dependent Variables

The primary dependent variables are missing-obligation delta, residual summary
availability, residual charge delta, PIC runtime field availability,
operational usability, and heuristic obligation coverage.

## Results Table

{_markdown_table(rows)}

## Aggregate Results

- Average baseline heuristic obligation coverage: {avg_baseline_coverage:.3f}
- Average PIC-assisted heuristic obligation coverage: {avg_pic_coverage:.3f}
- Average PIC missing-obligation delta: {avg_delta:.3f}
- Average PIC residual charge delta: {avg_residual_charge_delta:.3f}
- PIC accepted-after ratio: {accepted_after_ratio:.3f}
- PIC operationally-usable-after ratio: {usable_after_ratio:.3f}
- PIC settled-after ratio: {settled_after_ratio:.3f}
- PIC schema-field usable ratio: {schema_ratio:.3f}
- Average local phase score: {avg_phase:.3f}

## Interpretation Guide

- A positive missing-obligation delta means fewer obligations after repair.
- A positive residual charge delta means the normalized residual charge total
  decreased after repair.
- `accepted`, `operationally_usable`, and `settled` are reported separately.
  Do not read `accepted=true` as proof that all obligations were settled.
- Empty residual fields can mean either there were no residuals or the PIC schema
  changed; inspect raw PIC reports before making strong claims.

## Observations

- {missing_obligation_observation}
- {residual_observation}
- {schema_observation}
- These observations are diagnostic only and depend on the task set, model,
  prompts, PIC behavior, and local runtime state.

## Run Artifact Map

- Per-task raw outputs: `results/runs/<run_id>/<task_id>/`
- Per-task metrics: `results/runs/<run_id>/<task_id>/metrics.json`
- Summary JSON: `results/summary.json`
- Summary CSV: `results/summary.csv`
- This Markdown report: `reports/experiment_report.md`

## Threats To Validity

{threats}

## Safety Notes

- The experiment is local-only by default.
- It does not call cloud LLM APIs.
- It does not browse the web during experiment runs.
- It does not execute arbitrary commands suggested by LLM output.
- LLM-generated text is saved as data and then checked; it is not executed.
- Generated results may contain model output and are ignored by git by default.

## What This Report Cannot Conclude

This report cannot conclude that PIC creates ASI, proves ASI phase formation,
makes a local model superintelligent, validates physical or oracle outcomes, or
proves external-world capability acceleration.

## Conclusion

{missing_obligation_observation} {residual_observation} These results may support
a cautious local claim about residual visibility or missing-obligation handling
only when the recorded metrics support it.

PIC did not prove real ASI, truth, physical outcomes, oracle outcomes, or
external-world capability. Results are local, small-sample, model-dependent, and
protocol-relative.
"""
