# Reproduce the PIC 1.1.0 comparison

This is an independent experiment profile. The historical setup script,
lockfile, configurations, results and reports remain unchanged. No repository
push or publication is part of these commands. Run from a fresh checkout of
this repository to avoid overwriting this run's preserved local results.

## Installation and verification

Use Python 3.14 and the hash-locked public dependencies. In PowerShell:

```powershell
uv venv .venv-pic110 --python 3.14
uv pip install --python .venv-pic110/Scripts/python.exe --only-binary :all: --require-hashes -r configs/requirements.pic110.lock
uv pip install --python .venv-pic110/Scripts/python.exe --no-deps -e .
.venv-pic110/Scripts/python.exe scripts/setup_pic110.py
```

Only the experiment package is editable. PIC must be non-editable, exactly
1.1.0, imported from this environment's site-packages. The downloaded wheel
must have SHA-256
`2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7`.
`setup_pic110.py` verifies the fixed digest and local Ollama model identity and
runs one bounded real warmup. It never pulls models or changes Ollama settings.

The experiment requires the installed `gemma4:e4b` digest fixed in
`configs/experiment.pic-v1.1.0.yaml`. If absent, setup reports
ENVIRONMENT_BLOCKED. Another model requires an explicitly new protocol and run;
it is not an exact replication. The old qwen3.5 model is absent in this run.
Keep local Ollama reachable at loopback port 11434. No credentials are needed.

## Verify and freeze

```powershell
.venv-pic110/Scripts/python.exe -m compileall -q src scripts tests
.venv-pic110/Scripts/ruff.exe check .
.venv-pic110/Scripts/ruff.exe format --check .
$checkFiles = (Get-ChildItem src/pic_local_llm_phase_experiment/pic110*.py).FullName
& .venv-pic110/Scripts/mypy.exe --ignore-missing-imports $checkFiles
.venv-pic110/Scripts/python.exe -m pytest -q
.venv-pic110/Scripts/python.exe scripts/public_safety_audit.py
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110_runner freeze --phase pilot
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110_runner run --panel pilot
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110_analysis
```

The public tasks and gold files are committed; `scripts/build_pic110_tasks.py`
regenerates them deterministically if needed, before freezing. The runner
never loads gold answers into a prompt or exposes filesystem tools to the
model. Tests include positive/negative independent grading, missing fields,
status separation, evidence failure, schedule balance and a mocked comparison
pipeline. Mock tests do not count as model experiments.

Inspect the four pilot trials for technical viability. Do not select a new
confirmatory sample or change scoring based on which arm won. Preserve and
document any technical failure and amendment. Commit the unchanged final
protocol locally before main inference, then freeze the main manifest:

```powershell
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110_runner freeze --phase main
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110_runner run --panel confirmatory
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110_runner run --panel historical
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110_analysis --export
.venv-pic110/Scripts/python.exe scripts/audit_pic110_oracle.py
.venv-pic110/Scripts/python.exe scripts/probe_pic110_boundary.py
.venv-pic110/Scripts/python.exe scripts/report_pic110.py
.venv-pic110/Scripts/python.exe scripts/validate_pic110.py
```

The campaign has a 5,400-second wall limit, 80 actual-call cap including warmup,
768-token per-task generation ceiling, no retries and fixed memory/input
bounds. The wall clock includes time between panels; do not pause indefinitely
between commands. No automatic resume or overwrite is performed. Incomplete
requests and scheduled not-run trials remain visible. Check panel statuses.
The recorded run stopped in historical task 003 after three consecutive
truncations; its total is 58 real calls. Pilot and confirmation completed;
seven historical tasks were not run. Do not remove this stopping condition
to relabel the recorded campaign as complete. The report renderer describes
this recorded outcome pattern; if a new run differs, its narrative must be
reviewed using the freshly computed JSON rather than copying this report.

## Reanalysis, provenance and privacy

Local raw artifacts are under ignored `results/pic110/`, with separate pilot,
confirmatory and historical directories. A task has initial/A/B request,
response, answer, record and PIC check/intake files. Original outputs are never
executed. `prereg_pilot.json` and `prereg_main.json` contain full schedules and
frozen file hashes; their sidecars verify each manifest. `campaign.json` counts
attempts, budgets and observed tokens. `panel.json` records completion/stopping.

Offline reanalysis uses only those files and the frozen gold file:

```powershell
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110_analysis --export
```

It requires no model/PIC execution. The summary contains aggregate and per-task
metrics and hashes, not raw answer text, prompts or local absolute paths.
Evaluator CPU timings will vary on reanalysis; substantive counts, recorded
inference/PIC timings and deterministic confidence intervals remain unchanged.

For arithmetic reanalysis using only committed sanitized per-task metrics:

```powershell
.venv-pic110/Scripts/python.exe scripts/reanalyze_pic110_public.py
```

The separate `audit_pic110_oracle.py` is a post hoc measurement audit. It exposes
strict citation/type artifacts and an exploratory notation-normalization
sensitivity. It never changes the frozen oracle, primary labels or hypothesis
test. Its exploratory difference is not confirmatory evidence of benefit.

Raw artifacts are deliberately not publicly tracked. A third party can
recompute published aggregate estimates from the sanitized per-task metrics;
independent regrading of these exact raw answers requires private access to
the preserved raw archive or a fresh local run. Hashes establish identity but
cannot by themselves establish answer correctness. No public claim should
imply that withholding raw answers permits complete public regrading.
The original local raw files and exact frozen source bytes are also preserved
in an ignored ZIP archive; `PIC_1_1_0_PRIVATE_ARCHIVE_IDENTITY.json` records its
SHA-256 and CRC check. The archive contains private environment paths and must
not be treated as a publication artifact. `PIC_1_1_0_ATTEMPT_LEDGER.json` lists
all 78 scheduled generation slots, including the three truncations and 21
not-run entries, without raw answer text.

PIC's generic intake includes modeled proxy quantities. These are not observed
LLM cost or speed gains and are not converted into an acceleration certificate.
Runtime comparison needs an evidence-backed measurement contract not supplied
by this fixed one-revision experiment. Unknown monetary/energy costs remain
null. Historical v0.2.0 heuristic scores are not independent correctness scores.
