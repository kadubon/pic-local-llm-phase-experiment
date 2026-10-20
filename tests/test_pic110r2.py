from __future__ import annotations

import copy
import json
from types import SimpleNamespace

import pytest

from pic_local_llm_phase_experiment import pic110r2_runner as runner
from pic_local_llm_phase_experiment.pic110r2_logic import derive, matches, outcome, worlds
from pic_local_llm_phase_experiment.pic110r2_oracle import evaluate
from pic_local_llm_phase_experiment.pic110r2_runner import GENERIC, ROOT, revision, schedule

TASKS = json.loads((ROOT / "tasks/pic110r2/public.json").read_text())
GOLD = json.loads((ROOT / "tasks/pic110r2/oracles.json").read_text())
EXPECTED = {
    "r2_pilot_integration": 65,
    "r2_integrate_01": 65,
    "r2_integrate_02": 61,
    "r2_integrate_03": 137,
    "r2_integrate_04": 43,
    "r2_pilot_policy": "deny",
    "r2_policy_01": "deny",
    "r2_policy_02": "permit",
    "r2_policy_03": None,
    "r2_policy_04": 28,
    "r2_pilot_evidence": None,
    "r2_evidence_01": None,
    "r2_evidence_02": None,
    "r2_evidence_03": None,
    "r2_evidence_04": "fail",
    "r2_pilot_validation": ["beta", "gamma"],
    "r2_validate_01": ["alpha", "beta"],
    "r2_validate_02": ["alpha", "beta", "gamma"],
    "r2_validate_03": "fail",
    "r2_validate_04": None,
}


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t["task_id"])
def test_hand_calculated_outcomes_and_all_minimal_proofs(task):
    gold, audit = derive(task)
    assert gold == GOLD[task["task_id"]]
    assert gold["decision"] == EXPECTED[task["task_id"]]
    assert audit["world_count"] >= 3
    for proof in audit["all_minimal_proofs"]:
        constraints = [s for s in task["sources"] if s["id"] in proof["ids"]]
        possible = [w for w in worlds(task) if all(matches(w, s) for s in constraints)]
        assert possible
        assert all(
            outcome(task, w) == {k: gold[k] for k in ("decision", "complete", "unresolved")}
            for w in possible
        )
        for necessity in proof["necessity"]:
            assert necessity["counterexample_outcome"] != {
                k: gold[k] for k in ("decision", "complete", "unresolved")
            }


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t["task_id"])
def test_semantic_positive_bare_bracketed_and_redundant_known_sources(task):
    gold = GOLD[task["task_id"]]
    answer = {k: gold[k] for k in ("decision", "complete", "unresolved")}
    answer["evidence"] = gold["minimal_evidence_sets"][0]
    assert evaluate(json.dumps(answer), gold)["success"]
    answer["evidence"] = [f"[{s}]" for s in answer["evidence"]]
    assert evaluate(json.dumps(answer), gold)["success"]
    answer["evidence"] = gold["allowed_evidence"]
    assert evaluate(json.dumps(answer), gold)["success"]


def test_inactive_and_redundant_records_not_mandatory():
    assert GOLD["r2_policy_01"]["minimal_evidence_sets"] == [["E02"]]
    assert GOLD["r2_policy_02"]["minimal_evidence_sets"] == [["E01"]]
    assert GOLD["r2_policy_04"]["minimal_evidence_sets"] == [["E01"]]
    assert GOLD["r2_integrate_01"]["minimal_evidence_sets"] == [["E01", "E02", "E03", "E04"]]
    assert GOLD["r2_integrate_03"]["minimal_evidence_sets"] == [
        ["E01", "E02", "E03"],
        ["E02", "E03", "E04"],
    ]


def test_type_equivalence_is_fixed_and_not_a_false_factual_completion():
    gold = GOLD["r2_integrate_04"]
    answer = {k: gold[k] for k in ("decision", "complete", "unresolved")}
    answer.update(decision="43", evidence=["[E01]", " E02 ", "E03"])
    result = evaluate(json.dumps(answer), gold)
    assert result["success"] and result["substantive_false_completion"] is False
    assert result["format_conformant"] is False and result["surface_normalization_used"]
    answer["decision"] = True
    assert evaluate(json.dumps(answer), gold)["substantive_false_completion"] is True


def test_evidence_omission_not_conflated_with_substantive_false_completion():
    gold = GOLD["r2_policy_01"]
    answer = {k: gold[k] for k in ("decision", "complete", "unresolved")}
    answer["evidence"] = []
    result = evaluate(json.dumps(answer), gold)
    assert not result["success"] and result["substantive_false_completion"] is False
    assert result["evidence_incomplete_completion"] is True


@pytest.mark.parametrize(
    "tid", ["r2_policy_03", "r2_evidence_01", "r2_evidence_02", "r2_evidence_03", "r2_validate_04"]
)
def test_missing_evidence_or_conflict_cannot_be_declared_complete(tid):
    gold = GOLD[tid]
    answer = {
        "decision": "permit",
        "complete": True,
        "evidence": gold["allowed_evidence"],
        "unresolved": [],
    }
    result = evaluate(json.dumps(answer), gold)
    assert not result["success"] and result["substantive_false_completion"] is True


@pytest.mark.parametrize(
    "answer",
    [None, "not JSON", '{"complete":true,"complete":false}', '{"decision":NaN}', '{"decision":42}'],
)
def test_unknown_completion_claim_stays_unknown(answer):
    result = evaluate(answer, GOLD["r2_integrate_04"])
    assert result["success"] is False and result["substantive_false_completion"] is None


def test_invented_citations_fail_support():
    gold = GOLD["r2_policy_01"]
    answer = {k: gold[k] for k in ("decision", "complete", "unresolved")}
    answer["evidence"] = ["E02", "E99"]
    assert evaluate(json.dumps(answer), gold)["evidence_sufficient"] is False


def test_fresh_tasks_and_balanced_matched_prompts():
    prior = json.loads((ROOT / "tasks/pic110/public.json").read_text())
    assert not {t["task_id"] for t in TASKS} & {t["task_id"] for t in prior}
    assert not {t["prompt"] for t in TASKS} & {t["prompt"] for t in prior}
    planned = schedule()
    for panel, n in (("pilot", 4), ("confirmatory", 16)):
        group = [t for t in planned if t["panel"] == panel]
        assert len(group) == n
        assert sum(t["order"][0] == "A" for t in group) == n // 2
    assert (
        revision("task", "initial", GENERIC).split("REVIEW MATERIAL")[0]
        == revision("task", "initial", "actual PIC data").split("REVIEW MATERIAL")[0]
    )
    for t in TASKS:
        assert "minimal_evidence_sets" not in t["prompt"]
        assert "oracles.json" not in t["prompt"]


def test_adding_an_irrelevant_record_does_not_change_gold_or_minimal_proofs():
    task = copy.deepcopy(next(t for t in TASKS if t["task_id"] == "r2_policy_01"))
    before, _ = derive(task)
    task["domains"]["noise"] = [1, 2]
    task["sources"].append({"id": "E99", "facts": {"noise": 1}})
    after, _ = derive(task)
    assert after["decision"] == before["decision"]
    assert after["minimal_evidence_sets"] == before["minimal_evidence_sets"]


def test_model_free_r2_harness_uses_three_calls_and_shared_initial(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "OUT", tmp_path)
    task = {
        "task_id": "fixture_r2",
        "panel": "pilot",
        "family": "fixture",
        "prompt": "new task without gold",
        "order": ["B", "A"],
    }
    monkeypatch.setattr(runner, "verify", lambda phase: {"schedule": [task]})
    monkeypatch.setattr(runner, "preservation", lambda: {"status": "PASS"})
    monkeypatch.setattr(runner, "identity", lambda cfg: {})
    cfg = runner.settings()
    cfg["pic_distribution_hash"] = runner.sha(b"fixture")
    monkeypatch.setattr(runner, "settings", lambda: cfg)
    setup = tmp_path / "setup"
    setup.mkdir()
    (setup / "percolation_inversion_compiler-1.1.0-py3-none-any.whl").write_bytes(b"fixture")
    calls = []

    class FakeCampaign:
        def __init__(self, cfg):
            self.data = {"calls": 0}

        def generate(self, prompt, folder, task, condition, initial_hash):
            calls.append((condition, initial_hash, prompt))
            self.data["calls"] += 1
            folder.mkdir()
            (folder / "answer.txt").write_text(
                "shared initial" if condition == "initial" else "final"
            )
            record = {"attempt_status": "OK"}
            runner.write(folder / "record.json", record)
            return record

    monkeypatch.setattr(runner, "Campaign", FakeCampaign)
    monkeypatch.setattr(
        runner,
        "diagnose",
        lambda *args: {
            "check": {"status": "parsed"},
            "intake": {"status": "parsed"},
            "elapsed_seconds": 0.1,
        },
    )
    monkeypatch.setattr(
        runner.requests,
        "get",
        lambda *args, **kw: SimpleNamespace(
            raise_for_status=lambda: None, json=lambda: {"models": []}
        ),
    )
    runner.run("pilot")
    assert [x[0] for x in calls] == ["initial", "B", "A"]
    assert calls[1][1] == calls[2][1] == runner.sha("shared initial")
    assert runner.read(tmp_path / "pilot/panel.json")["status"] == "COMPLETED"
