# R4 interpretation and instrumentation scope

This explanatory note was prepared during confirmatory execution, before
answer grading. It changes no frozen methods, endpoints, task, model call or
denominator. The preregistered protocol and source remain authoritative.

## What the comparisons identify

G_minimal and P_minimal intentionally replay one exact model answer. Identical
decision scores between them are a structural identity, not statistical
evidence that PIC and generic workflows are equivalent. The meaningful backend
observations are whether the additional PIC path changes admission/readiness,
retains valid negative witnesses, or adds processing cost. Both receive the
same external trust policy and independent verifier. A correct generic gate
already implements this finite proof rule; this design does not test whether
PIC can outperform an absent or deliberately broken generic gate.

P_full versus P_minimal changes the feedback package. It adds actual native
checks, route and framework status, residuals and packet metadata without new
authoritative observations. It does add auxiliary information and length.
Any observed effect cannot be uniquely assigned to verbosity, individual fields
or PIC's internal algorithms. In particular, a framework-wide unresolved
obligation and an aggregate task with one decisive negative witness have
different scopes. The report must retain that distinction.

The evidence-supported primary endpoint still requires valid output schema
and sufficient authorized citations. It is not a measurement of unrestricted
reasoning. Decision correctness and canonical obligation-ID adherence are
reported independently. Supported model output and actual gate admission are
also separate; a correct answer can be withheld by a stricter gate.

The frozen summary contains obligation/citation validity flags. A separate
`scripts/audit_pic110r4_contracts.py`, written before answer grading, supplies
the protocol-declared missing/extra-ID and invalid-reference counts without
changing any grades. Unexpected model strings are hashed for public release.
The inherited answer parser can extract a JSON object from surrounding text;
raw JSON without wrappers is additionally described rather than retroactively
tightening the frozen format endpoint.

## Reuse harness startup

The frozen `pic110r4_reuse` module imports the unchanged R3 PIC adapter at module
load for both backend modes. Thus the generic worker also pays PIC import
startup in this shared harness. Parent wall times are actual instrumented
process times, not a clean cold-start deployment comparison between a PIC-free
generic binary and a PIC binary. No startup time is subtracted or fabricated.
Worker core timers start after imports and expose the repeated verification,
validation, resolution and cache processing separately. Cached versus no-cache
within each backend has the same import path. Both comparisons must be read
alongside the direct PIC-versus-generic core timings and the two-repeat limit.

A [separate lean-import replication](PROTOCOL_PIC_1_1_0_R4_LEAN.md) is registered
before any reuse outcomes are observed. It retains the original benchmark and
runs the same grid with PIC absent from generic child imports. Its results
are reported separately, without pooling or subtracting estimated startup.
Both harnesses measure the implemented, trace-recording workflows. PIC's
adapter saves more SDK/runtime artifacts; these timings do not isolate pure
domain-function CPU cost or prove a lower bound on an optimized integration.

The main inference backend comparison has a different scope: one process
already holds both implementations. Standalone workflow estimates reuse the
observed minimal generation time counterfactually for each backend, rather
than executing an extra model call. They must never be summed and presented
as actual physical compute.

With equal valid hit rates and the same independent verifier, both caches save
the same common verification work. Making that verifier more expensive can
increase the value of caching in both workflows without creating an incremental
PIC advantage. Reusing native PIC results can reduce work introduced by the
PIC path itself; that is distinct from outperforming the generic cache.
Additional PIC utility would need another measured mechanism, such as more
valid reuse at equal safety, better allocation, fewer integration mistakes or
lower audit effort. These are hypotheses, not effects established by the cache
call-count identity. This interpretation is specified before reuse measurement.

## What remains outside this experiment

Sources, authority roots, faults and policy context snapshots are synthetic.
The policy clock is fixed; expiry snapshots do not represent real elapsed
waiting. Cross-process reuse does not make producer/consumer autonomous agents.
The parent pins the persisted producer record; scalable cryptographic identity,
revocation distribution and adversarial cache-store administration are untested.
Verifier implementation is fixed by the installed-wheel checks; rolling
version upgrades of cached results are untested.

PIC route selection, source acquisition and aggregate proof policy are supplied
by the orchestrator. PIC-native planning, adaptive tool selection, population
coordination, human engineering effort and auditability improvements are not
identified by this design. Unknown energy, FLOPs, continuous GPU utilization
and financial costs remain unknown. A zero-width empirical interval cannot
establish equivalence, and eight authored episodes do not define a broad task
population.
