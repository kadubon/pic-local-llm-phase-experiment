# R4 publication and read-only validation

This guide records the later authorized publication of the completed R4
experiment and its documentation update. Publication adds no model inference,
rescoring or regenerated experimental artifacts. PIC remains 1.1.0 and the
experiment package remains 0.2.0; no package release is made.

## What the result supports

R4 separates backend integration, model feedback and reuse costs. An independent
verifier supplies identical source receipts. G_minimal and P_minimal replay
one minimal-prompt answer through generic and actual PIC backends; P_full
generates a separate answer with the same facts plus detailed PIC feedback.
Backend replay parity is a structural negative control for the model channel.
The primary contrast holds PIC processing and observations fixed but changes
feedback representation, metadata and length together.

All workflows achieve supported decisions 32/32, parsed field/ID contracts
32/32 and supported completion yield 23/23. Unsupported completions and unsafe
admissions are zero. P_full minus P_minimal is 0 percentage points, with
0 wins, 32 ties and 0 losses. Actual answer hashes also match on all main pairs.
Eight episodes are the working blocks. Episode sign-flip p=1.0 and the
degenerate [0,0] empirical bootstrap establish neither equivalence nor absence
of an effect on other tasks. A conservative task independent sensitivity
interval of [-12.80,+12.80] percentage points ignores episode dependence;
it is not the primary population interval.

Standalone workflow estimates are 423.181 seconds for G_minimal, 424.836 for
P_minimal and 2323.767 for P_full. PIC + detail costs 5.470 times PIC + minimal,
with 6.575 times its model input tokens. Minimal integration adds about 1.656
seconds (0.391%) over the generic estimate across 32 cases. Both minimal paths
are allocated the full one observed generation; summing the three estimates
would overcount physical compute. Actual calls are warmup 1, pilot 8 and main
64, all successful without retries/truncation. Main panel wall time is
2753.909 seconds. Prompt length, metadata, representation, prefix caching and
background effects are not separately identified. Timing includes recorded
adapter/trace work. Energy, FLOPs, continuous GPU use and monetary cost are
unknown.

The original reuse benchmark and separately preregistered lean-import
replication each contain 24 conditions and 72 child processes. The original
generic workers import PIC; that record is retained. Lean generic workers
verify no PIC modules loaded. Both backends skip 54 common domain calls per
study; PIC additionally skips 54 checks introduced by its native path.
In the largest lean fanout case, PIC cached/no-cache parent-wall means are
2.819/3.066 seconds, versus generic cached 0.645 seconds. Producer cost, fresh
imports and persisted I/O are included. Two repeats, simple arrays and
uncontrolled OS caching establish no general break-even threshold. These
studies are not pooled. Shared verifier savings are not PIC-specific.

The benchmark is small and authored, with one model/digest/seed/host and
explicit source verdicts; both feedback conditions reach a ceiling. External
orchestration supplies trust/TTL checks, acquisition, aggregate proof rules,
manual routes and cache storage. Final PIC runtime settlement is not the task
oracle. Synthetic identities and fixed policy times do not establish production
assurance. Autonomous planning/agents, real-world evidence acquisition,
engineering effort and auditability benefits remain unmeasured. The observed
composition is usable with minimal feedback; added task, safety or cost value
over this strong generic control is not demonstrated.

## Evaluation disclosures retained alongside the frozen outputs

The inherited frozen parser extracts a JSON object from surrounding text.
All 64 actual main responses are fenced, so raw JSON-only compliance is
0/32 per feedback condition even though parsed contracts pass 32/32. The
[descriptive contract audit](PIC_1_1_0_R4_CONTRACT_AUDIT.json) preserves that
distinction without tightening grades after outcomes.

The frozen secondary backend-yield helper uses all 32 planned cases; protocol
yield and arm tables correctly use 23 determinable cases. Source inspection
disclosed this before answer grading. A separate
[eligible-case audit](PIC_1_1_0_R4_ANALYSIS_AUDIT.json) records 23/23 versus
23/23, difference zero. Do not interpret the old 32-pair interval as a 23-case
yield interval. Frozen code, report and summary are retained, and neither
primary grades nor the protocol denominator change. `decision_correct` in R4
means both the decision and completion flag are correct.

## Chronology and preserved records

| Local commit | Recorded step |
| --- | --- |
| `282548846d44530b57d121c32a9d96fb5a4b0360` | Methods, tasks and pilot freeze before pilot inference |
| `3ab0ebd421b1f5c80fd44b4980e29049d28f11f9` | Technical pilot gate and unchanged main freeze before main inference |
| `e01a60aa51ee0ee2b2dcc13ff4981f4c86133716` | Separate lean-import replication before reuse outcomes and answer grading |
| `74f5793e13a118d94ff29fe48b35853bc713bc8d` | Descriptive raw-contract audit before answer grading |
| `5507cd1c8b1b1d853c12a75ec6835c9aa244ab71` | Secondary denominator disclosure before answer grading |
| `62e6f72aaea735cb01e9ada847a1c1d2124fd822` | Completed results, interpretation, audits and record validation |

These were local commits, not independently timestamped public registrations.
Publication after outcomes does not change that limitation. A merge commit
retains their identities and order. The later publication Docs commit is
separate from those research commits.

At experiment completion, all 2,884 pre-R4 tracked/raw/archive files were
byte-identical, as recorded in [record validation](PIC_1_1_0_R4_RECORD_VALIDATION.json).
Later publication changes only `README.md`, `CHANGELOG.md` and `docs/README.md`
among those files; the remaining 2,881 retain their bytes. All 34 new R4 public
files remain unchanged, including 33 [manifest entries](PIC_1_1_0_R4_PUBLIC_MANIFEST.json)
and the self-excluded manifest. Both freezes retain the same 54 method/input
hashes. The installed 617-file PIC payload, earlier manifests and private raw
records/archives remain intact. This later
[publication validation](PUBLICATION_VALIDATION_PIC_1_1_0_R4.json) records the
three authorized documentation exceptions without weakening or rewriting the
original experiment preservation check.

## Read-only checks from a public checkout

Use the pinned [dependency lock](../configs/requirements.pic110.lock) in an
isolated Python 3.14 environment. With those dependencies already available,
the following checks add no model generations:

```powershell
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r4_analysis --check-public
.venv-pic110/Scripts/python.exe scripts/audit_pic110r4_analysis.py --check-public
.venv-pic110/Scripts/python.exe -m pytest -q
.venv-pic110/Scripts/ruff.exe check .
.venv-pic110/Scripts/ruff.exe format --check .
.venv-pic110/Scripts/python.exe -m compileall -q src scripts tests
$checkFiles = (Get-ChildItem src/pic_local_llm_phase_experiment/pic110r4*.py).FullName
& .venv-pic110/Scripts/mypy.exe --ignore-missing-imports $checkFiles scripts/benchmark_pic110r4_lean.py scripts/audit_pic110r4_contracts.py scripts/audit_pic110r4_analysis.py
.venv-pic110/Scripts/python.exe scripts/public_safety_audit.py
```

Public arithmetic checks use sanitized rows, with no inference or private
responses. They do not independently verify original answer grades. Tests
exercise independent hand, boundary and metamorphic checks, actual PIC
integration and policy gates. Exact regrading and the raw-response audit need
retained private responses and source contexts or a fresh independent run.

For fresh inference follow the [reproduction guide](REPRODUCIBILITY_PIC_1_1_0_R4.md)
and [lean protocol](PROTOCOL_PIC_1_1_0_R4_LEAN.md) in a new checkout/result
directory, reporting actual available artifact coverage. Existing record,
analysis, report, freeze and archive commands must not overwrite completed
outputs. Their strict pre-R4 preservation check correctly detects the three
later navigation edits; use the read-only checks above for publication.

Public Git includes code, synthetic fixtures, protocols, sanitized metrics and
identities. Raw prompts/responses, environment details, SDK traces, private
archives and weights remain excluded. Archive contents remain private;
[primary identity](PIC_1_1_0_R4_PRIVATE_ARCHIVE_IDENTITY.json) and
[lean identity](PIC_1_1_0_R4_LEAN_PRIVATE_ARCHIVE_IDENTITY.json) expose only
recorded hash, size and integrity. Safety scanning and history review do not
authenticate model provenance or independently verify answer grades.
