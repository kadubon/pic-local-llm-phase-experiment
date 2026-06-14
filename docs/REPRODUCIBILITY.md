# Reproducibility Guide

This guide describes how to reproduce the v0.1.0 local experiment.

## Requirements

- Python 3.11 or newer
- `uv`
- `git`
- Ollama running locally
- Ollama model `qwen3.5:35b-a3b`

The experiment is local-only. It does not use cloud LLM APIs, API keys, web
browsing, or arbitrary execution of LLM-generated commands.

## Default Config

The default config is `configs/experiment.default.yaml`.

Important v0.1.0 defaults:

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

```bash
uv run python scripts/run_experiment.py --config configs/experiment.default.yaml
uv run python scripts/analyze_results.py --run latest
uv run python scripts/generate_report.py --run latest
```

With the default config, the full run performs approximately:

- `50` local Ollama generations
- `20` PIC intake calls

The v0.1.0 reference run took multiple hours on the local machine used for
release preparation. Runtime will vary by hardware and Ollama configuration.

## Outputs

Generated outputs are ignored by git:

- `results/runs/<run_id>/`
- `results/summary.csv`
- `results/summary.json`
- `reports/experiment_report.md`

The tracked public report is:

- `docs/EXPERIMENT_REPORT_v0.1.0.md`

## Interpreting Reproductions

Reproductions should compare the same classes of metrics, not expect identical
model output bytes. Local Ollama behavior can vary across hardware, driver
state, model packaging, and runtime version.

Strong claims require additional evidence. This repo's default metrics are
diagnostic workflow indicators, not measurements of intelligence, truth,
external-world capability, or ASI.
