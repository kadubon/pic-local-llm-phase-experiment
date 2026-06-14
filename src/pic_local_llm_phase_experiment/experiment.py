from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from pic_local_llm_phase_experiment.metrics import compute_baseline_metrics, compute_pic_metrics
from pic_local_llm_phase_experiment.ollama_client import OllamaClient, OllamaError
from pic_local_llm_phase_experiment.paths import (
    ensure_dir,
    read_json,
    relative_posix,
    write_json,
    write_text,
)
from pic_local_llm_phase_experiment.pic_runner import PicRunner
from pic_local_llm_phase_experiment.schemas import (
    ExperimentConfig,
    ExperimentMode,
    TaskRunMetrics,
    TaskSpec,
)
from pic_local_llm_phase_experiment.task_loader import load_tasks

LOCAL_BOUNDARY = """\
You are participating in a bounded local research experiment.
Do not claim real ASI, autonomous superintelligence, oracle truth, physical-world
outcomes, or real-world capability acceleration. Do not request cloud APIs,
secrets, browsing, or arbitrary command execution. Produce useful reviewable text.
"""

SETUP_MANIFEST = Path("results") / "setup_manifest.json"


def estimate_experiment_workload(
    task_count: int,
    repair_rounds: int,
    experiment_mode: ExperimentMode = "separate_initial",
) -> dict[str, Any]:
    if experiment_mode == "shared_initial":
        shared_initial_generation_count = task_count
        baseline_generation_count = task_count * 2
        pic_candidate_generation_count = 0
    else:
        shared_initial_generation_count = 0
        baseline_generation_count = task_count * 3
        pic_candidate_generation_count = task_count
    pic_repair_generation_count = task_count * repair_rounds
    return {
        "experiment_mode": experiment_mode,
        "shared_initial_answer_used": experiment_mode == "shared_initial",
        "task_count": task_count,
        "repair_rounds": repair_rounds,
        "shared_initial_generation_count": shared_initial_generation_count,
        "baseline_generation_count": baseline_generation_count,
        "pic_candidate_generation_count": pic_candidate_generation_count,
        "pic_repair_generation_count": pic_repair_generation_count,
        "ollama_generation_count": (
            shared_initial_generation_count
            + baseline_generation_count
            + pic_candidate_generation_count
            + pic_repair_generation_count
        ),
        "pic_intake_count": task_count * (1 + repair_rounds),
    }


def load_pic_setup_metadata(root: Path) -> dict[str, Any]:
    manifest_path = root / SETUP_MANIFEST
    if not manifest_path.exists():
        return {
            "status": "missing",
            "manifest_path": SETUP_MANIFEST.as_posix(),
        }
    try:
        raw = read_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "unreadable",
            "manifest_path": SETUP_MANIFEST.as_posix(),
            "error": str(exc),
        }
    if not isinstance(raw, dict):
        return {
            "status": "invalid",
            "manifest_path": SETUP_MANIFEST.as_posix(),
        }
    return {
        "status": str(raw.get("status", "unknown")),
        "manifest_path": SETUP_MANIFEST.as_posix(),
        "pic_commit": raw.get("pic_commit"),
        "pic_version": raw.get("pic_version"),
        "pic_agent_explain_available": bool(raw.get("pic_agent_explain_available", False)),
    }


def _expected_obligation_block(task: TaskSpec) -> str:
    obligations = "\n".join(f"- {item}" for item in task.expected_obligation_types)
    return obligations or "- none specified"


def build_answer_prompt(task: TaskSpec) -> str:
    return f"""\
{LOCAL_BOUNDARY}

Task ID: {task.task_id}
Title: {task.title}

Task prompt:
{task.prompt}

Expected obligation types:
{_expected_obligation_block(task)}

Answer the task directly. Include any missing assumptions and unresolved
obligations in a clearly labeled section.
"""


def build_self_review_prompt(task: TaskSpec, initial_answer: str) -> str:
    return f"""\
{LOCAL_BOUNDARY}

Review your prior answer for task {task.task_id}. Identify omissions,
unsupported claims, missing assumptions, and obligations that remain unresolved.

Prior answer:
{initial_answer}

Return a concise self-review only. Do not rewrite the full answer yet.
"""


def build_final_prompt(task: TaskSpec, initial_answer: str, self_review: str) -> str:
    return f"""\
{LOCAL_BOUNDARY}

Revise the answer for task {task.task_id} using the self-review. Preserve any
unresolved obligations instead of hiding them.

Task prompt:
{task.prompt}

Initial answer:
{initial_answer}

Self-review:
{self_review}

Return the final answer with clear sections.
"""


def build_pic_repair_prompt(
    *,
    task: TaskSpec,
    initial_answer: str,
    residual_summary: str,
    missing_obligations: list[str],
    accepted: bool,
    operationally_usable: bool,
    settled: bool,
    reasons: list[str],
    recommended_next_commands: list[str],
) -> str:
    missing_block = "\n".join(f"- {item}" for item in missing_obligations) or "- none reported"
    residual = residual_summary or "(no residual summary reported)"
    reasons_block = "\n".join(f"- {item}" for item in reasons) or "- none reported"
    commands_block = (
        "\n".join(f"- {item}" for item in recommended_next_commands) or "- none reported"
    )
    return f"""\
{LOCAL_BOUNDARY}

You are repairing an agent output using a PIC agent-output report. Preserve
unresolved obligations explicitly. Do not claim that PIC proves intelligence or
external-world truth.

Task ID: {task.task_id}
Title: {task.title}

Task prompt:
{task.prompt}

Initial candidate:
{initial_answer}

PIC accepted before repair: {accepted}
PIC operationally usable before repair: {operationally_usable}
PIC settled before repair: {settled}

PIC residual summary:
{residual}

PIC missing obligations:
{missing_block}

PIC reasons:
{reasons_block}

PIC recommended next commands:
{commands_block}

Produce a repaired answer. Include a short "Residuals and obligations preserved"
section that explains what remains unresolved if anything remains unresolved.
"""


class ExperimentRunner:
    def __init__(
        self,
        *,
        config: ExperimentConfig,
        root: Path,
        ollama_client: OllamaClient,
        pic_runner: PicRunner,
        config_path: Path | None = None,
    ) -> None:
        self.config = config
        self.root = root
        self.ollama_client = ollama_client
        self.pic_runner = pic_runner
        self.config_path = config_path

    def run(self) -> Path:
        tasks = load_tasks(self.root / "tasks", max_tasks=self.config.max_tasks)
        run_id = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        run_dir = ensure_dir(self.root / self.config.output_dir / run_id)
        workload = estimate_experiment_workload(
            task_count=len(tasks),
            repair_rounds=self.config.repair_rounds,
            experiment_mode=self.config.experiment_mode,
        )

        manifest: dict[str, Any] = {
            "run_id": run_id,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "config_path": (
                relative_posix(self.config_path, self.root) if self.config_path else None
            ),
            "model": self.config.model,
            "ollama_url": self.config.ollama_url,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "seed": self.config.seed,
            "num_predict": self.config.num_predict,
            "max_tasks": self.config.max_tasks,
            "repair_rounds": self.config.repair_rounds,
            "timeout_seconds": self.config.timeout_seconds,
            "generation_retries": self.config.generation_retries,
            "disable_ollama_thinking": self.config.disable_ollama_thinking,
            "abort_on_generation_error": self.config.abort_on_generation_error,
            "experiment_mode": self.config.experiment_mode,
            "shared_initial_answer_used": self.config.experiment_mode == "shared_initial",
            "pic_profile": self.config.pic_profile,
            "output_dir": self.config.output_dir.as_posix(),
            "task_count": len(tasks),
            "task_ids": [task.task_id for task in tasks],
            "workload_estimate": workload,
            "estimated_ollama_generation_count": workload["ollama_generation_count"],
            "estimated_pic_intake_count": workload["pic_intake_count"],
            "pic_setup": load_pic_setup_metadata(self.root),
            "safety_boundary": "local-only; no cloud APIs; no arbitrary LLM command execution",
        }
        write_json(run_dir / "run_manifest.json", manifest)
        write_json(self.root / "results" / "run_manifest.json", manifest)

        for task in tasks:
            metrics = self._run_task(task=task, run_dir=run_dir)
            write_json(run_dir / task.task_id / "metrics.json", metrics.model_dump(mode="json"))

        return run_dir

    def _generate(self, prompt: str, errors: list[str]) -> str:
        try:
            generation = self.ollama_client.generate(
                model=self.config.model,
                prompt=prompt,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                seed=self.config.seed,
                num_predict=self.config.num_predict,
            )
            return generation.text
        except OllamaError as exc:
            message = f"Ollama generation failed: {exc}"
            errors.append(message)
            if self.config.abort_on_generation_error:
                raise RuntimeError(message) from exc
            return f"ERROR: {message}"

    def _run_task(self, *, task: TaskSpec, run_dir: Path) -> TaskRunMetrics:
        task_dir = ensure_dir(run_dir / task.task_id)
        errors: list[str] = []

        task_yaml = yaml.safe_dump(task.model_dump(), sort_keys=False, allow_unicode=True)
        write_text(task_dir / "task.yaml", task_yaml)

        if self.config.experiment_mode == "shared_initial":
            return self._run_task_shared_initial(
                task=task,
                task_dir=task_dir,
                run_dir=run_dir,
                errors=errors,
            )
        return self._run_task_separate_initial(
            task=task,
            task_dir=task_dir,
            run_dir=run_dir,
            errors=errors,
        )

    def _run_task_separate_initial(
        self,
        *,
        task: TaskSpec,
        task_dir: Path,
        run_dir: Path,
        errors: list[str],
    ) -> TaskRunMetrics:
        initial_prompt = build_answer_prompt(task)
        baseline_initial = self._generate(initial_prompt, errors)
        write_text(task_dir / "baseline_initial.txt", baseline_initial)

        self_review_prompt = build_self_review_prompt(task, baseline_initial)
        baseline_self_review = self._generate(self_review_prompt, errors)
        write_text(task_dir / "baseline_self_review.txt", baseline_self_review)

        final_prompt = build_final_prompt(task, baseline_initial, baseline_self_review)
        baseline_final = self._generate(final_prompt, errors)
        write_text(task_dir / "baseline_final.txt", baseline_final)

        pic_initial = self._generate(initial_prompt, errors)
        initial_report = self.pic_runner.run_intake(
            candidate_text=pic_initial,
            candidate_path=task_dir / "pic_initial_candidate.txt",
            report_path=task_dir / "pic_initial_report.json",
            run_dir=run_dir,
        )

        repair_prompt = build_pic_repair_prompt(
            task=task,
            initial_answer=pic_initial,
            residual_summary=initial_report.residual_summary,
            missing_obligations=initial_report.missing_obligations,
            accepted=initial_report.accepted,
            operationally_usable=initial_report.operationally_usable,
            settled=initial_report.settled,
            reasons=initial_report.reasons,
            recommended_next_commands=initial_report.recommended_next_commands,
        )
        write_text(task_dir / "pic_repair_prompt.txt", repair_prompt)

        pic_repaired = self._generate(repair_prompt, errors)
        write_text(task_dir / "pic_repaired_output.txt", pic_repaired)
        repaired_report = self.pic_runner.run_intake(
            candidate_text=pic_repaired,
            candidate_path=task_dir / "pic_repaired_candidate_for_pic.txt",
            report_path=task_dir / "pic_repaired_report.json",
            run_dir=run_dir,
        )

        if initial_report.error_message:
            errors.append(initial_report.error_message)
        if repaired_report.error_message:
            errors.append(repaired_report.error_message)

        return self._build_task_metrics(
            task=task,
            experiment_mode="separate_initial",
            shared_initial_answer="",
            baseline_initial=baseline_initial,
            baseline_self_review=baseline_self_review,
            baseline_final=baseline_final,
            pic_repaired=pic_repaired,
            initial_report=initial_report,
            repaired_report=repaired_report,
            errors=errors,
        )

    def _run_task_shared_initial(
        self,
        *,
        task: TaskSpec,
        task_dir: Path,
        run_dir: Path,
        errors: list[str],
    ) -> TaskRunMetrics:
        initial_prompt = build_answer_prompt(task)
        shared_initial = self._generate(initial_prompt, errors)
        write_text(task_dir / "shared_initial_answer.txt", shared_initial)
        write_text(task_dir / "baseline_initial.txt", shared_initial)

        self_review_prompt = build_self_review_prompt(task, shared_initial)
        baseline_self_review = self._generate(self_review_prompt, errors)
        write_text(task_dir / "baseline_self_review.txt", baseline_self_review)

        final_prompt = build_final_prompt(task, shared_initial, baseline_self_review)
        baseline_final = self._generate(final_prompt, errors)
        write_text(task_dir / "baseline_final.txt", baseline_final)

        initial_report = self.pic_runner.run_intake(
            candidate_text=shared_initial,
            candidate_path=task_dir / "pic_initial_candidate.txt",
            report_path=task_dir / "pic_initial_report.json",
            run_dir=run_dir,
        )

        repair_prompt = build_pic_repair_prompt(
            task=task,
            initial_answer=shared_initial,
            residual_summary=initial_report.residual_summary,
            missing_obligations=initial_report.missing_obligations,
            accepted=initial_report.accepted,
            operationally_usable=initial_report.operationally_usable,
            settled=initial_report.settled,
            reasons=initial_report.reasons,
            recommended_next_commands=initial_report.recommended_next_commands,
        )
        write_text(task_dir / "pic_repair_prompt.txt", repair_prompt)

        pic_repaired = self._generate(repair_prompt, errors)
        write_text(task_dir / "pic_repaired_output.txt", pic_repaired)
        repaired_report = self.pic_runner.run_intake(
            candidate_text=pic_repaired,
            candidate_path=task_dir / "pic_repaired_candidate_for_pic.txt",
            report_path=task_dir / "pic_repaired_report.json",
            run_dir=run_dir,
        )

        if initial_report.error_message:
            errors.append(initial_report.error_message)
        if repaired_report.error_message:
            errors.append(repaired_report.error_message)

        return self._build_task_metrics(
            task=task,
            experiment_mode="shared_initial",
            shared_initial_answer=shared_initial,
            baseline_initial=shared_initial,
            baseline_self_review=baseline_self_review,
            baseline_final=baseline_final,
            pic_repaired=pic_repaired,
            initial_report=initial_report,
            repaired_report=repaired_report,
            errors=errors,
        )

    def _build_task_metrics(
        self,
        *,
        task: TaskSpec,
        experiment_mode: ExperimentMode,
        shared_initial_answer: str,
        baseline_initial: str,
        baseline_self_review: str,
        baseline_final: str,
        pic_repaired: str,
        initial_report: Any,
        repaired_report: Any,
        errors: list[str],
    ) -> TaskRunMetrics:
        baseline_metrics = compute_baseline_metrics(
            task=task,
            initial_answer=baseline_initial,
            self_review=baseline_self_review,
            final_answer=baseline_final,
        )
        pic_metrics = compute_pic_metrics(
            task=task,
            initial_report=initial_report,
            repaired_report=repaired_report,
            repaired_output=pic_repaired,
        )
        baseline_coverage = float(baseline_metrics["heuristic_obligation_coverage"])
        pic_coverage = float(pic_metrics["heuristic_obligation_coverage"])
        shared_initial_used = experiment_mode == "shared_initial"

        return TaskRunMetrics(
            task_id=task.task_id,
            title=task.title,
            experiment_mode=experiment_mode,
            shared_initial_answer_used=shared_initial_used,
            shared_initial_answer_length=len(shared_initial_answer) if shared_initial_used else 0,
            baseline_final_length=int(baseline_metrics["final_answer_length"]),
            pic_repaired_output_length=len(pic_repaired),
            baseline_obligation_coverage=baseline_coverage,
            pic_obligation_coverage=pic_coverage,
            obligation_coverage_delta=pic_coverage - baseline_coverage,
            pic_missing_obligation_count_before=int(pic_metrics["missing_obligation_count_before"]),
            pic_missing_obligation_count_after=int(pic_metrics["missing_obligation_count_after"]),
            pic_missing_obligation_delta=int(pic_metrics["missing_obligation_delta"]),
            pic_residual_charge_delta=float(pic_metrics["residual_charge_delta"]),
            pic_accepted_after=bool(pic_metrics["pic_accepted_after"]),
            pic_operationally_usable_after=bool(pic_metrics["pic_operationally_usable_after"]),
            pic_settled_after=bool(pic_metrics["pic_settled_after"]),
            pic_schema_fields_usable=bool(pic_metrics["pic_schema_fields_usable"]),
            local_phase_score=float(pic_metrics["local_phase_score"]),
            baseline=baseline_metrics,
            pic=pic_metrics,
            errors=errors,
        )
