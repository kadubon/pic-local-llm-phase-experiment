"""Post hoc measurement audit; never changes the frozen primary labels or gold.

Retain strict results and expose how surface notation affects interpretation.
The normalization sensitivity is exploratory, not a replacement confirmatory test.
"""

from __future__ import annotations

import copy
import json

from pic_local_llm_phase_experiment.pic110_oracle import evaluate, parse_answer
from pic_local_llm_phase_experiment.pic110_runner import OUT, ROOT, read, write


def main() -> None:
    golds = read(ROOT / "tasks/pic110/oracles.json")
    manifest = read(OUT / "prereg_main.json")
    rows = []
    for task in (t for t in manifest["schedule"] if t["panel"] == "confirmatory"):
        gold = golds[task["task_id"]]
        for condition in ("initial", "A", "B"):
            text = (OUT / "confirmatory" / task["task_id"] / condition / "answer.txt").read_text(
                encoding="utf-8"
            )
            strict = evaluate(text, gold)
            answer = parse_answer(text)
            decision = answer.get("decision")
            exact_decision = (
                type(decision) is type(gold["decision"]) and decision == gold["decision"]
            )
            normalized = copy.deepcopy(answer)
            for i, ref in enumerate(normalized.get("evidence", [])):
                if (
                    isinstance(ref, str)
                    and ref.startswith("[")
                    and ref.endswith("]")
                    and ref[1:-1] in gold["allowed_evidence"]
                ):
                    normalized["evidence"][i] = ref[1:-1]
            numeric_string = (
                type(gold["decision"]) is int
                and isinstance(decision, str)
                and decision.lstrip("-").isdigit()
            )
            if numeric_string:
                normalized["decision"] = int(decision)
            semantic_decision = (
                type(normalized["decision"]) is type(gold["decision"])
                and normalized["decision"] == gold["decision"]
            )
            sensitivity = evaluate(json.dumps(normalized), gold)
            missing = [
                s
                for s in gold["minimal_evidence_sets"][0]
                if s not in normalized.get("evidence", [])
            ]
            rows.append(
                {
                    "task_id": task["task_id"],
                    "condition": condition,
                    "strict_result": strict,
                    "exact_typed_decision_correct": exact_decision,
                    "decision_correct_allowing_numeric_string": semantic_decision,
                    "wrapped_known_source_ids_present": normalized["evidence"]
                    != answer["evidence"],
                    "numeric_string_present": bool(numeric_string),
                    "still_missing_required_source_ids_after_normalization": missing,
                    "surface_normalization_sensitivity": sensitivity,
                    "complete_true": answer.get("complete") is True,
                    "intrinsic_insufficient_evidence_task": gold["decision"] is None,
                    "task_obligation_set_correct": strict["unresolved_preserved"],
                }
            )
    arms = {}
    for arm in ("initial", "A", "B"):
        group = [r for r in rows if r["condition"] == arm]
        arms[arm] = {
            "n": len(group),
            "strict_success": sum(r["strict_result"]["success"] for r in group),
            "strict_false_completion": sum(
                r["strict_result"]["false_completion"] is True for r in group
            ),
            "exact_typed_decision_correct": sum(r["exact_typed_decision_correct"] for r in group),
            "decision_correct_allowing_numeric_string": sum(
                r["decision_correct_allowing_numeric_string"] for r in group
            ),
            "wrapped_known_ids_answers": sum(r["wrapped_known_source_ids_present"] for r in group),
            "strict_false_completion_with_semantically_wrong_decision": sum(
                r["strict_result"]["false_completion"] is True
                and not r["decision_correct_allowing_numeric_string"]
                for r in group
            ),
            "strict_false_completion_with_semantically_correct_decision": sum(
                r["strict_result"]["false_completion"] is True
                and r["decision_correct_allowing_numeric_string"]
                for r in group
            ),
            "complete_true_on_intrinsically_missing_evidence_task": sum(
                r["complete_true"] and r["intrinsic_insufficient_evidence_task"] for r in group
            ),
            "required_task_obligation_disappearances": sum(
                not r["task_obligation_set_correct"] and r["intrinsic_insufficient_evidence_task"]
                for r in group
            ),
            "exploratory_normalized_success": sum(
                r["surface_normalization_sensitivity"]["success"] for r in group
            ),
            "exploratory_normalized_false_completion": sum(
                r["surface_normalization_sensitivity"]["false_completion"] is True for r in group
            ),
        }
    result = {
        "analysis_status": "POST_HOC_MEASUREMENT_AUDIT_NOT_PRIMARY",
        "primary_labels_unchanged": True,
        "gold_unchanged": True,
        "normalization": [
            "unwrap square brackets around an already-known source ID",
            "convert integer-valued decimal strings to JSON integers only when "
            "the fixed gold decision is an integer",
        ],
        "limitations": [
            "The model saw bracketed source labels; requiring bare IDs can penalize notation.",
            "Some predeclared evidence sets contain policy/redundancy context beyond the "
            "logically smallest proof. They remain fixed in the primary analysis.",
            "A strict unsupported-completion label therefore need not mean a false "
            "factual decision.",
            "Normalization was designed after viewing outputs. Its arm differences are descriptive "
            "and cannot support confirmatory efficacy claims.",
        ],
        "arms": arms,
        "rows": rows,
        "efficacy_decision": "INCONCLUSIVE_SMALL_SAMPLE_AND_MEASUREMENT_VALIDITY_LIMITS",
    }
    write(ROOT / "docs/PIC_1_1_0_ORACLE_AUDIT.json", result)
    print(json.dumps(arms, indent=2))


if __name__ == "__main__":
    main()
