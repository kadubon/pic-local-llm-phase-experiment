from __future__ import annotations

import importlib.metadata
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from pic_local_llm_phase_experiment import pic110_runner as runner
from pic_local_llm_phase_experiment.pic110_adapter import feedback, parse_report
from pic_local_llm_phase_experiment.pic110_analysis import cp_interval, paired, total
from pic_local_llm_phase_experiment.pic110_oracle import evaluate, parse_answer
from pic_local_llm_phase_experiment.pic110_prompts import GENERIC, revision

ROOT = Path(__file__).resolve().parents[1]
GOLD = json.loads((ROOT / "tasks/pic110/oracles.json").read_text())
PUBLIC = json.loads((ROOT / "tasks/pic110/public.json").read_text())


@pytest.mark.parametrize("task_id", list(GOLD))
def test_oracle_positive(task_id):
    gold = GOLD[task_id]
    answer = {
        "decision": gold["decision"],
        "complete": gold["complete"],
        "evidence": gold["minimal_evidence_sets"][0],
        "unresolved": gold["unresolved"],
    }
    assert evaluate(json.dumps(answer), gold)["success"]
    assert evaluate("```json\n" + json.dumps(answer) + "\n```", gold)["success"]


@pytest.mark.parametrize("task_id", list(GOLD))
def test_oracle_missing_evidence_negative(task_id):
    gold = GOLD[task_id]
    answer = {"decision": gold["decision"], "complete": True, "evidence": [], "unresolved": []}
    result = evaluate(json.dumps(answer), gold)
    assert result["success"] is False
    assert result["false_completion"] is True


@pytest.mark.parametrize(
    "text", ["not JSON", '{"decision":NaN}', '{"complete":true,"complete":false}', "[]"]
)
def test_invalid_json_does_not_become_known_no_false_completion(text):
    result = evaluate(text, GOLD["integrate_01"])
    assert result["success"] is False and result["false_completion"] is None


def test_unknowns_stay_null():
    parsed = parse_report({}, "check")
    for key in (
        "accepted",
        "workflow_usable",
        "operationally_usable",
        "settled",
        "acceleration_metrics_certified",
        "missing_obligation_count",
        "residual_burden",
    ):
        assert parsed[key] is None
    assert total([None, 3]) is None
    assert total([0, 0]) == 0
    assert evaluate(None, GOLD["version_03"])["false_completion"] is None


def test_strict_boolean_status_and_numeric_burden():
    data = parse_report(
        {
            "accepted": "false",
            "workflow_usable": True,
            "settled": False,
            "residual_summary": {"x": True},
            "unresolved_obligations": ["missing"],
        },
        "check",
    )
    assert data["accepted"] is None and data["workflow_usable"] is True
    assert data["settled"] is False and data["residual_burden"] is None
    assert data["missing_obligation_count"] == 1


def test_status_separation_and_actual_schema_fixture():
    # Fields follow the inspected v1.1 CLI shape, not v0.4 legacy defaults.
    data = parse_report(
        {
            "accepted": True,
            "workflow_usable": True,
            "operationally_usable": False,
            "settled": False,
            "unresolved_obligations": ["baseline", "grounding"],
            "residual_summary": {"residual": 2.02},
        },
        "check",
    )
    assert data["accepted"] and data["workflow_usable"]
    assert data["operationally_usable"] is False and data["settled"] is False
    assert data["acceleration_metrics_certified"] is None
    assert data["residual_burden"] == 2.02
    intake = parse_report({"runtime_report": {"missing_obligations": ["x"]}}, "intake")
    assert intake["missing_obligations"] == ["x"]
    assert intake["workflow_usable"] is None


def test_typed_decision_and_fabricated_citation_rejected():
    gold = {
        "decision": 1,
        "complete": True,
        "minimal_evidence_sets": [["S"]],
        "allowed_evidence": ["S"],
        "unresolved": [],
    }
    answer = {"decision": True, "complete": True, "evidence": ["S"], "unresolved": []}
    assert not evaluate(json.dumps(answer), gold)["success"]
    answer.update(decision=1, evidence=["S", "invented"])
    assert evaluate(json.dumps(answer), gold)["false_completion"] is True


def test_unresolved_obligations_cannot_disappear():
    gold = GOLD["conflict_03"]
    answer = {
        "decision": None,
        "complete": False,
        "evidence": gold["minimal_evidence_sets"][0],
        "unresolved": [],
    }
    assert evaluate(json.dumps(answer), gold)["unresolved_preserved"] is False


def test_schedule_balanced_and_gold_not_in_generation_path():
    cfg = runner.settings()
    schedule = runner.schedule(cfg)
    for panel, n in (("pilot", 4), ("confirmatory", 12), ("historical", 10)):
        group = [t for t in schedule if t["panel"] == panel]
        assert len(group) == n
        assert sum(t["order"][0] == "A" for t in group) == n // 2
    assert len({t["task_id"] for t in schedule}) == 26
    for task in PUBLIC:
        assert set(task) == {"task_id", "family", "panel", "prompt", "source_ids"}
        assert "minimal_evidence_sets" not in task["prompt"]
        assert "oracles.json" not in task["prompt"]
    # The runner may hash the gold file for provenance but never read/parse it as input.
    source = Path(runner.__file__).read_text()
    assert 'read(ROOT / "tasks" / "pic110" / "oracles.json")' not in source


def test_feedback_preserves_actual_obligations_without_oracle():
    diagnosis = {
        "check": parse_report({"unresolved_obligations": ["unrelated"]}, "check"),
        "intake": parse_report({"runtime_report": {"missing_obligations": ["x"]}}, "intake"),
    }
    material = json.loads(feedback(diagnosis))
    assert material["check"]["missing_obligations"] == ["unrelated"]
    assert material["intake"]["missing_obligations"] == ["x"]
    a = revision("same task", "same initial", GENERIC)
    b = revision("same task", "same initial", feedback(diagnosis))
    assert a.split("REVIEW MATERIAL")[0] == b.split("REVIEW MATERIAL")[0]


def test_paired_ci_nonzero_with_no_discordance():
    p = paired([True] * 12, [True] * 12, 7, 100)
    assert p["difference_B_minus_A"] == 0
    assert p["ties"] == 12 and p["bootstrap_degenerate"]
    assert p["conservative_exact_95_ci"][0] < 0 < p["conservative_exact_95_ci"][1]
    assert cp_interval(0, 12)[0] == 0
    assert cp_interval(12, 12)[1] == 1
    q = paired([False, True], [True, False], 7, 100)
    assert q["B_higher"] == q["B_lower"] == 1


def test_parse_answer_rejects_trailing_prose():
    with pytest.raises(ValueError):
        parse_answer('{"complete":false} explanatory text')


def test_budget_stops_before_additional_inference(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "OUT", tmp_path)
    campaign = runner.Campaign.__new__(runner.Campaign)
    campaign.cfg = runner.settings()
    campaign.path = tmp_path / "campaign.json"
    campaign.data = {
        "calls": 80,
        "started_epoch": __import__("time").time(),
        "input_tokens_reserved": 0,
        "output_tokens_reserved": 0,
        "consecutive_failures": 0,
        "stopped_reason": None,
    }
    with pytest.raises(runner.BudgetStop, match="call_limit"):
        campaign.guard()
    assert runner.read(campaign.path)["stopped_reason"] == "call_limit"


def test_model_free_matched_harness_calls_and_artifact_identity(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "OUT", tmp_path)
    task = {
        "task_id": "fixture",
        "panel": "pilot",
        "family": "fixture",
        "prompt": "Synthetic task, no gold",
        "order": ["B", "A"],
    }
    monkeypatch.setattr(runner, "verify", lambda _: {"schedule": [task]})
    cfg = runner.settings()
    cfg["pic_distribution_hash"] = runner.sha(b"fixture")
    monkeypatch.setattr(runner, "settings", lambda: cfg)
    monkeypatch.setattr(importlib.metadata, "version", lambda _: "1.1.0")
    monkeypatch.setitem(
        sys.modules,
        "percolation_inversion_compiler",
        SimpleNamespace(__file__=str(Path(sys.prefix) / "fixture.py")),
    )
    setup = tmp_path / "setup"
    setup.mkdir()
    (setup / "percolation_inversion_compiler-1.1.0-py3-none-any.whl").write_bytes(b"fixture")
    calls = []

    class FakeCampaign:
        data = {"calls": 0}

        def __init__(self, cfg):
            pass

        def guard(self):
            pass

        def model_identity(self):
            pass

        def generate(self, prompt, folder, task, condition, initial_hash):
            calls.append((condition, initial_hash, prompt))
            self.data["calls"] += 1
            folder.mkdir()
            (folder / "answer.txt").write_text(
                "fixed initial" if condition == "initial" else "final answer"
            )
            rec = {"attempt_status": "OK"}
            runner.write(folder / "record.json", rec)
            return rec

    monkeypatch.setattr(runner, "Campaign", FakeCampaign)
    fake_diag = {
        "check": parse_report({}, "check"),
        "intake": parse_report({}, "intake"),
        "elapsed_seconds": 0.01,
    }
    monkeypatch.setattr(runner, "diagnose", lambda *a: fake_diag)
    monkeypatch.setattr(
        runner.requests,
        "get",
        lambda *a, **kw: SimpleNamespace(
            raise_for_status=lambda: None, json=lambda: {"models": []}
        ),
    )
    runner.run("pilot")
    assert [c[0] for c in calls] == ["initial", "B", "A"]
    assert calls[1][1] == calls[2][1] == runner.sha("fixed initial")
    assert runner.read(tmp_path / "pilot/panel.json")["status"] == "COMPLETED"
