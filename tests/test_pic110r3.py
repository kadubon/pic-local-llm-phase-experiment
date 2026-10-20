"""Independent expected cases, boundary/counterexamples, metamorphisms and actual PIC."""

from __future__ import annotations

import copy
import inspect
import json
from collections import Counter

import pytest

from pic_local_llm_phase_experiment import pic110r3_runner as runner
from pic_local_llm_phase_experiment.pic110r3_common import canonical, sha
from pic_local_llm_phase_experiment.pic110r3_oracle import evaluate, gold
from pic_local_llm_phase_experiment.pic110r3_pic_adapter import diagnose, native
from pic_local_llm_phase_experiment.pic110r3_tasks import dataset
from pic_local_llm_phase_experiment.pic110r3_validation import attacks
from pic_local_llm_phase_experiment.pic110r3_verifiers import final_gate, verify


@pytest.mark.parametrize("family", ["numerical", "telemetry", "trace", "reuse"])
@pytest.mark.parametrize("index", [1, 2, 3, 4])
def test_hand_checked_twenty_sources(family, index):
    tasks, _originals, delivery, trust = dataset()
    task = next(t for t in tasks if t["task_id"] == f"r3_{family}_{index:02d}")
    expected = (
        "NONCOMPLIANT"
        if family == "reuse" and index == 1
        else "UNKNOWN"
        if index >= 3 or family == "reuse"
        else "COMPLIANT"
        if index == 1
        else "NONCOMPLIANT"
    )
    reference = gold(task, delivery[task["source_id"]], trust)
    observed = verify(task, delivery[task["source_id"]], trust)
    assert reference["decision"] == expected
    assert observed.decision == expected
    assert observed.sufficient is reference["complete"]


@pytest.mark.parametrize("name,task,delivered,trust,sufficient", attacks())
def test_actual_pic_attacks(name, task, delivered, trust, sufficient, tmp_path):
    receipt = verify(task, delivered, trust)
    actual = diagnose(task, delivered, receipt, tmp_path / name)
    assert actual["pic_ready"] is sufficient
    assert actual["external_evidence_ready"] is sufficient
    assert bool(actual["evidence_batch"]["accepted_obligations"]) is sufficient
    if name in {"rehashed_forgery", "receiver_mismatch", "other_task", "confirmed_violation"}:
        # This is the measured metadata/semantics boundary, not a mocked outcome.
        assert actual["raw_resolution"]["accepted"] is True
        assert "verification_resolution_ids" in actual["raw_packet"]
    if name == "hash_mismatch":
        assert actual["raw_resolution"]["accepted"] is False
    if name == "expired":
        assert actual["raw_resolution"]["accepted"] is True
        assert "verification_resolution_ids" not in actual["raw_packet"]


@pytest.mark.parametrize("delta,expected", [(0, "COMPLIANT"), (0.125, "NONCOMPLIANT")])
def test_boundary_and_independent_rational_oracle(delta, expected):
    tasks, _, delivery, trust = dataset()
    task = tasks[0]
    d = delivery[task["source_id"]]
    d["payload"]["data"]["residual"] = 0.5 + delta
    d["advertised_sha256"] = trust[task["source_id"]]["sha256"] = sha(canonical(d["payload"]))
    assert gold(task, d, trust)["decision"] == verify(task, d, trust).decision == expected
    assert native(task, d["payload"])[0]["result"]["accepted"] is (expected == "COMPLIANT")


@pytest.mark.parametrize("invalid", [True, -0.1, float("nan"), float("inf")])
def test_nonfinite_and_negative_inputs_fail_closed(invalid):
    tasks, _, delivery, trust = dataset()
    task = tasks[0]
    d = delivery[task["source_id"]]
    d["payload"]["data"]["residual"] = invalid
    if invalid is True or invalid == -0.1:
        d["advertised_sha256"] = trust[task["source_id"]]["sha256"] = sha(canonical(d["payload"]))
    assert verify(task, d, trust).sufficient is False
    assert gold(task, d, trust)["complete"] is False


def test_cache_revalidates_context_and_preserves_semantics():
    tasks, _, delivery, trust = dataset()
    task = next(t for t in tasks if t["task_id"] == "r3_reuse_01")
    d = delivery[task["source_id"]]
    cache = {}
    producer = verify(
        {**task, "task_id": task["producer_role"], "receiver": "producer:lab"}, d, trust, cache
    )
    consumer = verify(task, d, trust, cache)
    assert producer.domain_calls == 1
    assert consumer.cache_hit and consumer.domain_calls == 0
    assert consumer.decision == "NONCOMPLIANT"
    bad_receiver = verify({**task, "receiver": "consumer:other"}, d, trust, cache)
    other_task = verify({**task, "task_id": "unapproved-task"}, d, trust, cache)
    assert not bad_receiver.sufficient and not bad_receiver.cache_hit
    assert not other_task.sufficient and not other_task.cache_hit


def test_telemetry_permutation_and_trace_counterexample():
    tasks, _, delivery, trust = dataset()
    task = next(t for t in tasks if t["task_id"] == "r3_telemetry_01")
    d = delivery[task["source_id"]]
    before = gold(task, d, trust)["decision"]
    task["parameters"]["references"].reverse()
    d["payload"]["data"]["samples"].reverse()
    d["advertised_sha256"] = trust[task["source_id"]]["sha256"] = sha(canonical(d["payload"]))
    assert gold(task, d, trust)["decision"] == verify(task, d, trust).decision == before
    trace = next(t for t in tasks if t["task_id"] == "r3_trace_01")
    d = delivery[trace["source_id"]]
    d["payload"]["data"]["events"].reverse()
    d["advertised_sha256"] = trust[trace["source_id"]]["sha256"] = sha(canonical(d["payload"]))
    assert gold(trace, d, trust)["decision"] == verify(trace, d, trust).decision == "NONCOMPLIANT"


def test_unrelated_authority_and_citation_semantics():
    tasks, _, delivery, trust = dataset()
    task = tasks[0]
    receipt = verify(task, delivery[task["source_id"]], trust)
    expected = gold(task, delivery[task["source_id"]], trust)
    trust["irrelevant"] = {"sha256": "0" * 64}
    assert gold(task, delivery[task["source_id"]], trust) == expected
    for citation in [task["evidence_id"], " [" + task["evidence_id"] + "] "]:
        text = json.dumps(
            {"decision": "COMPLIANT", "complete": True, "evidence": [citation], "unresolved": []}
        )
        assert evaluate(text, expected, evidence_access=True)["success"]
        assert final_gate(text, receipt)["admitted_complete"]
        assert evaluate(text, expected, evidence_access=False)["unsupported_completion"]
    text = json.dumps({"decision": "COMPLIANT", "complete": True, "evidence": [], "unresolved": []})
    score = evaluate(text, expected, evidence_access=True)
    assert score["citation_only_failure"] and score["unsupported_completion"] is False
    assert not final_gate(text, receipt)["admitted_complete"]


@pytest.mark.parametrize(
    "field,value", [("complete", "true"), ("decision", []), ("evidence", [0]), ("unresolved", [{}])]
)
def test_invalid_output_never_promotes(field, value):
    tasks, _, delivery, trust = dataset()
    t = tasks[0]
    receipt = verify(t, delivery[t["source_id"]], trust)
    expected = gold(t, delivery[t["source_id"]], trust)
    answer = {
        "decision": "COMPLIANT",
        "complete": True,
        "evidence": [t["evidence_id"]],
        "unresolved": [],
    }
    answer[field] = value
    text = json.dumps(answer)
    assert not evaluate(text, expected, evidence_access=True)["success"]
    assert not final_gate(text, receipt)["admitted_complete"]


def test_model_material_separation_and_balanced_schedule():
    source = inspect.getsource(runner)
    assert "pic110r3_oracle" not in source
    assert 'read(OUT / "setup/gold.json")' not in source
    assert "oracles.json" not in runner.GENERIC
    tasks = runner.schedule()
    assert len(tasks) == 20
    for panel in ("pilot", "confirmatory"):
        chosen = [t for t in tasks if t["panel"] == panel]
        for position in range(3):
            counts = Counter(t["order"][position] for t in chosen)
            assert max(counts.values()) - min(counts.values()) <= 1
    cfg = runner.settings()
    assert cfg["max_calls_including_warmup"] == 81
    assert cfg["num_predict"] == 768 and cfg["retries"] == 0
    original = {"receipt": {"decision": "UNKNOWN"}}
    enhanced = {**copy.deepcopy(original), "PIC": {"accepted": False}}
    assert {k: v for k, v in enhanced.items() if k != "PIC"} == original


@pytest.mark.parametrize("notation", ["[{}", "{}]", "[[{}]]", "unknown:{}"])
def test_malformed_citation_cannot_pass_gate(notation):
    tasks, _, delivery, trust = dataset()
    t = tasks[0]
    receipt = verify(t, delivery[t["source_id"]], trust)
    expected = gold(t, delivery[t["source_id"]], trust)
    text = json.dumps(
        {
            "decision": "COMPLIANT",
            "complete": True,
            "evidence": [notation.format(t["evidence_id"])],
            "unresolved": [],
        }
    )
    assert not final_gate(text, receipt)["admitted_complete"]
    assert not evaluate(text, expected, evidence_access=True)["success"]


def test_saved_fixtures_match_generator_and_pilot_hand_outcomes():
    from pic_local_llm_phase_experiment.pic110r3_common import DATA, read

    tasks, originals, delivery, trust = dataset()
    for name, value in (
        ("public.json", tasks),
        ("authoritative.json", originals),
        ("delivery.json", delivery),
        ("trusted_manifest.json", trust),
    ):
        assert read(DATA / name) == value
    expected = {
        "numerical": "COMPLIANT",
        "telemetry": "NONCOMPLIANT",
        "trace": "UNKNOWN",
        "reuse": "COMPLIANT",
    }
    for t in [t for t in tasks if t["panel"] == "pilot"]:
        assert gold(t, delivery[t["source_id"]], trust)["decision"] == expected[t["family"]]


def test_paired_statistics_observable_and_missing_cases():
    from pic_local_llm_phase_experiment.pic110r3_analysis import comparison

    rows = []
    for i, (b, c) in enumerate([(True, True), (False, True), (False, True), (True, False)]):
        for arm, value in (("B", b), ("C", c)):
            rows.append(
                {
                    "task_id": str(i),
                    "family": str(i),
                    "condition": arm,
                    "determinable": True,
                    "oracle": {"success": value},
                }
            )
    result = comparison(rows, "B", "C", "success")
    assert result["B_higher"] == 2 and result["B_lower"] == 1 and result["ties"] == 1
    assert result["difference_B_minus_A"] == 0.25
    assert result["conservative_exact_95_ci"][0] < 0 < result["conservative_exact_95_ci"][1]
    rows[-1]["oracle"]["success"] = None
    incomplete = comparison(rows, "B", "C", "success")
    assert incomplete["unknown_pairs"] == 1 and incomplete["n"] == 3
