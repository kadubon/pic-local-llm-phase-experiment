"""Disclose a frozen secondary denominator mismatch; primary scores never change."""

from __future__ import annotations

import argparse

from pic_local_llm_phase_experiment.pic110r4_common import ROOT, read, sha, write

SUMMARY = ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R4.json"
OUTPUT = ROOT / "docs/PIC_1_1_0_R4_ANALYSIS_AUDIT.json"


def details() -> dict:
    summary = read(SUMMARY)
    assert all(p["status"] != "RUNNING" for p in summary["panels"].values())
    selected = [r for r in summary["rows"] if r["panel"] == "confirmatory"]
    eligible = [r for r in selected if r["determinable"]]
    arms = {}
    for arm in ("G_minimal", "P_minimal"):
        rows = [r for r in eligible if r["arm"] == arm]
        count = sum(r["grade"]["supported_yield"] for r in rows)
        arms[arm] = {"count": count, "eligible": len(rows), "rate": count / len(rows)}
    original = summary["confirmatory"]["comparisons"]["backend_yield_secondary"]
    return {
        "scope": "Protocol-consistent secondary eligible yield; no primary or grade changes",
        "disclosure": (
            "Frozen secondary helper includes all 32 planned cases, including holding cases. "
            "The protocol and arm table define supported yield over 23 determinable cases. "
            "Retain the original field as per-planned-case contribution and report eligible "
            "rates separately. Its 32-pair uncertainty is not a 23-eligible-pair interval."
        ),
        "primary_and_contract_scores_unchanged": True,
        "model_calls_added": 0,
        "frozen_helper_planned_pairs": original["planned_pairs"],
        "frozen_helper_difference": original["difference"],
        "eligible_rates": arms,
        "eligible_difference_P_minus_G": arms["P_minimal"]["rate"] - arms["G_minimal"]["rate"],
        "inference_scope": (
            "Descriptive secondary correction only; backend replay is not a population "
            "equivalence test. No replacement primary test or superiority claim."
        ),
        "component_field_definition": "decision_correct requires both decision and complete flag",
        "summary_sha256_normalized_lf": sha(SUMMARY.read_bytes().replace(b"\r\n", b"\n")),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-public", action="store_true")
    args = parser.parse_args()
    result = details()
    if args.check_public:
        assert result == read(OUTPUT)
        print("R4 secondary denominator audit arithmetic PASS")
    else:
        write(OUTPUT, result, exclusive=True)
        print(result)
