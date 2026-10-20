# Reproduce or reanalyze R4

Use the unchanged PIC 1.1.0 wheel and model digest in the
[protocol](PROTOCOL_PIC_1_1_0_R4.md), Python 3.14 and existing hash-locked
environment. No model download or package update is performed by these commands.
Use a fresh checkout/result directory for new inference. Never replace an
existing panel, freeze or archive. A public clone lacks the recorded private
archives and must report its actual narrower preservation coverage.

Before adding R4 code, record the clean baseline, exact-byte hashes of existing
tracked files plus available `results/`, `reports/`, `external/` artifacts,
the matching 617 installed PIC wheel files, Python/Ollama/model identities in
ignored `results/pic110r4/setup/`. The recorded pre-code coverage was 2,884.
Save `preservation_before.json`, `installed_pic_hashes.json`, `inspection.json`.
This setup has no inference. The original wheel remains under ignored
`results/pic110r2/setup/`. No change to PIC is permitted.

In the prepared environment, first build the five new profile identities
(cases, gold, schedule, config, sanitized inspection). The task builder creates
cases/gold/schedule/config and refuses overwrites:

```powershell
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_tasks
.venv-pic110/Scripts/python.exe -m pytest -q
.venv-pic110/Scripts/ruff.exe check .
.venv-pic110/Scripts/ruff.exe format --check .
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_runner freeze --phase pilot
# Commit complete methods and pilot freeze locally before the next command.
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_runner prepare
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_runner run --panel pilot
# Record technical gate without inspecting model effect scores.
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_runner freeze --phase main
# Commit main freeze before the next command; do not change methods based on pilot outcomes.
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_runner run --panel confirmatory
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_reuse run
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_analysis
```

For a clone with existing fixtures, compare `dataset()` against `cases.json`
rather than rebuilding it. Prepare private gold with independent `expected()`
and record schedule/config before freezing. Installed-PIC integrity checks
are full byte checks, not a version-string substitution. Actual CLI/SDK
integration was established in R3 and real SDK calls are exercised in R4 tests.

Public arithmetic from sanitized rows needs no model, private raw responses
or actual PIC execution:

```powershell
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_analysis --check-public
.venv-pic110/Scripts/python.exe -m pytest -q
.venv-pic110/Scripts/ruff.exe check .
.venv-pic110/Scripts/ruff.exe format --check .
.venv-pic110/Scripts/python.exe -m compileall -q src scripts tests
$checkFiles = (Get-ChildItem src/pic_local_llm_phase_experiment/pic110r4*.py).FullName
& .venv-pic110/Scripts/mypy.exe --ignore-missing-imports $checkFiles
.venv-pic110/Scripts/python.exe scripts/public_safety_audit.py
```

Arithmetic checks are not answer-level regrading. Exact regrading requires
private answers and frozen source contexts. Reuse rows expose parent/core
timings and exact call reductions, not a fabricated energy estimate. All
physical subprocess and model attempts remain recorded, including failures.
The summary distinguishes shared inference replay from independent samples and
standalone workflow estimates from actual physical wall time.
