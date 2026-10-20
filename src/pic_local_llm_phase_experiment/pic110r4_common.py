"""R4 append-only identities, local environment and pre-inference freezes."""

from __future__ import annotations

import importlib.metadata as metadata
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pic_local_llm_phase_experiment.pic110r3_common import (
    DIGEST,
    MODEL,
    ROOT,
    WHEEL,
    canonical,
    head,
    normalized_hash,
    read,
    sha,
    write,
)

OUT = ROOT / "results/pic110r4"
DATA = ROOT / "tasks/pic110r4"
BASE = "b5275dff85d0c73024e0995d0b273d72f27795c0"


def settings() -> dict[str, Any]:
    return {
        "model": MODEL,
        "model_digest": DIGEST,
        "pic_version": "1.1.0",
        "pic_distribution_hash": WHEEL,
        "ollama_url": "http://localhost:11434",
        "temperature": 0,
        "top_p": 1,
        "seed": 20261020,
        "num_predict": 768,
        "num_ctx": 16384,
        "max_prompt_bytes": 24000,
        "max_input_tokens": 1752032,
        "max_output_tokens": 55360,
        "max_calls_including_warmup": 73,
        "max_wall_seconds": 3600,
        "request_timeout_seconds": 180,
        "max_consecutive_failures": 3,
        "max_ram_percent": 92,
        "think": False,
        "keep_alive": "10m",
        "retries": 0,
        "order_seed": 11042026,
        "reuse_sizes": [16, 4096, 65536],
        "reuse_fanouts": [1, 8],
        "reuse_repeats": 2,
        "reuse_wall_seconds": 1200,
        "worker_timeout_seconds": 90,
        "max_reuse_processes": 72,
    }


def preservation() -> dict:
    snapshot = read(OUT / "setup/preservation_before.json")
    changed = [
        name
        for name, expected in snapshot.items()
        if not (ROOT / name).is_file() or sha((ROOT / name).read_bytes()) != expected
    ]
    if changed:
        raise ValueError(f"Prior artifacts changed: {changed}")
    return {"status": "PASS", "protected_files": len(snapshot), "changed": []}


def environment() -> dict:
    import percolation_inversion_compiler as pic

    distribution = metadata.distribution("percolation-inversion-compiler")
    assert distribution.version == "1.1.0"
    assert Path(pic.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    hashes = read(OUT / "setup/installed_pic_hashes.json")
    for name, expected in hashes.items():
        assert sha(Path(str(distribution.locate_file(name))).read_bytes()) == expected, name
    return {"status": "PASS", "unchanged_wheel_payload_files": len(hashes)}


def freeze(phase: str) -> dict:
    files = [p for p in (ROOT / "src").rglob("*.py")]
    files += list((ROOT / "tests").glob("test_pic110r4.py"))
    files += list(DATA.glob("*.json"))
    files += [
        ROOT / "configs/experiment.pic-v1.1.0-r4.json",
        ROOT / "configs/requirements.pic110.lock",
        ROOT / "docs/PROTOCOL_PIC_1_1_0_R4.md",
        ROOT / "docs/REPRODUCIBILITY_PIC_1_1_0_R4.md",
        ROOT / "docs/PIC_1_1_0_R4_PREFLIGHT.json",
        ROOT / "docs/PIC_1_1_0_R4_INSPECTION.json",
        OUT / "setup/gold.json",
        OUT / "setup/schedule.json",
        OUT / "setup/preservation_before.json",
        OUT / "setup/installed_pic_hashes.json",
    ]
    result = {
        "phase": phase,
        "created_utc": datetime.now(UTC).isoformat(),
        "git_head": head(),
        "registration_scope": "Local pre-inference commit; not independently public timestamped",
        "hash_convention": "SHA256 with CRLF normalized to LF",
        "settings": settings(),
        "hashes": {p.relative_to(ROOT).as_posix(): normalized_hash(p) for p in sorted(files)},
    }
    write(OUT / f"prereg_{phase}.json", result, exclusive=True)
    write(ROOT / f"docs/PIC_1_1_0_R4_PREREG_{phase.upper()}.json", result, exclusive=True)
    return result


def frozen(phase: str) -> dict:
    result = read(OUT / f"prereg_{phase}.json")
    for name, expected in result["hashes"].items():
        assert normalized_hash(ROOT / name) == expected, name
    assert result["settings"] == settings()
    return result


__all__ = [
    "BASE",
    "DATA",
    "DIGEST",
    "MODEL",
    "OUT",
    "ROOT",
    "WHEEL",
    "canonical",
    "environment",
    "freeze",
    "frozen",
    "head",
    "preservation",
    "read",
    "settings",
    "sha",
    "write",
]
