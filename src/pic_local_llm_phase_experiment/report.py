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


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    columns = [
        "task_id",
        "baseline_heuristic_obligation_coverage",
        "pic_heuristic_obligation_coverage",
        "pic_missing_obligation_delta",
        "pic_local_phase_score",
    ]
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        values = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        body.append("| " + " | ".join(values) + " |")
    return "\n".join([header, separator, *body])


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
    residual_visibility = _avg(rows, "pic_residual_summary_length_before") > 0
    accepted_after_ratio = _avg(rows, "pic_pic_accepted_after")

    if avg_delta > 0:
        missing_obligation_observation = (
            "PIC-assisted repairs reduced missing-obligation counts on average in this run."
        )
    elif avg_delta < 0:
        missing_obligation_observation = (
            "PIC-assisted repairs increased missing-obligation counts on average in this run."
        )
    else:
        missing_obligation_observation = (
            "PIC-assisted repairs did not change missing-obligation counts on average in this run."
        )

    if residual_visibility:
        residual_observation = (
            "PIC reports exposed residual summaries for at least part of the run."
        )
    else:
        residual_observation = (
            "PIC residual summaries were absent or empty in the collected metrics."
        )

    task_count = len(rows)
    model = manifest.get("model", "unknown")
    run_id = manifest.get("run_id", rows[0].get("run_id", "unknown") if rows else "unknown")
    pic_commit = setup_manifest.get("pic_commit", "not recorded")

    non_claims = "\n".join(f"- {item}" for item in NON_CLAIMS)
    threats = "\n".join(f"- {item}" for item in THREATS_TO_VALIDITY)

    return f"""# PIC Local LLM Phase Experiment Report

## Abstract

This report summarizes a bounded local experiment comparing a baseline local LLM
workflow with a PIC-assisted closed-loop workflow. It evaluates finite,
protocol-relative indicators such as residual visibility, missing-obligation
tracking, repair completion, and reusable candidate formation.

## Research Question

Does adding PIC as a residual-preserving agent-output checker improve local LLM
workflow quality compared with a baseline local LLM loop without PIC?

## Scope and Non-Claims

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

## Model and Environment

- Ollama model: `{model}`
- Ollama endpoint: `{manifest.get("ollama_url", "local endpoint not recorded")}`
- Local-only execution boundary: no cloud LLM APIs, no browsing during experiment

## PIC Version / Commit Hash

- PIC repository: `https://github.com/kadubon/percolation-inversion-compiler`
- PIC commit: `{pic_commit}`
- PIC profile: `{manifest.get("pic_profile", "unknown")}`

## Task Set

The task set contains small synthetic prompts covering README improvement, Python
bug-fix review, test planning, PR summary critique, evidence extraction, safety
boundary clarification, refactoring review, documentation gaps, RAG answer audit,
and agent handoff audit.

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

## Metrics

Finite protocol-relative metrics include missing-obligation counts before and
after repair, residual summary lengths, PIC accepted/settled flags, repair
attempt count, heuristic obligation coverage, self-contradiction flags,
candidate reuse score, and `local_phase_score`.

`local_phase_score` is a weighted sum of finite observables. This score is a
local workflow diagnostic, not a measure of real ASI.

## Results Table

{_markdown_table(rows)}

## Aggregate Results

- Average baseline heuristic obligation coverage: {avg_baseline_coverage:.3f}
- Average PIC-assisted heuristic obligation coverage: {avg_pic_coverage:.3f}
- Average PIC missing-obligation delta: {avg_delta:.3f}
- PIC accepted-after ratio: {accepted_after_ratio:.3f}
- Average local phase score: {avg_phase:.3f}

## Observations

- {missing_obligation_observation}
- {residual_observation}
- These observations are diagnostic only and depend on the task set, model,
  prompts, PIC behavior, and local runtime state.

## Threats to Validity

{threats}

## Safety Notes

- The experiment is local-only by default.
- It does not call cloud LLM APIs.
- It does not browse the web during experiment runs.
- It does not execute arbitrary commands suggested by LLM output.
- LLM-generated text is saved as data and then checked; it is not executed.
- Generated results may contain model output and are ignored by git by default.

## Conclusion

{missing_obligation_observation} {residual_observation} These results may support
a cautious claim about residual visibility or missing-obligation preservation
only when the recorded metrics support it.

PIC did not prove real ASI, truth, physical outcomes, oracle outcomes, or
external-world capability. Results are local, small-sample, model-dependent, and
protocol-relative.
"""
