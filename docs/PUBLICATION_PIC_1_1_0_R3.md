# R3 publication and read-only validation

This guide records the later authorized publication of the completed PIC 1.1.0
R3 experiment and its documentation update. Inference and scoring are complete;
publication adds no model generations and does not regenerate scientific
artifacts. Package version remains 0.2.0; this is a research update using PIC
1.1.0, with no new package release.

## Results and interpretation

R3 isolates the incremental workflow contribution of PIC against a strong
generic evidence ledger. A receives no verified observations; B/C receive the
same independent verifier receipt. They share initial answers, model digest,
one revision and generation limits. Four pilot tasks and sixteen confirmatory
tasks were completed: 81 actual generations including warmup, no retries,
errors or truncations. Pilot outcomes are excluded from primary estimates.

| Confirmatory endpoint | A: review | B: verifier + ledger | C: verifier + PIC |
| --- | ---: | ---: | ---: |
| Frozen composite success | 0/16 | 15/16 | 13/16 |
| Correct decision label | 9/16 | 16/16 | 16/16 |
| Supported completion yield | 0/7 | 7/7 | 7/7 |
| Unsupported model completions | 0/16 | 0/16 | 0/16 |
| Allocated workflow seconds | 151.759 | 177.189 | 362.076 |

The primary C-B composite difference is -12.5 percentage points, conservative
95% interval [-41.95, +22.88], paired exact McNemar p=0.5; C has zero wins,
fourteen ties and two losses. The predeclared `HARM_OBSERVED` classification
means observed point degradation of the composite. General harm and incremental
superiority are not statistically established. Both C-only failures retain
correct holding decisions and required obligations; they add a draft citation
or an extra unresolved item. A shared B/C draft-citation error accounts for
another failed holding output. The [descriptive endpoint audit](PIC_1_1_0_R3_ENDPOINT_AUDIT.md)
decomposes these without replacing the frozen endpoint.

A's zero composite score includes failure to copy the prescribed obligation
IDs. It discloses missing observations in free text on all sixteen tasks and
gets nine UNKNOWN decisions right. The secondary B-A gain of +93.75 percentage
points (conservative interval [+42.25, +99.92]) combines evidence acquisition,
explicit verifier verdicts and structured-contract adherence. It does not
demonstrate improved intrinsic reasoning. Zero unsupported completions and
identical supported yield do not establish equivalence or incremental safety.

C/B measured time is 2.043; allocated tokens are about twice B's. Shared initial
cost is split equally across three arms under the frozen accounting rule.
Allowed call/context/output limits match; realized compute does not. Native PIC
processing contributes 0.547 s in main, while most measured added time is in
model processing and C has longer input. Cache/background activity was not
isolated, so prompt length alone is not an established causal explanation.
Energy, continuous GPU utilization, FLOPs and monetary cost are unknown.
One valid main reuse skips one independent domain computation and two native
checks; the measured cached paths are slower than their no-cache comparators.
That single cheap case establishes no timing benefit.

Actual native predicates, metadata routes, packet promotion, task obligation
discharge and global runtime settlement have separate meanings. Four invalid
cases pass raw PIC packet promotion in ten deterministic integration cases.
The common outer trust/context/TTL gate rejects all eight invalid cases in
both workflows; this protection cannot be credited to PIC alone. Trusted
issuer identity is synthetic and pinned, rather than cryptographically
authenticated production identity. Producer/consumer are logical roles in one
process; prior-date validity queries are retrospective checks.

The small authored sample, one model/seed/host, cheap finite predicates and
explicit-verdict receipts limit inference. C jointly changes native processing,
management, feedback representation and prompt length; component effects are
not isolated. Independent agents, collective intelligence and external-world
acquisition are untested. The recorded assessment is No-Go for an efficacy
claim or deployment scaling on this evidence, without asserting universal PIC
ineffectiveness. See the [report](EXPERIMENT_REPORT_PIC_1_1_0_R3.md) and
[fixed protocol](PROTOCOL_PIC_1_1_0_R3.md) for full definitions and uncertainty.
R1, R2 and historical profiles remain separate; their scores are not pooled.

## Chronology and immutable records

| Local commit | Recorded step |
| --- | --- |
| `205233b071acd0b867a8c3dbb10f5e27c49f1bf9` | Protocol, methods, fixtures, tests and pilot freeze before pilot inference |
| `9c266c290b3c03490385a7e249b617ae39a64da1` | Technical-only pilot gate and unchanged main freeze before main inference |
| `ddb2b68c3b23e2e343542e95f5fb696fe7094914` | Completed results, validation and descriptive endpoint audit |

These local pre-inference commits were not independently timestamped public
preregistrations. Publication after outcomes are known does not change that
limitation. The publication uses a merge commit to retain their identities
and order. The later Docs commit is distinguishable from all three research
commits in Git history.

The report, reproduction guide and [recorded R3 navigation](README_PIC_1_1_0_R3.md)
retain their execution-time statements about no publication and unchanged
prior files. A subsequent user instruction authorizes push/merge and Docs
updates. This later operation is documented here, without altering those
historical records, protocols, code, tasks, scoring, reports or metrics.

At R3 completion, all 1,832 files in the pre-R3 tracked/raw/archive snapshot
were byte-identical, as recorded in [campaign validation](PIC_1_1_0_R3_VALIDATION.json).
Later publication changes only `README.md`, `CHANGELOG.md` and `docs/README.md`
among those files; the other 1,829 retain their bytes. All 37 public files
added by the three R3 research commits remain unchanged, including the
36 entries and self-excluded manifest in [public identities](PIC_1_1_0_R3_PUBLIC_MANIFEST.json).
Both pre-inference freezes retain all 51 method/input hashes. Earlier
campaign manifests and private archives also remain intact. The separate
[publication validation](PUBLICATION_VALIDATION_PIC_1_1_0_R3.json) records the
later checks and authorized Docs exceptions; it does not replace experiment
validation or weaken its byte-preservation rule.

## Read-only checks from a public checkout

Use the pinned [dependency lock](../configs/requirements.pic110.lock) in an
isolated Python 3.14 environment. Installation requires package access but
does not download models. With the recorded environment already available,
run from the repository root:

```powershell
.venv-pic110/Scripts/python.exe -m pic_local_llm_phase_experiment.pic110r3_analysis --check-public
.venv-pic110/Scripts/python.exe scripts/report_pic110r2.py --check-public
.venv-pic110/Scripts/python.exe scripts/reanalyze_pic110_public.py
.venv-pic110/Scripts/python.exe -m pytest -q
.venv-pic110/Scripts/ruff.exe check .
.venv-pic110/Scripts/ruff.exe format --check .
.venv-pic110/Scripts/python.exe -m compileall -q src scripts tests
$checkFiles = (Get-ChildItem src/pic_local_llm_phase_experiment/pic110r3*.py).FullName
& .venv-pic110/Scripts/mypy.exe --ignore-missing-imports $checkFiles
.venv-pic110/Scripts/python.exe scripts/public_safety_audit.py
```

Public arithmetic checks need no model, PIC execution or private responses.
They recompute estimates from sanitized rows; they do not independently verify
the original answer grades. The tests check finite predicates, the independent
oracle and runtime boundaries. Exact answer regrading and the descriptive
raw-response audit need retained private responses or a fresh independent run.

For new inference follow the [R3 reproduction guide](REPRODUCIBILITY_PIC_1_1_0_R3.md)
in a fresh checkout/result directory with the exact already installed model
digest and verified noneditable PIC wheel. A public clone has narrower prior
artifact coverage and must report that actual coverage. Do not overwrite the
completed local campaign or invent missing private artifacts. Do not rerun its
record-producing analysis, report, validation, endpoint-append or archive
commands after Docs updates: the strict pre-R3 snapshot correctly detects the
three later changes. Use the read-only checks above for publication.

Public Git contains synthetic fixtures, code, protocols, sanitized rows and
identities. Exact prompts/responses, local environment details, raw SDK/CLI
outputs, private ZIP archives and weights remain excluded. The R3 archive
identity is recorded [as hash and size only](PIC_1_1_0_R3_PRIVATE_ARCHIVE_IDENTITY.json).
Public-safety scanning complements staged/history review and is not external
verification of model provenance or answer grades. No inference is rerun for
the GitHub publication.
