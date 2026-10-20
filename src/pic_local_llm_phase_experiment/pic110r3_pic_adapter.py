"""Real installed PIC calls; distinguish native semantics, raw routes and outer gates."""

from __future__ import annotations

import inspect
import time
from pathlib import Path
from typing import Any

from percolation_inversion_compiler.adapters import domain
from percolation_inversion_compiler.core.adapter_routes import (
    EvidenceArtifact,
    VerifierEvidenceEnvelope,
    list_adapter_route_specs,
    resolve_adapter_route,
)
from percolation_inversion_compiler.core.judgment import check_external_verifier_hook
from percolation_inversion_compiler.core.records import ExternalProofObligation
from percolation_inversion_compiler.ecology.records import CapabilityPacketCandidate
from percolation_inversion_compiler.ecpt.records import (
    ASIProxyTargetContract,
    CapabilityHypergraph,
    CapabilityStateVector,
    PhaseControlObjective,
    PhaseControlState,
)
from percolation_inversion_compiler.runtime.algorithms import (
    build_runtime_step,
    promote_packet_candidate,
    resolve_step_evidence,
)
from percolation_inversion_compiler.runtime.records import (
    AgentRuntimeConfig,
    RuntimeState,
    RuntimeStepInput,
)

from pic_local_llm_phase_experiment.pic110r3_common import DATA, canonical, read, sha, write
from pic_local_llm_phase_experiment.pic110r3_verifiers import EvidenceReceipt

ROUTES = {
    "numerical": "verify_ecpt_numerical_envelope",
    "telemetry": "verify_trc_telemetry_calibration",
    "trace": "replay_trc_physical_trace",
    "reuse": "verify_archive_domain_evidence",
}


def state(identifier: str) -> RuntimeState:
    return RuntimeState(
        state_id=identifier,
        phase_state=PhaseControlState(
            state_id=identifier,
            graph=CapabilityHypergraph(),
            state_vector=CapabilityStateVector(),
        ),
        phase_objective=PhaseControlObjective(
            objective_id=identifier, target=ASIProxyTargetContract(target_id=identifier)
        ),
    )


def native(task: dict, payload: dict | None) -> list[dict]:
    if payload is None:
        return []
    p, data, family = task["parameters"], payload["data"], task["family"]
    jobs: list[tuple[Any, dict[str, Any]]] = []
    if family in ("numerical", "reuse"):
        jobs.append(
            (
                domain.verify_ecpt_numerical_envelope,
                {
                    "residual": data["residual"],
                    "residual_bound": p["residual_bound"],
                    "finite_horizon": p["finite_horizon"],
                },
            )
        )
    elif family == "telemetry":
        jobs.append(
            (
                domain.verify_trc_telemetry_calibration,
                {
                    "samples": data["samples"],
                    "references": p["references"],
                    "tolerance": p["tolerance"],
                },
            )
        )
    else:
        jobs.append(
            (
                domain.replay_trc_physical_trace,
                {
                    "events": data["events"],
                    "expected_events": p["expected_events"],
                    "allow_prefix": False,
                },
            )
        )
    if family == "reuse":
        jobs.append(
            (
                domain.verify_archive_domain_evidence,
                {
                    "record_domains": {payload["source_id"]: payload["domain"]},
                    "allowed_domains": set(p["allowed_domains"]),
                },
            )
        )
    results = []
    for fn, arguments in jobs:
        started = time.perf_counter()
        result = fn(**arguments)
        results.append(
            {
                "function": f"{fn.__module__}.{fn.__name__}",
                "implementation_sha256": sha(inspect.getsource(fn).encode()),
                "arguments": {
                    k: sorted(v) if isinstance(v, set) else v for k, v in arguments.items()
                },
                "result": result.model_dump(mode="json"),
                "elapsed_seconds": time.perf_counter() - started,
            }
        )
    return results


def diagnose(
    task: dict,
    delivered: dict,
    receipt: EvidenceReceipt,
    folder: Path,
    *,
    cached_native: list[dict] | None = None,
    agent_output: str | None = None,
    producer_packet: dict | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    folder.mkdir(parents=True, exist_ok=False)
    payload = delivered.get("payload")
    native_results = (
        cached_native if receipt.cache_hit and cached_native is not None else native(task, payload)
    )
    native_calls = 0 if receipt.cache_hit and cached_native is not None else len(native_results)
    fn = ROUTES[task["family"]]
    spec = next(s for s in list_adapter_route_specs() if s.route_id == f"adapters.domain.{fn}")
    source = folder / "source.json"
    if payload is not None:
        source.write_bytes(canonical(payload))
    artifact = (
        []
        if payload is None
        else [
            EvidenceArtifact(
                artifact_id=task["evidence_id"],
                evidence_kind=spec.required_evidence_kind[0],
                sha256=delivered["advertised_sha256"],
                media_type="application/json",
                schema_uri="urn:pic110r3:finite-source:1",
                schema_sha256=sha(canonical(read(DATA / "source_schema.json"))),
                producer_id=payload["issuer"],
                produced_at=payload["produced_at"],
                verifier_id="pic110r3-independent-verifier",
                verifier_version="1",
                content_ref=str(source.resolve()),
            )
        ]
    )
    raw_envelope = VerifierEvidenceEnvelope(
        envelope_id=f"envelope:{task['task_id']}",
        route_id=spec.route_id,
        obligation_ids=[task["obligation_id"]],
        evidence_kind=spec.required_evidence_kind,
        evidence_artifacts=artifact,
    )
    write(folder / "raw_envelope.json", raw_envelope.model_dump(mode="json"))
    raw_resolution = resolve_adapter_route(spec, raw_envelope, profile="production")
    obligation = ExternalProofObligation(
        obligation_id=task["obligation_id"],
        description="Determine finite compliance using authentic evidence",
        obligation_category=spec.obligation_category,
        verifier_hint=spec.verifier_route,
        accepted_evidence_kind=spec.required_evidence_kind,
    )
    raw_hook = raw_resolution.to_external_verifier_hook()
    raw_discharge = check_external_verifier_hook(raw_hook, [obligation])
    agrees = (
        bool(native_results)
        and ("COMPLIANT" if native_results[0]["result"]["accepted"] else "NONCOMPLIANT")
        == receipt.decision
    )
    if receipt.sufficient and not agrees:
        raise ValueError("Native finite predicate disagrees with shared independent verifier")
    ready = receipt.trusted and receipt.sufficient and agrees
    protected_envelope = raw_envelope.model_copy(
        update={
            "envelope_id": f"gated:{task['task_id']}",
            "evidence_artifacts": artifact if ready else [],
        }
    )
    step_input = RuntimeStepInput(
        input_id=task["task_id"],
        evidence_envelopes=[protected_envelope],
        allow_live_connectors=False,
        agent_output=agent_output,
    )
    batch = resolve_step_evidence(step_input, profile="production")
    protected_resolution = batch.resolutions[0]
    protected_discharge = check_external_verifier_hook(
        protected_resolution.to_external_verifier_hook(), [obligation]
    )
    content_hash = delivered["advertised_sha256"]
    candidate = CapabilityPacketCandidate(
        packet_id=f"candidate:{task['task_id']}",
        source_ref=task["source_id"],
        content_sha256=content_hash,
        claim="finite determination, not global settlement",
        receiver_family=payload.get("receiver_contexts", []) if payload else [task["receiver"]],
        evidence_refs=[f"sha256:{content_hash}"],
        verifier_routes=[spec.route_id],
        expires_at=payload.get("expires_at") if payload else None,
        expected_downstream_gain=1.0,
        dependencies=[producer_packet["packet_id"]]
        if receipt.cache_hit
        and producer_packet
        and "verification_resolution_ids" in producer_packet
        else [],
    )
    raw_packet = promote_packet_candidate(candidate, [raw_resolution], [])
    protected_candidate = candidate.model_copy(
        update={
            "evidence_hash_valid": receipt.trusted,
            "route_safe": ready,
            "receiver_family": [task["receiver"]] if ready else [],
        }
    )
    packet = promote_packet_candidate(protected_candidate, [protected_resolution], [])
    step_input = step_input.model_copy(update={"packets": [protected_candidate]})
    # Packet policy is the explicit finite development policy, not production identity attestation.
    runtime = build_runtime_step(
        state(task["task_id"]),
        step_input,
        AgentRuntimeConfig(profile="development", allow_live_connectors=False),
    )
    output = {
        "native": native_results,
        "native_calls": native_calls,
        "native_reused": receipt.cache_hit and cached_native is not None,
        "reused_verified_packet_id": candidate.dependencies[0] if candidate.dependencies else None,
        "raw_resolution": raw_resolution.model_dump(mode="json"),
        "raw_hook": raw_hook.model_dump(mode="json"),
        "raw_discharge": raw_discharge.model_dump(mode="json"),
        "obligation": obligation.model_dump(mode="json"),
        "evidence_batch": batch.model_dump(mode="json"),
        "protected_discharge": protected_discharge.model_dump(mode="json"),
        "raw_packet": raw_packet.model_dump(mode="json"),
        "protected_packet": packet.model_dump(mode="json"),
        "runtime": runtime.model_dump(mode="json"),
        "external_evidence_ready": ready,
        "pic_ready": ready and batch.accepted and hasattr(packet, "verification_resolution_ids"),
        "elapsed_seconds": time.perf_counter() - started,
        "orchestrator_selected_route": spec.route_id,
        "packet_identity_profile": "development",
    }
    write(folder / "actual_pic.json", output)
    write(folder / "step_input.json", step_input.model_dump(mode="json"))
    write(folder / "runtime_state.json", state(task["task_id"]).model_dump(mode="json"))
    write(folder / "obligations.json", {"obligations": [obligation.model_dump(mode="json")]})
    return output


def feedback(result: dict) -> dict:
    """Compact actual fields; common receipt remains exactly the same as B's."""
    return {
        "route_resolution": result["evidence_batch"]["resolutions"][0],
        "native_domain_checks": [
            {"function": r["function"], "result": r["result"]} for r in result["native"]
        ],
        "runtime": {
            k: result["runtime"].get(k)
            for k in (
                "accepted",
                "operationally_usable",
                "settled",
                "missing_obligations",
                "residual_ledger",
            )
        },
        "packet": result["protected_packet"],
    }
