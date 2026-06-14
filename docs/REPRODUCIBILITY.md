# Reproducibility Guide

This guide describes how to reproduce the local PIC plus Ollama experiment.
v0.1.0 used separate initial answers. v0.2.0 adds a shared-initial mode where
baseline and PIC-assisted branches start from the exact same initial local LLM
answer.

## Requirements

- Python 3.11 or newer
- `uv`
- `git`
- Ollama running locally
- Ollama model `qwen3.5:35b-a3b`

The experiment is local-only. It does not use cloud LLM APIs, API keys, web
browsing, or arbitrary execution of LLM-generated commands.

## Configs

The historical v0.1.0-compatible config is:

```text
configs/experiment.default.yaml
```

It uses `experiment_mode: separate_initial` through the schema default.

The v0.2.0 shared-initial config is:

```text
configs/experiment.shared_initial.yaml
```

Important v0.2.0 defaults:

```yaml
model: qwen3.5:35b-a3b
ollama_url: http://localhost:11434
temperature: 0
top_p: 1
seed: 42
num_predict: 1024
max_tasks: 10
repair_rounds: 1
pic_profile: development
timeout_seconds: 1800
generation_retries: 1
disable_ollama_thinking: true
abort_on_generation_error: true
experiment_mode: shared_initial
```

`disable_ollama_thinking: true` is important for models that stream thinking
tokens separately from answer tokens. This keeps the experiment focused on
answer text and avoids empty answer artifacts.

## Setup

```bash
uv sync
uv run python scripts/setup_pic.py
uv run python scripts/smoke_check.py
```

The smoke check includes a short real Ollama generation. If it fails, do not run
the full experiment yet.

## Full Experiment

For the v0.2.0 shared-initial experiment:

```bash
uv run python scripts/run_experiment.py --config configs/experiment.shared_initial.yaml
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

With the shared-initial config, the full run performs approximately:

- `40` local Ollama generations
- `20` PIC intake calls

For the historical v0.1.0-compatible flow:

```bash
uv run python scripts/run_experiment.py --config configs/experiment.default.yaml
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

With the separate-initial config, the full run performs approximately:

- `50` local Ollama generations
- `20` PIC intake calls

The v0.1.0 reference run took multiple hours on the local machine used for
release preparation. Runtime for v0.2.0 will vary by hardware and Ollama
configuration.

## Outputs

Generated outputs are ignored by git:

- `results/runs/<run_id>/`
- `results/summary.csv`
- `results/summary.json`
- `reports/experiment_report.md`

The tracked public reports are:

- `docs/EXPERIMENT_REPORT_v0.1.0.md`
- `docs/EXPERIMENT_REPORT_v0.2.0.md`

The reusable v0.2.0 report template is:

- `docs/EXPERIMENT_REPORT_v0.2.0_TEMPLATE.md`

## Interpreting Reproductions

Reproductions should compare the same classes of metrics, not expect identical
model output bytes. Local Ollama behavior can vary across hardware, driver
state, model packaging, and runtime version.

Strong claims require additional evidence. This repo's default metrics are
diagnostic workflow indicators, not measurements of intelligence, truth,
external-world capability, or ASI.
