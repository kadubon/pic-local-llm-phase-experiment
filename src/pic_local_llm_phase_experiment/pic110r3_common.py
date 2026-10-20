"""R3 identities, append-only artifacts and preservation; no inference on import."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/pic110r3"
DATA = ROOT / "tasks/pic110r3"
BASE = "ca788ca800b58b00995e056ecde05b389e18077c"
MODEL = "gemma4:e4b"
DIGEST = "dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c"
WHEEL = "2d23def1bb734d12a6746caeabcc76fdce985476ed126545caba4a16838c0bb7"
AS_OF = "2026-10-20T00:00:00+00:00"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: Any, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive and path.exists():
        raise FileExistsError(path.name)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def normalized_hash(path: Path) -> str:
    return sha(path.read_bytes().replace(b"\r\n", b"\n"))


def head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def preservation() -> dict[str, Any]:
    original = read(OUT / "setup/preservation_before.json")
    changed = [
        name
        for name, digest in original.items()
        if not (ROOT / name).is_file() or sha((ROOT / name).read_bytes()) != digest
    ]
    if changed:
        raise ValueError(f"Earlier artifacts changed: {changed}")
    return {"status": "PASS", "protected_files": len(original), "changed": []}
