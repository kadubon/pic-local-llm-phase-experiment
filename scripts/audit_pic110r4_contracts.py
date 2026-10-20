"""Descriptive details for protocol-declared secondary endpoints; never rescore."""

from __future__ import annotations

import json

from pic_local_llm_phase_experiment.pic110_oracle import parse_answer
from pic_local_llm_phase_experiment.pic110r4_common import (
    DATA,
    OUT,
    ROOT,
    frozen,
    read,
    sha,
    write,
)
from pic_local_llm_phase_experiment.pic110r4_oracle import expected, normalized


def audit() -> None:
    frozen("main")
    summary = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R4.json")
    assert all(p["status"] != "RUNNING" for p in summary["panels"].values())
    cases = {c["task_id"]: c for c in read(DATA / "cases.json")}
    rows = []
    private = []
    for row in summary["rows"]:
        case = cases[row["task_id"]]
        gold = expected(case)
        kind = "full" if row["arm"] == "P_full" else "minimal"
        path = OUT / row["panel"] / row["task_id"] / kind / "answer.txt"
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        try:
            parsed = parse_answer(text)
        except (TypeError, ValueError):
            parsed = {}
        refs = normalized(parsed.get("evidence"))
        unresolved = normalized(parsed.get("unresolved"))
        missing = sorted(set(gold["unresolved"]) - (unresolved or set()))
        extra = sorted((unresolved or set()) - set(gold["unresolved"]))
        invalid = sorted((refs or set()) - set(gold["evidence_ids"]))
        try:
            raw = json.loads(text)
            raw_only = type(raw) is dict
        except (ValueError, TypeError):
            raw_only = False
        private.append(
            {
                "task_id": row["task_id"],
                "arm": row["arm"],
                "extra_obligation_strings": extra,
                "invalid_reference_strings": invalid,
            }
        )
        rows.append(
            {
                "task_id": row["task_id"],
                "panel": row["panel"],
                "arm": row["arm"],
                "missing_expected_obligation_ids": missing,
                "extra_obligation_count": len(extra),
                "extra_obligation_sha256": [sha(x.encode()) for x in extra],
                "invalid_reference_count": len(invalid),
                "invalid_reference_sha256": [sha(x.encode()) for x in invalid],
                "raw_json_object_without_wrapper": raw_only,
                "frozen_supported_success": row["grade"]["supported_success"],
                "frozen_contract_success": row["grade"]["contract_success"],
            }
        )
    totals = {}
    for arm in ("G_minimal", "P_minimal", "P_full"):
        selected = [r for r in rows if r["arm"] == arm and r["panel"] == "confirmatory"]
        totals[arm] = {
            "planned": len(selected),
            "missing_obligation_ids": sum(
                len(r["missing_expected_obligation_ids"]) for r in selected
            ),
            "outputs_with_extra_obligations": sum(
                r["extra_obligation_count"] > 0 for r in selected
            ),
            "outputs_with_invalid_references": sum(
                r["invalid_reference_count"] > 0 for r in selected
            ),
            "raw_json_without_wrapper": sum(r["raw_json_object_without_wrapper"] for r in selected),
        }
    write(OUT / "contract_audit_private.json", private, exclusive=True)
    write(
        ROOT / "docs/PIC_1_1_0_R4_CONTRACT_AUDIT.json",
        {
            "scope": "Descriptive protocol-declared secondary details; all frozen grades unchanged",
            "model_calls_added": 0,
            "summary_sha256": sha(
                (ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0_R4.json")
                .read_bytes()
                .replace(b"\r\n", b"\n")
            ),
            "free_text_publication": "Unexpected model strings are represented only by hashes",
            "confirmatory": totals,
            "rows": rows,
        },
        exclusive=True,
    )
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    audit()
