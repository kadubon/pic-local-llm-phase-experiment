from __future__ import annotations

import argparse
from pathlib import Path

from pydantic import ValidationError

from pic_local_llm_phase_experiment.experiment import (
    ExperimentRunner,
    estimate_experiment_workload,
)
from pic_local_llm_phase_experiment.ollama_client import OllamaClient, OllamaError
from pic_local_llm_phase_experiment.paths import ensure_dir
from pic_local_llm_phase_experiment.pic_runner import PicRunner
from pic_local_llm_phase_experiment.schemas import ExperimentConfig
from pic_local_llm_phase_experiment.task_loader import load_config, load_tasks


def _check_output_dir_writable(root: Path, output_dir: Path) -> str | None:
    target = root / output_dir
    probe = target / ".pic-full-run-write-probe"
    try:
        ensure_dir(target)
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return f"Output directory is not writable: {target.as_posix()} ({exc})"
    return None


def _check_short_ollama_generation(
    config_model: str,
    config: ExperimentConfig,
    client: OllamaClient,
) -> str | None:
    try:
        generation = client.generate(
            model=config_model,
            prompt=(
                "Local readiness check. Reply with one short sentence confirming that "
                "the local generation path is working."
            ),
            temperature=0,
            top_p=1,
            seed=config.seed,
            num_predict=32,
        )
    except OllamaError as exc:
        return (
            f"Short Ollama generation preflight failed: {exc}\n"
            "The full experiment was not started because generation did not produce usable text."
        )
    if not generation.text.strip():
        return "Short Ollama generation preflight returned empty text."
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local PIC/LLM phase experiment.")
    parser.add_argument("--config", default="configs/experiment.default.yaml")
    parser.add_argument("--model", help="Override the configured Ollama model.")
    parser.add_argument("--max-tasks", type=int, help="Override the configured task count.")
    parser.add_argument(
        "--skip-ollama-preflight",
        action="store_true",
        help="Skip the local Ollama model availability check.",
    )
    parser.add_argument(
        "--skip-generation-preflight",
        action="store_true",
        help="Skip the short local Ollama generation readiness check.",
    )
    parser.add_argument(
        "--skip-pic-preflight",
        action="store_true",
        help="Skip the local PIC command availability check.",
    )
    args = parser.parse_args(argv)

    root = Path.cwd()
    config_path = root / args.config
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ValueError, ValidationError) as exc:
        print(f"Experiment configuration is not ready: {exc}")
        return 2
    if args.model:
        config.model = args.model
    if args.max_tasks is not None:
        if args.max_tasks <= 0:
            print("Experiment configuration is not ready: --max-tasks must be positive.")
            return 2
        config.max_tasks = args.max_tasks
    try:
        tasks = load_tasks(root / "tasks", max_tasks=config.max_tasks)
    except (FileNotFoundError, ValueError, ValidationError) as exc:
        print(f"Task fixtures are not ready: {exc}")
        return 2

    output_error = _check_output_dir_writable(root, config.output_dir)
    if output_error:
        print(output_error)
        return 2

    ollama_client = OllamaClient(
        config.ollama_url,
        timeout_seconds=config.timeout_seconds,
        generation_retries=config.generation_retries,
        disable_thinking=config.disable_ollama_thinking,
    )
    if not args.skip_ollama_preflight:
        try:
            ollama_client.ensure_model_available(config.model)
        except OllamaError as exc:
            print(exc)
            print("Run `ollama list` and `ollama pull qwen3.5:35b-a3b` if the model is missing.")
            return 2
    if not args.skip_generation_preflight:
        generation_error = _check_short_ollama_generation(config.model, config, ollama_client)
        if generation_error:
            print(generation_error)
            return 2

    pic_runner = PicRunner(profile=config.pic_profile, timeout_seconds=config.timeout_seconds)
    if not args.skip_pic_preflight:
        pic_preflight = pic_runner.preflight(cwd=root)
        if not pic_preflight["ok"]:
            print("PIC preflight failed.")
            for error in pic_preflight["errors"]:
                print(f"- {error}")
            print("Run `uv run python scripts/setup_pic.py`.")
            print("Then run `uv run python scripts/smoke_check.py`.")
            return 2

    workload = estimate_experiment_workload(
        task_count=len(tasks),
        repair_rounds=config.repair_rounds,
    )
    print(
        "Preflight passed. Starting "
        f"{len(tasks)} tasks with about {workload['ollama_generation_count']} local "
        f"Ollama generations and {workload['pic_intake_count']} PIC intakes."
    )

    runner = ExperimentRunner(
        config=config,
        root=root,
        ollama_client=ollama_client,
        pic_runner=pic_runner,
        config_path=config_path,
    )
    try:
        run_dir = runner.run()
    except RuntimeError as exc:
        print(f"Experiment stopped before completion: {exc}")
        print("Partial artifacts remain under results/runs/ for diagnosis.")
        return 1
    print(f"Experiment run complete: {run_dir.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
