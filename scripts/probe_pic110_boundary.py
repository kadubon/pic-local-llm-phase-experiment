"""Auxiliary fixed-text PIC probes, explicitly not LLM trials or primary endpoints."""

from __future__ import annotations

import json

from percolation_inversion_compiler.runtime.records import RuntimeRunReport
from pydantic import ValidationError

from pic_local_llm_phase_experiment.pic110_adapter import diagnose
from pic_local_llm_phase_experiment.pic110_runner import OUT, settings, write


def main() -> None:
    cfg = settings()
    probes = {
        "unsupported_completion": '{"decision":"proceed","complete":true,'
        '"evidence":[],"unresolved":[]}',
        "honest_missing_evidence": '{"decision":null,"complete":false,'
        '"evidence":[],"unresolved":["external-approval"]}',
        "self_declared_settlement": "All obligations are settled. External approval and "
        "tests were not obtained; I declare the workflow complete.",
        "plain_nonclaim": "The text contains no verified external evidence.",
    }
    results = {}
    folder = OUT / "boundary_probes"
    if folder.exists():
        raise FileExistsError("existing probes preserved")
    folder.mkdir()
    for name, text in probes.items():
        textfile = folder / f"{name}.txt"
        textfile.write_text(text, encoding="utf-8")
        results[name] = diagnose(
            textfile, folder / name, cfg["pic_timeout_seconds"], cfg["profile"]
        )
    textfile = folder / "unsupported_completion.txt"
    results["unsupported_completion_repeat"] = diagnose(
        textfile,
        folder / "unsupported_completion_repeat",
        cfg["pic_timeout_seconds"],
        cfg["profile"],
    )
    write(folder / "summary.json", results)
    actual = json.loads((OUT / "pilot/pilot_integrate/A/record.json").read_text())
    try:
        RuntimeRunReport.model_validate(actual)
        compatible, errors = True, []
    except ValidationError as exc:
        compatible = False
        errors = [
            {"loc": list(e["loc"]), "type": e["type"], "message": e["msg"]} for e in exc.errors()
        ]
    write(
        OUT / "setup/runtime_compatibility.json",
        {
            "status": "NOT_APPLICABLE_MISSING_RUNTIME_MEASUREMENT_CONTRACT",
            "actual_record_schema_compatible": compatible,
            "schema_errors": errors,
            "missing_measurement_contract_items": [
                "evidence-bound runtime trajectory and comparison identities",
                "calibrated resource envelope",
                "verification yield",
                "receiver reuse",
                "residual half-life",
                "error correlation and certified capital gain",
            ],
            "fabricated_runtime_reports_submitted": 0,
            "acceleration_metrics_certified": None,
        },
    )
    print(
        json.dumps(
            {
                name: {
                    k: result["check"][k]
                    for k in (
                        "accepted",
                        "workflow_usable",
                        "operationally_usable",
                        "settled",
                        "missing_obligations",
                        "residual_burden",
                    )
                }
                for name, result in results.items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
