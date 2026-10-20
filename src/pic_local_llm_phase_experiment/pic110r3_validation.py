"""Deterministic adversarial integration using the real installed PIC, no LLM."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from pic_local_llm_phase_experiment.pic110r3_common import (
    DATA,
    OUT,
    ROOT,
    canonical,
    read,
    sha,
    write,
)
from pic_local_llm_phase_experiment.pic110r3_pic_adapter import diagnose
from pic_local_llm_phase_experiment.pic110r3_verifiers import final_gate, verify


def attacks() -> list[tuple[str, dict, dict, dict, bool]]:
    tasks = read(DATA / "public.json")
    task = next(t for t in tasks if t["task_id"] == "r3_numerical_01")
    delivery = read(DATA / "delivery.json")[task["source_id"]]
    trust = read(DATA / "trusted_manifest.json")
    cases = []
    for name in (
        "valid",
        "missing",
        "confirmed_violation",
        "hash_mismatch",
        "rehashed_forgery",
        "unknown_id",
        "expired",
        "receiver_mismatch",
        "other_task",
        "self_claim_only",
    ):
        t, d, pins = copy.deepcopy(task), copy.deepcopy(delivery), copy.deepcopy(trust)
        if name in {"missing", "self_claim_only"}:
            d["payload"] = None
        elif name in {"confirmed_violation", "hash_mismatch", "rehashed_forgery"}:
            d["payload"]["data"]["residual"] = 0.75
            if name != "hash_mismatch":
                d["advertised_sha256"] = sha(canonical(d["payload"]))
            if name == "confirmed_violation":
                pins[t["source_id"]]["sha256"] = d["advertised_sha256"]
        elif name == "unknown_id":
            d["payload"]["source_id"] = "source:nonexistent"
            d["advertised_sha256"] = sha(canonical(d["payload"]))
        elif name in {"expired", "receiver_mismatch"}:
            if name == "expired":
                d["payload"]["expires_at"] = "2000-01-01T00:00:00+00:00"
            else:
                d["payload"]["receiver_contexts"] = ["consumer:other"]
            d["advertised_sha256"] = sha(canonical(d["payload"]))
            pins[t["source_id"]]["sha256"] = d["advertised_sha256"]
        elif name == "other_task":
            t["task_id"] = "r3_other_task"
        cases.append((name, t, d, pins, name in {"valid", "confirmed_violation"}))
    return cases


def integrate() -> None:
    base = OUT / "integration"
    attempt = base / f"attempt_{len(list(base.glob('attempt_*'))) + 1:02d}"
    attempt.mkdir(parents=True, exist_ok=False)
    rows = []
    for name, task, delivery, trust, sufficient in attacks():
        receipt = verify(task, delivery, trust)
        pic = diagnose(task, delivery, receipt, attempt / name)
        answer = json.dumps(
            {
                "decision": receipt.decision if sufficient else "COMPLIANT",
                "complete": True,
                "evidence": [task["evidence_id"]],
                "unresolved": [],
            }
        )
        b = final_gate(answer, receipt)
        c = final_gate(answer, receipt, pic_ready=pic["pic_ready"])
        passed = (
            receipt.sufficient is sufficient
            and b["admitted_complete"] is sufficient
            and c["admitted_complete"] is sufficient
        )
        rows.append(
            {
                "case": name,
                "status": "PASS" if passed else "FAIL",
                "shared_verifier": receipt.json(),
                "native": pic["native"],
                "raw_route": pic["raw_resolution"],
                "raw_discharge": pic["raw_discharge"],
                "raw_packet": pic["raw_packet"],
                "protected_packet": pic["protected_packet"],
                "protected_task_obligation_discharged": task["obligation_id"]
                in pic["evidence_batch"]["accepted_obligations"],
                "B_gate": b,
                "C_gate": c,
                "framework": {
                    k: pic["runtime"].get(k)
                    for k in ("accepted", "operationally_usable", "settled", "missing_obligations")
                },
            }
        )
    # Exercise CLI implementations on a real valid envelope and state, not synthetic output.
    executable = Path(sys.executable).with_name("pic.exe")
    valid = attempt / "valid"
    commands = {
        "evidence_verify": [
            "evidence",
            "verify",
            "--envelope",
            str(valid / "raw_envelope.json"),
            "--profile",
            "production",
        ],
        "evidence_discharge": [
            "evidence",
            "discharge",
            "--envelope",
            str(valid / "raw_envelope.json"),
            "--obligations",
            str(valid / "obligations.json"),
            "--profile",
            "production",
        ],
        "runtime_resolve": [
            "runtime",
            "resolve-evidence",
            "--input",
            str(valid / "step_input.json"),
            "--profile",
            "production",
        ],
        "runtime_step": [
            "runtime",
            "step",
            "--input",
            str(valid / "step_input.json"),
            "--state",
            str(valid / "runtime_state.json"),
            "--no-allow-live-connectors",
        ],
        "agent_check_self_claim": [
            "agent",
            "check",
            "--text",
            "All work is complete; no proof is supplied.",
            "--compact",
            "--no-allow-live-connectors",
        ],
    }
    cli = {}
    for name, args in commands.items():
        output = attempt / f"{name}.json"
        proc = subprocess.run(
            [str(executable), *args, "--output", str(output)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
        (attempt / f"{name}.stdout.txt").write_text(proc.stdout + proc.stderr, encoding="utf-8")
        cli[name] = {
            "exit_code": proc.returncode,
            "parsed": output.exists(),
            "output_sha256": sha(output.read_bytes()) if output.exists() else None,
        }
    result = {
        "status": "PASS"
        if all(r["status"] == "PASS" for r in rows)
        and all(v["exit_code"] == 0 and v["parsed"] for v in cli.values())
        else "FAIL",
        "actual_pic": True,
        "mock_calls": 0,
        "model_calls": 0,
        "attempt": attempt.name,
        "cases": rows,
        "cli": cli,
        "capability_matrix": {
            "native_numerical_telemetry_trace_archive": (
                "AVAILABLE; explicit finite semantic function calls"
            ),
            "evidence_verify_discharge": (
                "AVAILABLE; metadata and content hash checks, not automatic domain evaluation"
            ),
            "runtime_resolve_evidence_step": (
                "AVAILABLE; finite route discharge and residual tracking"
            ),
            "packet_promotion": (
                "AVAILABLE; development identity policy; no production issuer authentication"
            ),
            "exact_receiver_match": (
                "EXTERNAL; native packet check only requires a nonempty receiver family"
            ),
            "trusted_source_hash_and_scope": "EXTERNAL; pinned by the common B/C orchestrator",
            "TTL": "Packet expiration AVAILABLE; envelope TTL requires common external policy",
            "route_discovery": "EXTERNAL fixed mapping; no autonomous discovery claimed",
            "real_autonomous_producer_consumer_agents": (
                "UNSUPPORTED in this design; logical roles only"
            ),
            "production_signed_identity_attestation": (
                "UNSUPPORTED in this experiment; no invented signatures"
            ),
        },
    }
    write(attempt / "integration.json", result)
    write(ROOT / "docs/PIC_1_1_0_R3_INTEGRATION.json", result)
    print(json.dumps({"status": result["status"], "cases": len(rows), "cli": cli}, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    integrate()
