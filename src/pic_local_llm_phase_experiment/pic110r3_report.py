"""Render the fixed R3 report structure from saved observations, without inference."""

from __future__ import annotations

# Tables and literal report paragraphs are intentionally long.
# ruff: noqa: E501
from collections import Counter

from pic_local_llm_phase_experiment.pic110r3_common import OUT, ROOT, read, write


def interval(pair: dict) -> str:
    value = pair.get("conservative_exact_95_ci")
    return "unknown" if value is None else f"[{100 * value[0]:.2f}, {100 * value[1]:.2f}] pp"


def render() -> None:
    data = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R3.json")
    main = data["panels"]["confirmatory"]
    arms = main["arms"]
    comparisons = main["comparisons"]
    cb = comparisons["C_minus_B"]
    ba = comparisons["B_minus_A"]
    ev = [e for e in data["evidence"] if e["panel"] == "confirmatory" and e["status"] == "OBSERVED"]
    reuse = [e for e in ev if e["family"] == "reuse"]
    integration = read(ROOT / "docs/PIC_1_1_0_R3_INTEGRATION.json")
    inspection = read(OUT / "setup/inspection.json")
    cost = main["costs"]
    success_ci = cb["success"].get("conservative_exact_95_ci")
    false_ci = cb["unsupported_completion"].get("conservative_exact_95_ci")
    supported = bool(success_ci and success_ci[0] > 0 or false_ci and false_ci[1] < 0)
    harmful = (
        arms["C"]["success"] < arms["B"]["success"]
        or arms["C"]["gate_unsupported_completion"] > arms["B"]["gate_unsupported_completion"]
        or arms["C"]["supported_yield_count"] < arms["B"]["supported_yield_count"]
    )
    judgment = (
        "INCONCLUSIVE"
        if data["status"] != "COMPLETED"
        else "HARM_OBSERVED"
        if harmful
        else "SUPPORTED"
        if supported
        else "NOT_DEMONSTRATED"
    )
    write(
        ROOT / "docs/PIC_1_1_0_R3_JUDGMENT.json",
        {
            "judgment": judgment,
            "rule": "Frozen protocol endpoint/uncertainty rule; resource cost remains a separate utility consideration",
            "incremental_superiority_established": judgment == "SUPPORTED",
        },
    )
    lines = [
        "# PIC 1.1.0 R3: evidence-bound closed-loop experiment",
        "",
        f"Execution: **{data['status']}**. Run date: 2026-10-20, Asia/Tokyo. Local only; no external publication.",
        "",
        "## Executive summary",
        "",
        f"Generic A / verifier-ledger B / verifier-PIC C success: {arms['A']['success']}/16, {arms['B']['success']}/16, {arms['C']['success']}/16. Primary C-B risk difference: {100 * (cb['success'].get('difference_B_minus_A') or 0):.2f} pp; conservative 95% interval {interval(cb['success'])}. Utility judgment: **{judgment}**. Running a real integration is not evidence of incremental PIC utility.",
        "",
        "## Research questions",
        "",
        "RQ1 evidence acquisition (B-A); RQ2 incremental PIC (primary C-B); RQ3 model false completion and final admission; RQ4 valid evidence reuse; RQ5 missing, stale, conflicting, altered and context-incompatible boundaries. No R2 data are pooled. This is a finite synthetic intervention on one model/seed.",
        "",
        "## Environment and exact identities",
        "",
        f"Baseline main: `{inspection['head']}`; clean before changes. PIC 1.1.0 non-editable official wheel SHA-256 `{inspection['wheel_sha256']}`. All {inspection['installed_wheel_files_verified']} installed payload files match that wheel; installed-map SHA-256 `{inspection['installed_content_sha256']}`.",
        "",
        "Model `gemma4:e4b`, digest `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`, 7.5B GGUF Q4_K_M. Its local validation parent is an observed package label, not authenticated vendor provenance. Ollama 0.35.0, Python 3.14.7, unchanged isolated environment. CPU Ryzen 7 8840HS, 8 cores/16 threads, RAM 66,363,183,104 bytes. CPU/RAM snapshots and Ollama timing/token metadata are saved; no continuous GPU/energy/FLOP/monetary measurement. No model download, cloud inference or external lookup.",
        "",
        "## PIC integration capability matrix",
        "",
        "| Feature | Installed 1.1.0 observation |",
        "| --- | --- |",
    ]
    lines += [f"| {key} | {value} |" for key, value in integration["capability_matrix"].items()]
    lines += [
        "",
        "The native functions really execute finite numeric, error, event-order and archive-domain predicates. Route resolution does not execute those functions. Production content-reference envelope validation and development packet identity policy are deliberately separate. The orchestrator supplies the route mapping and trust/recipient/task binding. Native/local settlement, resolution scope, packet usability and global runtime status retain their original meanings.",
        "",
        "## Independent verifier implementation",
        "",
        "Four layers separate authoritative finite sources, the standard-library domain verifier/common typed ledger, actual PIC SDK/CLI evidence/runtime operations, and an independent exact-rational/index oracle. Trusted source hashes, issuer, task grants, scope, TTL and recipient are checked against pre-inference pins. A newly rehashed forgery cannot replace that authority. Hash agreement is not cryptographic issuer authentication or external-world truth. Private gold is isolated from the model/PIC normal inputs. Hand outcomes, boundary cases, adversarial and metamorphic tests precede inference.",
        "",
        "## Experimental design and preregistration",
        "",
        "Four pilot and sixteen new confirmatory tasks; four families. Seven confirmatory tasks permit supported definite decisions, including four proved violations; nine require holding. One shared initial and one A/B/C revision, identical digest/seed/context/output caps; balanced Latin arm orders fixed in advance. A sees no authoritative observations. B/C share the same actual receipt; C adds actual native/PIC fields. Prompt lengths and measured compute differ. The full protocol and freeze manifests are linked below.",
        "",
        "Local preregistration precedes inference but is not independently timestamped third-party registration. The base preservation snapshot predates code changes. Native predicate rejection can establish a supported negative determination; it is distinct from missing/untrusted evidence. Source specifications/observations, delivered faults, trusted provenance and private gold are separate artifacts.",
        "",
        "## Pilot findings",
        "",
        f"Execution: {data['panels']['pilot']['execution']['status']}. Pilot success A/B/C: "
        + "/".join(str(data["panels"]["pilot"]["arms"][a]["success"]) for a in "ABC")
        + " out of four each. Pilot is excluded from every primary estimate. The technical gate concerns operation, propagation, isolation and budget, not effect size. No favorable-case selection is permitted.",
        "",
        "## Confirmatory results",
        "",
        "| Endpoint | A | B | C |",
        "| --- | ---: | ---: | ---: |",
    ]
    for label, key, denom in (
        ("Independent success", "success", "planned"),
        (
            "Unsupported model completion (observable)",
            "unsupported_completion",
            "unsupported_observed",
        ),
        ("Unsupported gate admissions", "gate_unsupported_completion", "planned"),
        ("Supported completion yield", "supported_yield_count", "supported_yield_denominator"),
        ("Correct holding", "correct_abstention", "abstention_denominator"),
        ("Format compliance", "format_conformant", "planned"),
        ("Exact task obligations", "obligations_correct", "planned"),
    ):
        lines.append(
            f"| {label} | " + " | ".join(f"{arms[a][key]}/{arms[a][denom]}" for a in "ABC") + " |"
        )
    lines += [
        "",
        "A's gate admits schema-valid declarations without certifying evidence. B/C apply the same real evidence/conclusion gate; C additionally requires protected PIC readiness. Citation-only failures are separate from substantive false completion when actual adequate B/C observations exist. Missing or untyped completion flags are unknown, never safe zeros.",
        "",
        "## Statistical uncertainty",
        "",
        "| Contrast / endpoint | Difference | Conservative 95% interval | Wins / ties / losses | Exact McNemar p |",
        "| --- | ---: | --- | --- | ---: |",
    ]
    for contrast, pairs in comparisons.items():
        for endpoint, result in pairs.items():
            value = result.get("difference_B_minus_A")
            lines.append(
                f"| {contrast} / {endpoint} | {100 * value:.2f} pp | {interval(result)} | {result.get('B_higher')} / {result.get('ties')} / {result.get('B_lower')} | {result.get('exact_mcnemar_two_sided_p')} |"
                if value is not None
                else f"| {contrast} / {endpoint} | unknown | unknown | unknown | unknown |"
            )
    lines += [
        "",
        "Exact paired construction uses Bonferroni 97.5% discordance intervals. Paired and whole-family bootstrap intervals, degeneration flags, unknown-pair planned-denominator bounds and Wilson arm intervals are in machine-readable results. A zero-width bootstrap does not demonstrate equivalence. Four authored families and single-source producer/consumer dependencies limit effective independent information; producer rows are not additional task outcomes. No multiplicity-adjusted joint superiority claim is made.",
        "",
        "## Per-family results",
        "",
        "| Family | A success | B success | C success |",
        "| --- | ---: | ---: | ---: |",
    ]
    for family, values in main["families"].items():
        lines.append(
            f"| {family} | "
            + " | ".join(f"{values[a]['success']}/{values[a]['planned']}" for a in "ABC")
            + " |"
        )
    lines += [
        "",
        "## Evidence provenance and reuse",
        "",
        f"Confirmatory valid cache hits: {sum(e['reuse']['correct_reuse'] for e in reuse)}/{len(reuse)}; independent domain calls skipped: {sum(e['reuse']['domain_calls_saved'] for e in reuse)}; native PIC calls skipped: {sum(e['reuse']['native_calls_saved'] for e in reuse)}. Reused verified packet references: {sum(e['reused_verified_packet_id'] is not None for e in reuse)}. Both B/C reuse the same validated receipt; the PIC packet link is not independently discovered semantic evidence.",
        "",
        "| Consumer | Valid hit | Generic cached / no-cache seconds | PIC cached / no-cache seconds | B/C supported output |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for e in reuse:
        decisions = [
            r for r in data["rows"] if r["task_id"] == e["task_id"] and r["condition"] in "BC"
        ]
        lines.append(
            f"| {e['task_id']} | {e['reuse']['correct_reuse']} | {e['receipt']['elapsed_seconds']:.6f} / {e['reuse']['no_cache']['elapsed_seconds']:.6f} | {e['pic_seconds']:.6f} / {e['reuse']['no_cache_pic_seconds']:.6f} | "
            + ", ".join(f"{r['condition']}={r['supported_completion_yield']}" for r in decisions)
            + " |"
        )
    lines += [
        "",
        "Logical producer/consumer roles run in one process. A prior-date producer validity query is a retrospective finite query, not a past autonomous execution. Consumer policies are identical in B/C. Current PIC expiration may already reject an expired producer packet. No-cache comparators execute real checks without model calls. One timing per case and very cheap predicates cannot establish robust time/energy savings; fewer calls alone is not an efficiency result.",
        "",
        "## False completion and promotion audit",
        "",
        f"Ten deterministic attack cases: {integration['status']}, actual PIC, zero mocks. Raw route accepts {sum(r['raw_route']['accepted'] for r in integration['cases'])}/10; raw packet promotion accepts {sum('verification_resolution_ids' in r['raw_packet'] for r in integration['cases'])}/10. Common B and protected C gates admit {sum(r['B_gate']['admitted_complete'] for r in integration['cases'])}/10 and {sum(r['C_gate']['admitted_complete'] for r in integration['cases'])}/10, including the valid positive and proved negative only. These counts include intentionally invalid evidence probes; raw acceptance is not a protected task success.",
        "",
        f"Confirmatory raw routes accept {sum(e['raw_resolution']['accepted'] for e in ev)}/{len(ev)}; protected C readiness {sum(e['pic_ready'] for e in ev)}/{len(ev)}. Global final C statuses: {dict(Counter((e['final_pic_flags']['operationally_usable'], e['final_pic_flags']['settled']) for e in ev if e['final_pic_flags']))}. Per-source native results, raw/protected discharge, ledgers, packet decisions and lost obligations are retained in the summary. Exact recipient, source authority and task binding are external defenses common to B/C, not PIC-alone findings.",
        "",
        "## Resource accounting",
        "",
        "| Arm | Allocated measured seconds | Model seconds | Shared verifier seconds | PIC seconds | Allocated input / output tokens |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm in "ABC":
        c = cost["arms"][arm]
        lines.append(
            f"| {arm} | {c['allocated_seconds']:.3f} | {c['model_seconds']:.3f} | {c['shared_verifier_seconds']:.6f} | {c['pic_seconds']:.6f} | {c['allocated_tokens']['input']} / {c['allocated_tokens']['output']} |"
        )
    campaign = data["campaign"] or {}
    warm = read(OUT / "warmup/record.json") if (OUT / "warmup/record.json").exists() else {}
    lines += [
        "",
        cost["allocation"],
        "",
        f"C/B allocated time ratio: {cost['C_over_B_seconds']}. Actual campaign calls including warmup: {campaign.get('calls')}; planned task calls: 80. Actual input/output tokens including warmup: {campaign.get('input_tokens_observed')}/{campaign.get('output_tokens_observed')}. Warmup time: {warm.get('elapsed_time')} s. Confirmatory panel wall: {main['execution'].get('elapsed_seconds')} s. Observed task states: {dict(Counter(r['attempt_status'] for r in data['rows']))}. Energy, money, FLOPs and continuous GPU use are null. Allocation sums exclude I/O/orchestration and do not equal observed wall time. Prefix caching/background activity is recorded but uncontrolled.",
        "",
        "## Negative results and missingness",
        "",
        f"Incremental PIC judgment: {judgment}. B-A success difference: {100 * (ba['success'].get('difference_B_minus_A') or 0):.2f} pp, interval {interval(ba['success'])}. Unknown completion counts A/B/C: "
        + "/".join(str(arms[a]["unsupported_unknown"]) for a in "ABC")
        + ". All planned tasks remain in success/yield denominators. No retry, task replacement, effect-driven extension or model substitution is used. Completion of the campaign is distinct from proof of utility; non-significance is distinct from equivalence.",
        "",
        "## Threats to validity",
        "",
        "Small authored finite dataset, seven determinable cases, one model/digest/seed/host, explicit verdict receipts that may produce a ceiling, synthetic trusted authority, no independently validated benchmark or cryptographic issuer roots, logical rather than autonomous roles, retrospective producer validity query, related templates, unequal realized prompt costs, no background-load/cache isolation, one timing per no-cache comparison, and no external-world actions. C combines native verification and management/formatting; their individual effects are not identified. A has no acquired observations, so B-A mainly tests evidence access and controlled integration rather than intrinsic reasoning improvement. Unmeasured costs are not zero.",
        "",
        "## Reproducibility and preservation",
        "",
        f"Preservation: {data['preservation']['status']}, {data['preservation']['protected_files']} prior files byte-identical. Raw inputs/responses and PIC outputs remain private; sanitized public rows reproduce statistics without the model. Source/protocol freezes use normalized LF hashes, raw evidence uses exact canonical byte hashes. Public file identities and validation are separate artifacts. Local commits are not third-party preregistration.",
        "",
        "[Protocol](PROTOCOL_PIC_1_1_0_R3.md), [reproduction](REPRODUCIBILITY_PIC_1_1_0_R3.md), [summary](EXPERIMENT_SUMMARY_PIC_1_1_0_R3.json), [integration](PIC_1_1_0_R3_INTEGRATION.json), [validation](PIC_1_1_0_R3_VALIDATION.json).",
        "",
        "## Implications for PIC and collective intelligence research",
        "",
        "This tests explicit finite verification plus evidence/runtime management in a role-separated workflow. It can show which checks are native and which are orchestrator-supplied, and whether verified evidence survives reuse. It cannot show emergence of collective intelligence, independent agent discovery, multi-agent complementarity, real-world truth acquisition, scalable trust, capability self-improvement or external resource acceleration. A functioning packet format and local promotion are mechanisms, not observations of collective intelligence.",
        "",
        "## Final bounded Go / No-Go assessment",
        "",
        f"Assessment: {judgment}. A positive next-stage utility claim requires a reliable C-B benefit jointly assessed with safety, supported yield and actual cost. This run alone does not authorize scaling or deployment. If no conservative incremental benefit is supported, retain this result and pause the efficacy claim; a separately preregistered next experiment would need an identified mechanism and workloads where verification/reuse cost matters, without weakening B. Unsupported autonomous-agent/production-identity claims remain outside scope.",
        "",
    ]
    (ROOT / "docs/EXPERIMENT_REPORT_PIC_1_1_0_R3.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"R3 report rendered: {judgment}")


if __name__ == "__main__":
    render()
