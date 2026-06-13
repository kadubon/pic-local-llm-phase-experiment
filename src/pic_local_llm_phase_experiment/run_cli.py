from __future__ import annotations

import argparse
from pathlib import Path

from pic_local_llm_phase_experiment.experiment import ExperimentRunner
from pic_local_llm_phase_experiment.ollama_client import OllamaClient, OllamaError
from pic_local_llm_phase_experiment.pic_runner import PicRunner
from pic_local_llm_phase_experiment.task_loader import load_config


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
    args = parser.parse_args(argv)

    root = Path.cwd()
    config = load_config(root / args.config)
    if args.model:
        config.model = args.model
    if args.max_tasks is not None:
        config.max_tasks = args.max_tasks

    ollama_client = OllamaClient(config.ollama_url, timeout_seconds=config.timeout_seconds)
    if not args.skip_ollama_preflight:
        try:
            ollama_client.ensure_model_available(config.model)
        except OllamaError as exc:
            print(exc)
            return 2

    runner = ExperimentRunner(
        config=config,
        root=root,
        ollama_client=ollama_client,
        pic_runner=PicRunner(profile=config.pic_profile, timeout_seconds=config.timeout_seconds),
    )
    run_dir = runner.run()
    print(f"Experiment run complete: {run_dir.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
