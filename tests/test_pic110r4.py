from __future__ import annotations

import copy
import json

import pytest

from pic_local_llm_phase_experiment.pic110r3_verifiers import verify
from pic_local_llm_phase_experiment.pic110r4_backend import acquire, gate, states
from pic_local_llm_phase_experiment.pic110r4_common import canonical, sha
from pic_local_llm_phase_experiment.pic110r4_oracle import expected, score, source_status
from pic_local_llm_phase_experiment.pic110r4_reuse import fixture, grid
from pic_local_llm_phase_experiment.pic110r4_tasks import dataset

CASES = dataset()
MAIN = [c for c in CASES if c["panel"] == "confirmatory"]
HAND = [
    ["COMPLIANT", "UNKNOWN", "UNKNOWN", "NONCOMPLIANT"],
    ["NONCOMPLIANT", "NONCOMPLIANT", "UNKNOWN", "COMPLIANT"],
    ["COMPLIANT", "UNKNOWN", "UNKNOWN", "NONCOMPLIANT"],
    ["NONCOMPLIANT", "NONCOMPLIANT", "COMPLIANT", "COMPLIANT"],
    ["COMPLIANT", "UNKNOWN", "UNKNOWN", "NONCOMPLIANT"],
    ["NONCOMPLIANT", "NONCOMPLIANT", "UNKNOWN", "COMPLIANT"],
    ["COMPLIANT", "UNKNOWN", "NONCOMPLIANT", "NONCOMPLIANT"],
    ["NONCOMPLIANT", "NONCOMPLIANT", "NONCOMPLIANT", "COMPLIANT"],
]


@pytest.mark.parametrize("index", range(32))
def test_independent_hand_outcomes(index):
    assert expected(MAIN[index])["decision"] == HAND[index // 4][index % 4]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["task_id"])
def test_real_pic_and_independent_oracle_agree(case, tmp_path):
    acquired = acquire(case, tmp_path / "actual_pic", {}, {})
    gold = expected(case)
    assert states(acquired, "generic") == gold["statuses"]
    assert states(acquired, "pic") == gold["statuses"]
    refs = (
        gold["negative_witnesses"][:1]
        if gold["negative_witnesses"]
        else (gold["evidence_ids"] if gold["complete"] else [])
    )
    answer = json.dumps(
        {
            "decision": gold["decision"],
            "complete": gold["complete"],
            "evidence": refs,
            "unresolved": gold["unresolved"],
        }
    )
    for backend in ("generic", "pic"):
        admitted = gate(answer, acquired, backend)["admitted_complete"]
        assert admitted == gold["complete"]
        assert score(answer, gold, admitted=admitted)["supported_success"]
        forged = json.dumps(
            {
                "decision": "COMPLIANT",
                "complete": True,
                "evidence": ["draft:ready"],
                "unresolved": [],
            }
        )
        assert not gate(forged, acquired, backend)["admitted_complete"]


def test_decisive_failure_does_not_require_unavailable_irrelevant_evidence():
    gold = expected(MAIN[5])
    assert "UNKNOWN" in gold["statuses"] and gold["decision"] == "NONCOMPLIANT"
    answer = {
        "decision": "NONCOMPLIANT",
        "complete": True,
        "evidence": gold["negative_witnesses"][:1],
        "unresolved": [],
    }
    assert score(json.dumps(answer), gold, admitted=True)["contract_success"]
    answer["evidence"] = []
    assert not score(json.dumps(answer), gold, admitted=False)["supported_success"]


def test_id_contract_is_separate_from_semantic_and_evidence_success():
    gold = expected(MAIN[1])
    answer = {
        "decision": "UNKNOWN",
        "complete": False,
        "evidence": [],
        "unresolved": ["missing observations"],
    }
    grade = score(json.dumps(answer), gold, admitted=False)
    assert grade["supported_success"] and not grade["contract_success"]
    assert not grade["unsupported_completion"]


def test_citation_normalization_and_minimum_proof():
    gold = expected(MAIN[0])
    refs = [f" [{ref}] " for ref in reversed(gold["evidence_ids"])]
    obj = {"decision": "COMPLIANT", "complete": True, "evidence": refs + refs, "unresolved": []}
    assert score(json.dumps(obj), gold, admitted=True)["supported_success"]
    obj["evidence"] = refs[:2]
    assert not score(json.dumps(obj), gold, admitted=False)["supported_success"]


@pytest.mark.parametrize("flag", ["true", "false", 1, 0, None])
def test_no_coerced_completion_flag(flag):
    gold = expected(MAIN[0])
    obj = {
        "decision": "COMPLIANT",
        "complete": flag,
        "evidence": gold["evidence_ids"],
        "unresolved": [],
    }
    grade = score(json.dumps(obj), gold, admitted=False)
    assert not grade["format_conformant"] and not grade["supported_success"]


def test_cache_rechecks_trust_and_parameter_changes():
    source = fixture(16, "cache_test")
    task = {
        **source["task"],
        "task_id": "cache_test:consumer",
        "receiver": "consumer:lab",
        "evidence_id": "ev:cache_test",
        "obligation_id": "ob:cache_test",
    }
    cache = {}
    first = verify(task, source["delivery"], source["trust"], cache)
    assert first.sufficient and not first.cache_hit
    assert verify(task, source["delivery"], source["trust"], cache).cache_hit
    denied = {**task, "receiver": "consumer:other"}
    assert not verify(denied, source["delivery"], source["trust"], cache).sufficient
    changed = copy.deepcopy(task)
    changed["parameters"]["tolerance"] = 0
    assert not verify(changed, source["delivery"], source["trust"], cache).cache_hit


def test_rehashed_forgery_is_not_new_authority():
    case = copy.deepcopy(MAIN[0])
    task = case["components"][0]
    delivery = case["delivery"][task["source_id"]]
    delivery["payload"]["data"]["residual"] = 0.99
    delivery["advertised_sha256"] = sha(canonical(delivery["payload"]))
    assert source_status(task, delivery, case["trust"]) == "UNKNOWN"


def test_trace_extension_and_telemetry_boundary_metamorphisms():
    case = copy.deepcopy(MAIN[0])
    task = case["components"][2]
    delivery = case["delivery"][task["source_id"]]
    delivery["payload"]["data"]["events"].append("extra")
    digest = sha(canonical(delivery["payload"]))
    delivery["advertised_sha256"] = case["trust"][task["source_id"]]["sha256"] = digest
    assert source_status(task, delivery, case["trust"]) == "FAIL"
    task = case["components"][1]
    delivery = case["delivery"][task["source_id"]]
    delivery["payload"]["data"]["samples"] = [10.25, 20.25]
    digest = sha(canonical(delivery["payload"]))
    delivery["advertised_sha256"] = case["trust"][task["source_id"]]["sha256"] = digest
    assert source_status(task, delivery, case["trust"]) == "PASS"


def test_worker_grid_is_bounded_and_balanced():
    jobs = grid()
    assert len(jobs) == 24 and len(jobs) * 3 == 72
    assert sum(j["backend"] == "pic" for j in jobs) == 12
    assert all(sorted(j["consumer_order"]) == ["cached", "no_cache"] for j in jobs)


@pytest.mark.parametrize("mutation", ["extra_field", "trace_string", "boolean_number"])
def test_independent_oracle_rejects_malformed_but_rehashed_sources(mutation):
    case = copy.deepcopy(MAIN[0])
    task = case["components"][2 if mutation == "trace_string" else 0]
    delivered = case["delivery"][task["source_id"]]
    if mutation == "extra_field":
        delivered["payload"]["unexpected"] = True
    elif mutation == "trace_string":
        delivered["payload"]["data"]["events"] = "start-check-end"
    else:
        delivered["payload"]["data"]["residual"] = False
    digest = sha(canonical(delivered["payload"]))
    delivered["advertised_sha256"] = case["trust"][task["source_id"]]["sha256"] = digest
    assert source_status(task, delivered, case["trust"]) == "UNKNOWN"
    assert not verify(task, delivered, case["trust"]).sufficient
