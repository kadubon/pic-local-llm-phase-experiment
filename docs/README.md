# Documentation Index

Start with the completed R3 comparison. The experiment profiles below have
different tasks, endpoints and execution status; their results are not pooled.

| Profile | Recorded status | Entry points |
| --- | --- | --- |
| PIC 1.1.0 R3 | Pilot 4/4; confirmation 16/16 completed; three arms sharing initial answers | [Report](EXPERIMENT_REPORT_PIC_1_1_0_R3.md), [protocol](PROTOCOL_PIC_1_1_0_R3.md), [reproduction](REPRODUCIBILITY_PIC_1_1_0_R3.md) |
| PIC 1.1.0 R2 | Pilot 4/4; confirmation 16/16 completed | [Report](EXPERIMENT_REPORT_PIC_1_1_0_R2.md), [protocol](PROTOCOL_PIC_1_1_0_R2.md), [reproduction](REPRODUCIBILITY_PIC_1_1_0_R2.md) |
| First PIC 1.1.0 campaign | Confirmation 12/12 completed; historical panel stopped and incomplete; oracle limitations recorded | [Report](EXPERIMENT_REPORT_PIC_1_1_0.md), [protocol](PROTOCOL_PIC_1_1_0.md), [reproduction](REPRODUCIBILITY_PIC_1_1_0.md) |
| Historical v0.2.0 | Completed shared-initial reference run; heuristic endpoints | [Report](EXPERIMENT_REPORT_v0.2.0.md), [audit](PUBLIC_SAFETY_AUDIT_v0.2.0.md) |
| Historical v0.1.0 | Completed separate-initial reference run; heuristic endpoints | [Report](EXPERIMENT_REPORT_v0.1.0.md), [audit](PUBLIC_SAFETY_AUDIT_v0.1.0.md) |

R3 compares review A, independent verifier plus strong generic ledger B, and
the same verifier/evidence plus actual PIC C. Composite success is 0/16,
15/16 and 13/16. The primary C-B difference is -12.5 percentage points,
conservative 95% interval [-41.95, +22.88], exact McNemar p=0.5. Both B/C have
correct decision labels on all sixteen and supported completion yield 7/7.
The two C-only failures are citation/obligation-contract errors on holding
outputs; required obligations remain visible and no arm declares an unsupported
completion. The predeclared `HARM_OBSERVED` label describes point degradation
of the composite, without establishing general or statistically conclusive harm.

A always discloses missing observations, but uses free text instead of the
required obligation IDs. Its zero composite success must be read alongside
its nine correct UNKNOWN decisions. B-A combines actual evidence acquisition,
explicit verdict feedback and machine-contract adherence. The
[post-hoc endpoint audit](PIC_1_1_0_R3_ENDPOINT_AUDIT.md) explains this without
changing the frozen scores.

Allocated workflow seconds are A 151.759, B 177.189 and C 362.076: C/B=2.043.
Allowed generation limits match, while realized prompts, tokens and time differ.
One valid main reuse case saves verifier calls but no measured time. A small
authored benchmark, one model/seed/host, explicit verdict receipts, cheap finite
predicates and synthetic trust roots limit generalization. Raw PIC packet
acceptance is distinct from the common outer gate, which rejects all eight
invalid integration cases. PIC's incremental efficacy, safety or resource
advantage is not demonstrated. Independent agents and production identity
assurance remain untested. See the report for the full boundaries and costs.

## R3 evidence and provenance

- [Sanitized metrics and all 80 task rows](EXPERIMENT_SUMMARY_PIC_1_1_0_R3.json)
- [Recorded research navigation](README_PIC_1_1_0_R3.md) and [descriptive endpoint audit](PIC_1_1_0_R3_ENDPOINT_AUDIT.md)
- [Pilot gate](PIC_1_1_0_R3_PILOT_GATE.json), [pilot freeze](PIC_1_1_0_R3_PREREG_PILOT.json), [main freeze](PIC_1_1_0_R3_PREREG_MAIN.json)
- [Installed-wheel inspection](PIC_1_1_0_R3_INSPECTION.json) and [actual native/CLI integration and adversarial cases](PIC_1_1_0_R3_INTEGRATION.json)
- [Operation counts](PIC_1_1_0_R3_OPERATION_COUNTS.json) and [preregistered judgment](PIC_1_1_0_R3_JUDGMENT.json)
- [Campaign validation](PIC_1_1_0_R3_VALIDATION.json) and [post-analysis preservation](PIC_1_1_0_R3_POST_ANALYSIS_VALIDATION.json)
- [Public file identities](PIC_1_1_0_R3_PUBLIC_MANIFEST.json) and [private archive identity](PIC_1_1_0_R3_PRIVATE_ARCHIVE_IDENTITY.json)
- [Publication chronology, read-only checks and snapshot handling](PUBLICATION_PIC_1_1_0_R3.md), with [publication validation](PUBLICATION_VALIDATION_PIC_1_1_0_R3.json)

## R2 results and evidence

R2 success is A 8/16 versus B 9/16. The conservative 95% interval for B-A is
[-23.9, +33.8] percentage points. The one discordance reflects A losing an
initially correct answer; B repairs no initial success failure. Measured
allocated workflow time is 191.2 s versus 479.5 s. These observations do not
establish PIC superiority or a resource-efficiency advantage.

R2 prospectively defines citation/type equivalence, grades format separately,
and derives sufficient minimal evidence proofs by enumerating finite worlds.
The model digest and generation limits are matched; realized prompt tokens and
runtime differ. See the report for endpoint definitions, costs and limitations.

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
