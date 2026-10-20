"""Recalculate primary paired estimates from the sanitized, saved per-task metrics.

This checks arithmetic reproducibility. Raw answers are needed to audit grading.
"""

from __future__ import annotations

import json

from pic_local_llm_phase_experiment.pic110_analysis import summarize
from pic_local_llm_phase_experiment.pic110_runner import ROOT, read, settings


def main() -> None:
    saved = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0.json")
    rows = [r for r in saved["rows"] if r["panel"] == "confirmatory"]
    recomputed = summarize(rows, settings())
    expected = saved["panels"]["confirmatory"]
    for key in ("success_paired", "false_completion_paired", "families"):
        if recomputed[key] != expected[key]:
            raise ValueError(f"published metric differs: {key}")
    print(
        json.dumps(
            {k: recomputed[k] for k in ("success_paired", "false_completion_paired")}, indent=2
        )
    )


if __name__ == "__main__":
    main()
