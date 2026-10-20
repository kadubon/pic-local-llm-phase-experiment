# PIC 1.1.0 R3: evidence-bound closed-loop experiment

Execution: **COMPLETED**. Run date: 2026-10-20, Asia/Tokyo. Local only; no external publication.

## Executive summary

Generic A / verifier-ledger B / verifier-PIC C success: 0/16, 15/16, 13/16. Primary C-B risk difference: -12.50 pp; conservative 95% interval [-41.95, 22.88] pp. Utility judgment: **HARM_OBSERVED**. Running a real integration is not evidence of incremental PIC utility.

## Research questions

RQ1 evidence acquisition (B-A); RQ2 incremental PIC (primary C-B); RQ3 model false completion and final admission; RQ4 valid evidence reuse; RQ5 missing, stale, conflicting, altered and context-incompatible boundaries. No R2 data are pooled. This is a finite synthetic intervention on one model/seed.

## Environment and exact identities

Baseline main: `ca788ca800b58b00995e056ecde05b389e18077c`; clean before changes. PIC 1.1.0 non-editable official wheel SHA-256 `2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7`. All 617 installed payload files match that wheel; installed-map SHA-256 `c317caa37d63f5769d813785711dcc537be0ca4afddd110dc7375863497f0794`.

Model `gemma4:e4b`, digest `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`, 7.5B GGUF Q4_K_M. Its local validation parent is an observed package label, not authenticated vendor provenance. Ollama 0.35.0, Python 3.14.7, unchanged isolated environment. CPU Ryzen 7 8840HS, 8 cores/16 threads, RAM 66,363,183,104 bytes. CPU/RAM snapshots and Ollama timing/token metadata are saved; no continuous GPU/energy/FLOP/monetary measurement. No model download, cloud inference or external lookup.

## PIC integration capability matrix

| Feature | Installed 1.1.0 observation |
| --- | --- |
| native_numerical_telemetry_trace_archive | AVAILABLE; explicit finite semantic function calls |
| evidence_verify_discharge | AVAILABLE; metadata and content hash checks, not automatic domain evaluation |
| runtime_resolve_evidence_step | AVAILABLE; finite route discharge and residual tracking |
| packet_promotion | AVAILABLE; development identity policy; no production issuer authentication |
| exact_receiver_match | EXTERNAL; native packet check only requires a nonempty receiver family |
| trusted_source_hash_and_scope | EXTERNAL; pinned by the common B/C orchestrator |
| TTL | Packet expiration AVAILABLE; envelope TTL requires common external policy |
| route_discovery | EXTERNAL fixed mapping; no autonomous discovery claimed |
| real_autonomous_producer_consumer_agents | UNSUPPORTED in this design; logical roles only |
| production_signed_identity_attestation | UNSUPPORTED in this experiment; no invented signatures |

The native functions really execute finite numeric, error, event-order and archive-domain predicates. Route resolution does not execute those functions. Production content-reference envelope validation and development packet identity policy are deliberately separate. The orchestrator supplies the route mapping and trust/recipient/task binding. Native/local settlement, resolution scope, packet usability and global runtime status retain their original meanings.

## Independent verifier implementation

Four layers separate authoritative finite sources, the standard-library domain verifier/common typed ledger, actual PIC SDK/CLI evidence/runtime operations, and an independent exact-rational/index oracle. Trusted source hashes, issuer, task grants, scope, TTL and recipient are checked against pre-inference pins. A newly rehashed forgery cannot replace that authority. Hash agreement is not cryptographic issuer authentication or external-world truth. Private gold is isolated from the model/PIC normal inputs. Hand outcomes, boundary cases, adversarial and metamorphic tests precede inference.

## Experimental design and preregistration

Four pilot and sixteen new confirmatory tasks; four families. Seven confirmatory tasks permit supported definite decisions, including four proved violations; nine require holding. One shared initial and one A/B/C revision, identical digest/seed/context/output caps; balanced Latin arm orders fixed in advance. A sees no authoritative observations. B/C share the same actual receipt; C adds actual native/PIC fields. Prompt lengths and measured compute differ. The full protocol and freeze manifests are linked below.

Local preregistration precedes inference but is not independently timestamped third-party registration. The base preservation snapshot predates code changes. Native predicate rejection can establish a supported negative determination; it is distinct from missing/untrusted evidence. Source specifications/observations, delivered faults, trusted provenance and private gold are separate artifacts.

## Pilot findings

Execution: COMPLETED. Pilot success A/B/C: 0/3/4 out of four each. Pilot is excluded from every primary estimate. The technical gate concerns operation, propagation, isolation and budget, not effect size. No favorable-case selection is permitted.

## Confirmatory results

| Endpoint | A | B | C |
| --- | ---: | ---: | ---: |
| Independent success | 0/16 | 15/16 | 13/16 |
| Unsupported model completion (observable) | 0/16 | 0/16 | 0/16 |
| Unsupported gate admissions | 0/16 | 0/16 | 0/16 |
| Supported completion yield | 0/7 | 7/7 | 7/7 |
| Correct holding | 0/9 | 8/9 | 6/9 |
| Format compliance | 16/16 | 16/16 | 16/16 |
| Exact task obligations | 0/16 | 16/16 | 15/16 |

A's gate admits schema-valid declarations without certifying evidence. B/C apply the same real evidence/conclusion gate; C additionally requires protected PIC readiness. Citation-only failures are separate from substantive false completion when actual adequate B/C observations exist. Missing or untyped completion flags are unknown, never safe zeros.

## Statistical uncertainty

| Contrast / endpoint | Difference | Conservative 95% interval | Wins / ties / losses | Exact McNemar p |
| --- | ---: | --- | --- | ---: |
| C_minus_B / success | -12.50 pp | [-41.95, 22.88] pp | 0 / 14 / 2 | 0.5 |
| C_minus_B / unsupported_completion | 0.00 pp | [-23.96, 23.96] pp | 0 / 16 / 0 | 1.0 |
| C_minus_B / gate_unsupported_completion | 0.00 pp | [-23.96, 23.96] pp | 0 / 16 / 0 | 1.0 |
| C_minus_B / supported_completion_yield | 0.00 pp | [-46.53, 46.53] pp | 0 / 7 / 0 | 1.0 |
| B_minus_A / success | 93.75 pp | [42.25, 99.92] pp | 15 / 1 / 0 | 6.103515625e-05 |
| B_minus_A / unsupported_completion | 0.00 pp | [-23.96, 23.96] pp | 0 / 16 / 0 | 1.0 |
| B_minus_A / gate_unsupported_completion | 0.00 pp | [-23.96, 23.96] pp | 0 / 16 / 0 | 1.0 |
| B_minus_A / supported_completion_yield | 100.00 pp | [6.94, 100.00] pp | 7 / 0 / 0 | 0.015625 |

Exact paired construction uses Bonferroni 97.5% discordance intervals. Paired and whole-family bootstrap intervals, degeneration flags, unknown-pair planned-denominator bounds and Wilson arm intervals are in machine-readable results. A zero-width bootstrap does not demonstrate equivalence. Four authored families and single-source producer/consumer dependencies limit effective independent information; producer rows are not additional task outcomes. No multiplicity-adjusted joint superiority claim is made.

## Per-family results

| Family | A success | B success | C success |
| --- | ---: | ---: | ---: |
| numerical | 0/4 | 4/4 | 4/4 |
| reuse | 0/4 | 4/4 | 4/4 |
| telemetry | 0/4 | 4/4 | 3/4 |
| trace | 0/4 | 3/4 | 2/4 |

## Evidence provenance and reuse

Confirmatory valid cache hits: 1/4; independent domain calls skipped: 1; native PIC calls skipped: 2. Reused verified packet references: 1. Both B/C reuse the same validated receipt; the PIC packet link is not independently discovered semantic evidence.

| Consumer | Valid hit | Generic cached / no-cache seconds | PIC cached / no-cache seconds | B/C supported output |
| --- | --- | ---: | ---: | --- |
| r3_reuse_02 | False | 0.000119 / 0.000045 | 0.011377 / 0.009542 | B=False, C=False |
| r3_reuse_03 | False | 0.000200 / 0.000054 | 0.019522 / 0.010303 | B=False, C=False |
| r3_reuse_01 | True | 0.000175 / 0.000058 | 0.011076 / 0.008402 | B=True, C=True |
| r3_reuse_04 | False | 0.000112 / 0.000039 | 0.010014 / 0.009033 | B=False, C=False |

Logical producer/consumer roles run in one process. A prior-date producer validity query is a retrospective finite query, not a past autonomous execution. Consumer policies are identical in B/C. Current PIC expiration may already reject an expired producer packet. No-cache comparators execute real checks without model calls. One timing per case and very cheap predicates cannot establish robust time/energy savings; fewer calls alone is not an efficiency result.

## False completion and promotion audit

Ten deterministic attack cases: PASS, actual PIC, zero mocks. Raw route accepts 7/10; raw packet promotion accepts 6/10. Common B and protected C gates admit 2/10 and 2/10, including the valid positive and proved negative only. These counts include intentionally invalid evidence probes; raw acceptance is not a protected task success.

Confirmatory raw routes accept 12/16; protected C readiness 7/16. Global final C statuses: {(False, False): 16}. Per-source native results, raw/protected discharge, ledgers, packet decisions and lost obligations are retained in the summary. Exact recipient, source authority and task binding are external defenses common to B/C, not PIC-alone findings.

## Resource accounting

| Arm | Allocated measured seconds | Model seconds | Shared verifier seconds | PIC seconds | Allocated input / output tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 151.759 | 151.759 | 0.000000 | 0.000000 | 11280.666666666666 / 1371.0 |
| B | 177.189 | 177.188 | 0.001214 | 0.000000 | 12415.666666666666 / 1412.0 |
| C | 362.076 | 361.527 | 0.001214 | 0.546977 | 26412.666666666668 / 1441.0 |

One third shared initial per arm; half common independent verification per B/C; C includes producer/consumer and final PIC. No-cache diagnostic excluded; allocated sums omit I/O/orchestration.

C/B allocated time ratio: 2.0434442647704194. Actual campaign calls including warmup: 81; planned task calls: 80. Actual input/output tokens including warmup: 63120/5258. Warmup time: 20.396992599999976 s. Confirmatory panel wall: 693.7479806000001 s. Observed task states: {'OK': 80}. Energy, money, FLOPs and continuous GPU use are null. Allocation sums exclude I/O/orchestration and do not equal observed wall time. Prefix caching/background activity is recorded but uncontrolled.

## Negative results and missingness

Incremental PIC judgment: HARM_OBSERVED. B-A success difference: 93.75 pp, interval [42.25, 99.92] pp. Unknown completion counts A/B/C: 0/0/0. All planned tasks remain in success/yield denominators. No retry, task replacement, effect-driven extension or model substitution is used. Completion of the campaign is distinct from proof of utility; non-significance is distinct from equivalence.

## Threats to validity

Small authored finite dataset, seven determinable cases, one model/digest/seed/host, explicit verdict receipts that may produce a ceiling, synthetic trusted authority, no independently validated benchmark or cryptographic issuer roots, logical rather than autonomous roles, retrospective producer validity query, related templates, unequal realized prompt costs, no background-load/cache isolation, one timing per no-cache comparison, and no external-world actions. C combines native verification and management/formatting; their individual effects are not identified. A has no acquired observations, so B-A mainly tests evidence access and controlled integration rather than intrinsic reasoning improvement. Unmeasured costs are not zero.

## Reproducibility and preservation

Preservation: PASS, 1832 prior files byte-identical. Raw inputs/responses and PIC outputs remain private; sanitized public rows reproduce statistics without the model. Source/protocol freezes use normalized LF hashes, raw evidence uses exact canonical byte hashes. Public file identities and validation are separate artifacts. Local commits are not third-party preregistration.

[Protocol](PROTOCOL_PIC_1_1_0_R3.md), [reproduction](REPRODUCIBILITY_PIC_1_1_0_R3.md), [summary](EXPERIMENT_SUMMARY_PIC_1_1_0_R3.json), [integration](PIC_1_1_0_R3_INTEGRATION.json), [validation](PIC_1_1_0_R3_VALIDATION.json).

## Implications for PIC and collective intelligence research

This tests explicit finite verification plus evidence/runtime management in a role-separated workflow. It can show which checks are native and which are orchestrator-supplied, and whether verified evidence survives reuse. It cannot show emergence of collective intelligence, independent agent discovery, multi-agent complementarity, real-world truth acquisition, scalable trust, capability self-improvement or external resource acceleration. A functioning packet format and local promotion are mechanisms, not observations of collective intelligence.

## Final bounded Go / No-Go assessment

Assessment: HARM_OBSERVED. A positive next-stage utility claim requires a reliable C-B benefit jointly assessed with safety, supported yield and actual cost. This run alone does not authorize scaling or deployment. If no conservative incremental benefit is supported, retain this result and pause the efficacy claim; a separately preregistered next experiment would need an identified mechanism and workloads where verification/reuse cost matters, without weakening B. Unsupported autonomous-agent/production-identity claims remain outside scope.

## Post-run descriptive endpoint audit

The frozen composite loss is narrower than general performance harm: B/C
decision labels are both correct on 16/16 and supported yield is 7/7. Two
C-only errors concern a draft citation or an extra unresolved label on holding
outputs. A's zero primary score includes noncanonical free-text obligations,
despite explicit uncertainty disclosure. See the
[descriptive audit](PIC_1_1_0_R3_ENDPOINT_AUDIT.md) for the unchanged primary
labels and their component interpretation. It also clarifies gold hashing
versus semantic access. This post-hoc description does not alter the protocol,
statistics, failure retention or preregistered judgment.
