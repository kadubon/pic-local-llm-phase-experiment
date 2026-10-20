# Reproduce or reanalyze PIC 1.1.0 R2

R2 is separate from the earlier experiment. All R2 files contain `R2` or
`pic110r2` in their names; raw data is under ignored `results/pic110r2/`.
Do not rerun into an existing R2 panel: the runner refuses overwrites and
automatic retries. Earlier results are never relabeled, resumed or pooled.

## Environment and tasks

Use the same unchanged `.venv-pic110`, official non-editable PIC 1.1.0 wheel
and installed `gemma4:e4b` digest as the protocol. No model download is part
of reproduction. A fresh environment can use the unchanged hash lock:

```powershell
uv venv .venv-pic110 --python 3.14
uv pip install --python .venv-pic110/Scripts/python.exe --only-binary :all: --require-hashes -r configs/requirements.pic110.lock
uv pip install --python .venv-pic110/Scripts/python.exe --no-deps -e .
```

The fixed wheel SHA-256 is
`2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7`.
The existing local wheel is copied read-only from prior setup to R2 setup.
In a fresh checkout, put that verified official wheel in
`results/pic110r2/setup/` before preparing. Verify local Ollama and the exact
configured model digest; another model is a new experiment, not this replication.

`scripts/build_pic110r2_tasks.py` regenerates the twenty public tasks, private
oracle inputs and exhaustive proof audit deterministically. Run it before
freezing, never after seeing model outcomes to select another sample.
Proof-audit counterexamples are not passed to Ollama/PIC. Hand-calculated
answers, deletion witnesses and irrelevant-record invariance are tested.

## Preservation manifest and checks

Before any new work, create an R2 local preservation manifest mapping each
earlier tracked/raw/archive relative filename to its SHA-256 byte digest.
The recorded campaign protects 957 previous files in
`results/pic110r2/setup/preservation_before.json`. For a fresh checkout without
the private prior archive, preserve all available earlier tracked files and
report that narrower coverage rather than inventing unavailable raw artifacts.
The R2 runner checks this manifest before panels and after reanalysis.

```powershell
.venv-pic110/Scripts/python.exe -m compileall -q src scripts tests
.venv-pic110/Scripts/ruff.exe check .
.venv-pic110/Scripts/ruff.exe format --check .
$checkFiles = (Get-ChildItem src/pic_local_llm_phase_experiment/pic110r2*.py).FullName
& .venv-pic110/Scripts/mypy.exe --ignore-missing-imports $checkFiles
.venv-pic110/Scripts/python.exe -m pytest -q
.venv-pic110/Scripts/python.exe scripts/public_safety_audit.py
```

## Real inference and preregistration

Commit the new protocol, tasks, evaluator, proof audit, runner and analysis
locally. Preparation makes one bounded real warmup, then freeze the pilot:

```powershell
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r2_runner prepare
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r2_runner freeze --phase pilot
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r2_runner run --panel pilot
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r2_analysis
```

The pilot gates technical viability, not favorable effect. Do not change tasks,
scoring or prompts because of ceiling/floor or poor PIC actionability. Record
any technical amendment and preserve its failures. Freeze and locally commit
the final protocol before main inference. The recorded protocol was committed
even before pilot inference. With no amendments, create the main manifest:

```powershell
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r2_runner freeze --phase main
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r2_runner run --panel confirmatory
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r2_analysis --export
```

Each task has one common initial and one revision per arm. Limit: 62 actual
attempts including one warmup; planned total is 61. All task calls have the
same context/output, seed, sampling and timeout settings. Keep the one-hour
campaign clock in mind between panels. Stop rules are finite and not waived
to complete a favorable subset. No cloud LLM, model pull, generated code
execution, push or publication is included.

## Offline reanalysis and public limitations

The last analysis command reads only saved raw outputs, frozen oracle data,
diagnostics and records. It makes no inference or PIC calls. It refuses to
grade while a panel is RUNNING. Saved prompt/output hashes and shared initial
identities permit integrity auditing. Unknown flags/costs remain null.

The semantic equivalences, substantive false completion and evidence-completion
secondary endpoint were fixed before the pilot, not chosen after seeing outputs.
Formatting compliance remains separate. The proof audit establishes minimality
only relative to explicit finite domains, not unrestricted external truth.

Sanitized per-task metrics are in `EXPERIMENT_SUMMARY_PIC_1_1_0_R2.json`.
`scripts/report_pic110r2.py --check-public` recomputes primary paired estimates
from those metrics without private raw files. Regrading exact answers requires
private raw access or a fresh run. Repeated offline grading changes tiny
evaluator CPU timings; recorded inference/PIC timings and deterministic estimates
are unchanged. Protocol/source manifests use normalized LF SHA-256, so Windows
line endings do not make Git content unverifiable.
