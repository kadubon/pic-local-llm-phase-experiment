# PIC 1.1.0 publication and offline checks

This guide accompanies publication of the two PIC 1.1.0 campaigns and the
subsequent documentation update on 2026-10-20. The latest completed experiment
is [R2](EXPERIMENT_REPORT_PIC_1_1_0_R2.md). Package version remains 0.2.0; no new
package release is implied. Inference is complete and is not repeated as part
of publication.

## Interpretation and resource accounting

On sixteen confirmatory R2 tasks, generic review A succeeds on eight and PIC
feedback B on nine. Substantive false completion is seven versus six. The
success difference B-A is +6.25 percentage points, conservative 95% interval
[-23.9, +33.8]; exact paired McNemar p=1.0. One A revision loses a correct
initial answer and B retains it. B improves no initial success label. The
experiment does not establish incremental superiority.

Each arm has the same model digest, shared initial answer, revision count,
generation settings and context/output limits. Allocated measured workflow
time is 191.167 s for A and 479.477 s for B (2.51 times A); allocated tokens
are 16,214.5 and 30,115.5. Shared initial cost is split equally; B includes
the PIC feedback path, while observational PIC diagnostics on A are excluded
from A's intervention cost. These accounting choices are fixed in the
[protocol](PROTOCOL_PIC_1_1_0_R2.md). Matched allowed budgets do not constitute
equal realized compute. Energy, monetary cost and continuous GPU usage are
unknown; resource-efficiency superiority is not demonstrated.

The first campaign's strict endpoints, oracle limitations and stopped
historical panel remain visible in its [report](EXPERIMENT_REPORT_PIC_1_1_0.md).
Its post-hoc normalization sensitivity and the prospective R2 endpoints are
distinct analyses. Comparing their scores does not estimate a PIC effect.

## Recorded chronology and immutable evidence

| Local commit | Recorded step |
| --- | --- |
| `501a1d8` | First campaign preregistration before confirmatory inference |
| `bff2907` | First campaign results, stopped panel and oracle audit |
| `bcff157` | R2 protocol, tasks, scoring, proofs and tests before pilot inference |
| `93edf59` | R2 pilot gate and confirmatory freeze before main inference |
| `a771ce4` | Completed R2 results and campaign validation |

These are local pre-inference commits, not an independently timestamped public
registration. Publication occurs after outcomes are known. A merge commit
retains the original commit identities and their recorded order.

The recorded reports state that no external publication was performed during
execution. That describes their execution-time state. The later authorized
push/merge and Docs update are separate from inference and scoring. Frozen
protocols, source, tasks, gold, reports, metrics and manifests are retained;
publication does not regenerate or amend the experimental result.

At the end of R2, 957 prior tracked/raw/archive files were byte-identical to
the pre-R2 snapshot. That historical check remains recorded in
[campaign validation](PIC_1_1_0_R2_VALIDATION.json). The subsequent authorized
Docs update changes only `README.md`, `CHANGELOG.md` and `docs/README.md`
among those protected files. All other earlier files, including raw data and
private archives, retain their original bytes. The
[publication validation](PUBLICATION_VALIDATION_PIC_1_1_0.json) records this
distinction without altering the old snapshot.

The [first public manifest](PIC_1_1_0_PUBLIC_MANIFEST.json) and
[R2 public manifest](PIC_1_1_0_R2_PUBLIC_MANIFEST.json) identify recorded files
using SHA-256 after CRLF-to-LF normalization. New publication Docs are outside
those experiment snapshots. Local archive identities are published only as
hashes; archive contents remain private.

## Offline checks from a public checkout

From the repository root, install the isolated environment using the pinned
[dependency lock](../configs/requirements.pic110.lock). These commands install
dependencies, not model weights:

```powershell
uv venv .venv-pic110 --python 3.14
uv pip install --python .venv-pic110/Scripts/python.exe --only-binary :all: --require-hashes -r configs/requirements.pic110.lock
uv pip install --python .venv-pic110/Scripts/python.exe --no-deps -e .
.venv-pic110/Scripts/python.exe scripts/report_pic110r2.py --check-public
.venv-pic110/Scripts/python.exe scripts/reanalyze_pic110_public.py
.venv-pic110/Scripts/python.exe -m pytest -q
.venv-pic110/Scripts/ruff.exe check .
.venv-pic110/Scripts/ruff.exe format --check .
.venv-pic110/Scripts/python.exe scripts/public_safety_audit.py
```

These arithmetic checks use saved sanitized rows and need neither Ollama nor
private responses. They verify the published estimates, not the correctness
of each original answer's grade. The tests verify evaluator behavior and
finite proof logic. Exact regrading requires the retained private responses
or a fresh independent run.

For new inference, follow the [R2 reproduction guide](REPRODUCIBILITY_PIC_1_1_0_R2.md)
in a fresh checkout/result directory with the exact already installed model
digest and verified PIC wheel. Another model is a new protocol. Preserve only
actually available prior artifacts and report that coverage. Do not rerun
the record-producing `validate`, report-rendering or archive commands on the
completed local campaign after updating Docs: its strict pre-R2 byte snapshot
correctly detects the later documentation changes. Use the read-only checks
above for publication validation. Existing raw directories and private ZIPs
are retained without overwriting them.

Public Git content excludes generated raw responses, private environment
details, archives and model weights. The public-safety scan complements
review of the staged files; it is not independent verification of model
provenance or a substitute for answer-level auditing.
