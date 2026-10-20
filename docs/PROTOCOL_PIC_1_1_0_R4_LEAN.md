# R4 lean-import cost replication

This separate technical replication is specified during R4 confirmatory
inference, before any reuse benchmark outcomes or model grades are inspected.
Source inspection showed that the frozen R4 cost harness imports PIC even
for its generic backend. R4 remains unchanged and its planned reuse benchmark
will still execute. This replication does not replace an unfavorable result,
rescore an endpoint, or modify PIC. It isolates cold-start import costs.

Freeze this document, the complete new script, the unchanged R4 fixture/grid
and worker implementation, the R3 generic verifier/PIC adapter, common settings
and installed-PIC map before running. Commit the registration locally. This
is not independently publicly timestamped preregistration.

Use the same real telemetry sizes (16, 4096, 65536), fanouts (1, 8), two
repeats, fixed randomized arm/mode order, trust policy, source schema and
producer/consumer task contracts as R4. There are 24 conditions and exactly
72 planned processes: a producer and cached/no-cache consumers per condition.
Source contents and parameters match R4 up to fresh identifiers. No model
calls, artificial verification delays, downloads, external access or updates.

Each generic child imports only the independent generic verifier and support
modules. It must have no `percolation_inversion_compiler` module in sys.modules.
Each PIC child invokes the original frozen R4 worker and must import PIC.
Generic cache and verification loops duplicate the frozen worker's generic
branch, including source validation, producer pin checks and persistence.
The new wrapper records module-loading state and process IDs after each worker
finishes; output persists before exit in both modes. Core timers begin after
imports, while parent wall includes startup, imports, execution and saved I/O.

Run only after model inference and the original R4 reuse measurement finish.
Allow 1200 seconds total, 90 seconds per child, at most 72 processes and no
retry/resume/overwrite. A failure or timeout remains recorded. No favorable
cell is repeated or omitted. Producer cost is included identically in the
cached and no-cache workflow totals. Preserve all prior artifacts.

Primary purpose is cost attribution, not an additional model efficacy test.
Report every cell/repeat's end-to-end totals, core times, correctness, skipped
calls, actual process status and import checks. Compare PIC caching with its
own no-cache path and separately with generic caching. Do not infer savings
from skipped calls alone. Two repeats cannot establish a general break-even
threshold. Do not subtract estimated startup from old results or pool timing
observations across the original and lean-import harnesses.

Commands, in the existing isolated environment:

```powershell
.venv-pic110/Scripts/python.exe scripts/benchmark_pic110r4_lean.py freeze
# Commit registration and source before executing this separate replication.
.venv-pic110/Scripts/python.exe scripts/benchmark_pic110r4_lean.py run
.venv-pic110/Scripts/python.exe scripts/benchmark_pic110r4_lean.py analyze
```

Raw subprocess inputs, outputs, stderr, caches and PIC records stay in ignored
`results/pic110r4lean/`. Public results contain sanitized timings, identities,
correctness and module-loading flags. They do not authenticate issuer identity,
test autonomous coordination or measure energy. The model/feedback conclusions
continue to use the original R4 fixed protocol and denominators.
