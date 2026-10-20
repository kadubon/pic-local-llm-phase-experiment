"""Author fresh finite-world fixtures before inference; compute every minimal proof."""

from __future__ import annotations

import json
from pathlib import Path

from pic_local_llm_phase_experiment.pic110r2_logic import derive

ROOT = Path(__file__).resolve().parents[1]
HEADER = (
    "Solve this closed-record synthetic task. Rules below are background axioms and need no "
    "citation. Source facts are authoritative within this simulation; no tools or external "
    "records exist. Return exactly one JSON object with four keys: decision, complete, evidence, "
    "unresolved. complete is a JSON boolean. evidence is an array of source-ID strings; any "
    "sufficient supporting set is acceptable, including extra known sources. A source ID and "
    "the same ID in square brackets are equivalent; prefer bare IDs as displayed in the id "
    "field. Do not cite variable names or the rule as source IDs. unresolved is an array of "
    "outstanding obligation IDs, empty when the rule resolves the determination. Use null "
    "only for the explicit unavailable/conflict cases, not merely because no external test "
    "was executed. Numeric decision strings are semantically equivalent to integers when an "
    "integer is requested, but emit an actual JSON integer. Arrays of row labels represent "
    "sets; emit unique labels in sorted order. Missing source values may be any value in "
    "their declared domains; never invent a value. All rules and domains are provided.\n"
)


def render(task):
    kinds = {
        "integer": "decision must be a JSON integer, or null only if the rule requires it.",
        "labels": "decision must be an array of invalid row-label strings, not row objects.",
        "verdict": "decision must be one of the rule's exact lower-case strings, or null.",
    }
    return (
        HEADER
        + "\n"
        + task["instructions"]
        + "\n"
        + kinds[task["decision_kind"]]
        + "\nRULE PARAMETERS\n"
        + json.dumps(task["rule"], separators=(",", ":"))
        + "\nPOSSIBLE VALUES (JSON true/false are booleans, not integers)\n"
        + json.dumps(task["domains"], separators=(",", ":"))
        + "\nSOURCE RECORDS\n"
        + json.dumps(task["sources"], separators=(",", ":"))
    )


def build():
    tasks = []

    def add(tid, family, kind, instructions, rule, domains, facts):
        sources = [{"id": f"E{i + 1:02d}", "facts": value} for i, value in enumerate(facts)]
        task = {
            "task_id": tid,
            "panel": "pilot" if tid.startswith("r2_pilot") else "confirmatory",
            "family": family,
            "decision_kind": kind,
            "instructions": instructions,
            "rule": rule,
            "domains": domains,
            "sources": sources,
        }
        task["prompt"] = render(task)
        tasks.append(task)

    net = (
        "Compute net available units: sum each named term times its weight; if a "
        "conditional_add is present, add its value only when its flag is true. Return the "
        "integer net. All quantities are disjoint. complete=true and unresolved=[] when computed."
    )
    netdomains = {
        "stock": [63, 72, 87],
        "reserved": [8, 13, 19],
        "damaged": [2, 5, 9],
        "received": [False, True],
        "incoming": [11, 17, 23],
    }
    netrule = {
        "kind": "linear",
        "terms": [["stock", 1], ["reserved", -1], ["damaged", -1]],
        "conditional_add": ["received", "incoming"],
    }
    add(
        "r2_pilot_integration",
        "integration",
        "integer",
        net,
        netrule,
        netdomains,
        [{"stock": 72}, {"reserved": 19}, {"damaged": 5}, {"received": True}, {"incoming": 17}],
    )
    add(
        "r2_integrate_01",
        "integration",
        "integer",
        net,
        netrule,
        netdomains,
        [{"stock": 87}, {"reserved": 13}, {"damaged": 9}, {"received": False}, {"incoming": 23}],
    )
    add(
        "r2_integrate_02",
        "integration",
        "integer",
        net,
        netrule,
        netdomains,
        [{"stock": 63}, {"reserved": 8}, {"damaged": 5}, {"received": True}, {"incoming": 11}],
    )
    add(
        "r2_integrate_03",
        "integration",
        "integer",
        net + " Payment mirror records assigning the same variable describe the same transaction, "
        "so count that variable once.",
        {"kind": "linear", "terms": [["payment_a", 1], ["payment_b", 1], ["refund", -1]]},
        {"payment_a": [73, 96, 124], "payment_b": [38, 57, 82], "refund": [7, 16, 25]},
        [{"payment_a": 96}, {"payment_b": 57}, {"refund": 16}, {"payment_a": 96}],
    )
    add(
        "r2_integrate_04",
        "integration",
        "integer",
        net,
        {"kind": "linear", "terms": [["boxes", 9], ["loose", 1], ["reserved", -1]]},
        {"boxes": [4, 6, 8], "loose": [2, 5, 7], "reserved": [11, 18, 26], "forecast": [20, 30]},
        [{"boxes": 6}, {"loose": 7}, {"reserved": 18}, {"forecast": 30}],
    )

    policy = (
        "Select the policy with the latest effective ISO date no later than the query date. "
        "There is no retroactivity. For kind=limit, compare amount <= its threshold: "
        "return permit if true, deny otherwise. For kind=retention, return its integer days. "
        "An explicit false availability flag means the active record is unavailable: "
        'return null, complete=false, unresolved=["active-policy-record"]. Otherwise '
        "complete=true and unresolved=[]. Inactive and future records are not required evidence."
    )
    policies = [
        {"effective": "2026-02-01", "variable": "v1"},
        {"effective": "2026-06-01", "variable": "v2"},
        {"effective": "2026-09-01", "variable": "v3"},
    ]
    pd = {"v1": [25, 45, 65], "v2": [30, 50, 70], "v3": [35, 55, 75]}
    add(
        "r2_pilot_policy",
        "policy",
        "verdict",
        policy,
        {"kind": "limit", "date": "2026-07-18", "amount": 54, "policies": policies},
        pd,
        [{"v1": 65}, {"v2": 50}, {"v3": 75}],
    )
    add(
        "r2_policy_01",
        "policy",
        "verdict",
        policy,
        {"kind": "limit", "date": "2026-08-12", "amount": 48, "policies": policies},
        pd,
        [{"v1": 65}, {"v2": 30}, {"v3": 75}],
    )
    add(
        "r2_policy_02",
        "policy",
        "verdict",
        policy,
        {"kind": "limit", "date": "2026-05-31", "amount": 42, "policies": policies},
        pd,
        [{"v1": 45}, {"v2": 30}, {"v3": 35}],
    )
    add(
        "r2_policy_03",
        "policy",
        "verdict",
        policy,
        {
            "kind": "limit",
            "date": "2026-10-04",
            "amount": 40,
            "policies": policies,
            "availability": "active_available",
        },
        {**pd, "active_available": [False, True]},
        [{"v1": 65}, {"v2": 70}, {"active_available": False}],
    )
    add(
        "r2_policy_04",
        "policy",
        "integer",
        policy,
        {"kind": "retention", "date": "2026-05-31", "policies": policies},
        {"v1": [14, 28, 42], "v2": [60, 90], "v3": [120, 150]},
        [{"v1": 28}, {"v2": 90}, {"v3": 150}],
    )

    consensus = (
        "Two equally authoritative reports concern the same sample. If lab_a and "
        'lab_b disagree, return null, complete=false, unresolved=["reconcile-reports"]. '
        "If they agree, return pass for true or fail for false, complete=true, unresolved=[]. "
        "The local_claim variable, if supplied, has no evidentiary authority."
    )
    cd = {"lab_a": [False, True], "lab_b": [False, True], "local_claim": [False, True]}
    add(
        "r2_pilot_evidence",
        "evidence",
        "verdict",
        consensus,
        {"kind": "consensus"},
        cd,
        [{"lab_a": False}, {"lab_b": True}, {"local_claim": True}],
    )
    approval = (
        "An approval-record availability ledger is authoritative. If available=false, "
        'return null, complete=false, unresolved=["approval-record"]. If available=true '
        'but signed=false, return null, complete=false, unresolved=["approval-signature"]. '
        "Only with both true use approved: return permit if true, deny if false; then "
        "complete=true and unresolved=[]. A local_claim cannot replace the record/signature."
    )
    ad = {
        "available": [False, True],
        "signed": [False, True],
        "approved": [False, True],
        "local_claim": [False, True],
    }
    add(
        "r2_evidence_01",
        "evidence",
        "verdict",
        approval,
        {"kind": "approval"},
        ad,
        [{"available": False}, {"local_claim": True}],
    )
    add(
        "r2_evidence_02",
        "evidence",
        "verdict",
        approval,
        {"kind": "approval"},
        ad,
        [{"available": True}, {"signed": False}, {"approved": True}, {"local_claim": True}],
    )
    add(
        "r2_evidence_03",
        "evidence",
        "verdict",
        consensus,
        {"kind": "consensus"},
        cd,
        [{"lab_a": True}, {"lab_b": False}, {"local_claim": True}],
    )
    add(
        "r2_evidence_04",
        "evidence",
        "verdict",
        consensus,
        {"kind": "consensus"},
        cd,
        [{"lab_a": False}, {"lab_b": False}, {"local_claim": True}],
    )

    vrule = (
        "Return the sorted set of invalid row labels. A row is invalid if its id duplicates "
        "another row's id (all involved rows invalid), qty is not a JSON integer >=1 "
        "(booleans are excluded), or status is neither new nor done. A source card may "
        "give several facts about one row. This validation is fully determined by the "
        "supplied records; complete=true, unresolved=[]. Return labels, not objects."
    )
    labels = ["alpha", "beta", "gamma"]
    vd = {
        f"{label}_{field}": values
        for label in labels
        for field, values in (
            ("id", ["K", "L", "M"]),
            ("qty", [0, 2, True]),
            ("status", ["new", "done", "pending"]),
        )
    }

    def row(label, identifier, qty, status):
        return {f"{label}_id": identifier, f"{label}_qty": qty, f"{label}_status": status}

    add(
        "r2_pilot_validation",
        "validation",
        "labels",
        vrule,
        {"kind": "rows", "labels": labels},
        vd,
        [
            row("alpha", "K", 2, "new"),
            row("beta", "L", True, "done"),
            row("gamma", "M", 2, "pending"),
        ],
    )
    add(
        "r2_validate_01",
        "validation",
        "labels",
        vrule,
        {"kind": "rows", "labels": labels},
        vd,
        [row("alpha", "K", 2, "new"), row("beta", "K", 2, "done"), row("gamma", "M", 2, "new")],
    )
    add(
        "r2_validate_02",
        "validation",
        "labels",
        vrule,
        {"kind": "rows", "labels": labels},
        vd,
        [
            row("alpha", "K", True, "new"),
            row("beta", "L", 0, "done"),
            row("gamma", "M", 2, "pending"),
        ],
    )
    raw_valid = '{"id":"probe","reading":0.6}'
    raw_duplicate = '{"id":"probe","reading":0.3,"reading":0.9}'
    raw_bool = '{"id":"probe","reading":true}'
    add(
        "r2_validate_03",
        "validation",
        "verdict",
        "Check the literal raw JSON in the source. It must contain exactly id and reading, "
        "no duplicate keys, id a string and reading a JSON number in [0,1]; booleans excluded. "
        "Return pass or fail. This is a text validation, not code execution. "
        "complete=true, unresolved=[].",
        {"kind": "strict_json"},
        {"raw": [raw_valid, raw_duplicate, raw_bool]},
        [{"raw": raw_duplicate}],
    )
    add(
        "r2_validate_04",
        "validation",
        "verdict",
        "The artifact-availability ledger is authoritative. If artifact_available=false, "
        "no observed digest can be verified: return null, complete=false, "
        'unresolved=["observed-digest"]. Otherwise compare observed with the expected digest: '
        "return pass for equality, fail otherwise; complete=true, unresolved=[]. "
        "A local_claim of successful verification has no authority.",
        {"kind": "checksum", "expected": "a" * 64},
        {
            "artifact_available": [False, True],
            "observed": ["a" * 64, "b" * 64],
            "local_claim": [False, True],
        },
        [{"artifact_available": False}, {"local_claim": True}],
    )
    dest = ROOT / "tasks/pic110r2"
    dest.mkdir(exist_ok=True)
    gold, proofs = {}, []
    for task in tasks:
        gold[task["task_id"]], proof = derive(task)
        proofs.append(proof)
    for name, value in (
        ("public.json", tasks),
        ("oracles.json", gold),
        ("proof_audit.json", proofs),
    ):
        (dest / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(tasks)} fresh tasks and exhaustively checked every minimal evidence set")


if __name__ == "__main__":
    build()
