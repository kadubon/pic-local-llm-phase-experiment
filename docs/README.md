# Documentation Index

Start with the completed R2 comparison. The experiment profiles below have
different tasks, endpoints and execution status; their results are not pooled.

| Profile | Recorded status | Entry points |
| --- | --- | --- |
| PIC 1.1.0 R2 | Pilot 4/4; confirmation 16/16 completed | [Report](EXPERIMENT_REPORT_PIC_1_1_0_R2.md), [protocol](PROTOCOL_PIC_1_1_0_R2.md), [reproduction](REPRODUCIBILITY_PIC_1_1_0_R2.md) |
| First PIC 1.1.0 campaign | Confirmation 12/12 completed; historical panel stopped and incomplete; oracle limitations recorded | [Report](EXPERIMENT_REPORT_PIC_1_1_0.md), [protocol](PROTOCOL_PIC_1_1_0.md), [reproduction](REPRODUCIBILITY_PIC_1_1_0.md) |
| Historical v0.2.0 | Completed shared-initial reference run; heuristic endpoints | [Report](EXPERIMENT_REPORT_v0.2.0.md), [audit](PUBLIC_SAFETY_AUDIT_v0.2.0.md) |
| Historical v0.1.0 | Completed separate-initial reference run; heuristic endpoints | [Report](EXPERIMENT_REPORT_v0.1.0.md), [audit](PUBLIC_SAFETY_AUDIT_v0.1.0.md) |

R2 success is A 8/16 versus B 9/16. The conservative 95% interval for B-A is
[-23.9, +33.8] percentage points. The one discordance reflects A losing an
initially correct answer; B repairs no initial success failure. Measured
allocated workflow time is 191.2 s versus 479.5 s. These observations do not
establish PIC superiority or a resource-efficiency advantage.

R2 prospectively defines citation/type equivalence, grades format separately,
and derives sufficient minimal evidence proofs by enumerating finite worlds.
The model digest and generation limits are matched; realized prompt tokens and
runtime differ. See the report for endpoint definitions, costs and limitations.

## R2 evidence and provenance

- [Sanitized metrics and per-answer rows](EXPERIMENT_SUMMARY_PIC_1_1_0_R2.json)
- [Pilot gate](PIC_1_1_0_R2_PILOT_GATE.md), [pilot freeze](PIC_1_1_0_R2_PREREG_PILOT.json), [main freeze](PIC_1_1_0_R2_PREREG_MAIN.json)
- [Initial-to-revision transitions](PIC_1_1_0_R2_INITIAL_TRANSITIONS.json) and [obligation audit](PIC_1_1_0_R2_OBLIGATION_AUDIT.json)
- [Pre-inference proof audit](../tasks/pic110r2/proof_audit.json) and [oracle tests](../tests/test_pic110r2.py)
- [Recorded campaign validation](PIC_1_1_0_R2_VALIDATION.json), [public file identities](PIC_1_1_0_R2_PUBLIC_MANIFEST.json), and [private archive identity](PIC_1_1_0_R2_PRIVATE_ARCHIVE_IDENTITY.json)
- [Publication, offline checks and snapshot handling](PUBLICATION_PIC_1_1_0.md)

## First PIC 1.1.0 campaign evidence

- [Sanitized metrics](EXPERIMENT_SUMMARY_PIC_1_1_0.json) and [attempt ledger](PIC_1_1_0_ATTEMPT_LEDGER.json)
- [Oracle-validity and post-hoc sensitivity audit](PIC_1_1_0_ORACLE_AUDIT.json)
- [Pilot record](PIC_1_1_0_PILOT.md) and [preregistration identities](PIC_1_1_0_PREREG_IDENTITIES.json)
- [Recorded validation](PIC_1_1_0_VALIDATION.json), [public file identities](PIC_1_1_0_PUBLIC_MANIFEST.json), and [source identities](PIC_1_1_0_SOURCE_IDENTITIES.json)

The original strict scores and failed/unrun attempts remain recorded. Its
post-hoc scoring sensitivity does not replace its preregistered endpoints or
count as prospective R2 evidence.

## Historical workflow and publication scope

Use the [historical reproducibility guide](REPRODUCIBILITY.md) for the original
CLI and configurations. The [v0.2.0 rerun template](EXPERIMENT_REPORT_v0.2.0_TEMPLATE.md)
is a template, not an additional completed run. Package version 0.2.0 is
distinct from the PIC runtime version 1.1.0 in the new profiles.

Generated artifacts under `results/` and `reports/` are ignored by Git. Public
files contain sanitized metrics, code, tasks, protocols and recorded identities.
Raw responses, private archives and weights are excluded. Public rows permit
arithmetic reanalysis; exact answer regrading needs private raw access or a
fresh run. Local pre-inference commits are preserved, but were not externally
timestamped preregistrations. Later public availability does not change that
limitation.
