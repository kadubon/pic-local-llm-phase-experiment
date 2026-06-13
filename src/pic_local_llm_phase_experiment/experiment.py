from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from pic_local_llm_phase_experiment.metrics import compute_baseline_metrics, compute_pic_metrics
from pic_local_llm_phase_experiment.ollama_client import OllamaClient, OllamaError
from pic_local_llm_phase_experiment.paths import ensure_dir, write_json, write_text
from pic_local_llm_phase_experiment.pic_runner import PicRunner
from pic_local_llm_phase_experiment.schemas import ExperimentConfig, TaskRunMetrics, TaskSpec
from pic_local_llm_phase_experiment.task_loader import load_tasks

LOCAL_BOUNDARY = """\
You are participating in a bounded local research experiment.
Do not claim real ASI, autonomous superintelligence, oracle truth, physical-world
outcomes, or real-world capability acceleration. Do not request cloud APIs,
secrets, browsing, or arbitrary command execution. Produce useful reviewable text.
"""


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
    settled: bool,
) -> str:
    missing_block = "\n".join(f"- {item}" for item in missing_obligations) or "- none reported"
    residual = residual_summary or "(no residual summary reported)"
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
PIC settled before repair: {settled}

PIC residual summary:
{residual}

PIC missing obligations:
{missing_block}

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
    ) -> None:
        self.config = config
        self.root = root
        self.ollama_client = ollama_client
        self.pic_runner = pic_runner

    def run(self) -> Path:
        tasks = load_tasks(self.root / "tasks", max_tasks=self.config.max_tasks)
        run_id = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        run_dir = ensure_dir(self.root / self.config.output_dir / run_id)

        manifest: dict[str, Any] = {
            "run_id": run_id,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "model": self.config.model,
            "ollama_url": self.config.ollama_url,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "seed": self.config.seed,
            "num_predict": self.config.num_predict,
            "max_tasks": self.config.max_tasks,
            "repair_rounds": self.config.repair_rounds,
            "pic_profile": self.config.pic_profile,
            "task_count": len(tasks),
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
            return f"ERROR: {message}"

    def _run_task(self, *, task: TaskSpec, run_dir: Path) -> TaskRunMetrics:
        task_dir = ensure_dir(run_dir / task.task_id)
        errors: list[str] = []

        task_yaml = yaml.safe_dump(task.model_dump(), sort_keys=False, allow_unicode=True)
        write_text(task_dir / "task.yaml", task_yaml)

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
            settled=initial_report.settled,
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

        return TaskRunMetrics(
            task_id=task.task_id,
            title=task.title,
            baseline=baseline_metrics,
            pic=pic_metrics,
            errors=errors,
        )
