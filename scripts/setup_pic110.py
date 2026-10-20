"""Verify an isolated public-wheel installation and one bounded local warmup.

Run with the independent environment after installing its hash-locked profile.
No installation, model download, server launch or external repository mutation.
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import psutil
import requests

from pic_local_llm_phase_experiment.pic110_runner import OUT, ROOT, settings, sha, write


def main() -> int:
    cfg = settings()
    setup = OUT / "setup"
    setup.mkdir(parents=True, exist_ok=True)
    if (setup / "warmup_response.json").exists():
        raise FileExistsError("existing warmup is preserved; use a fresh result directory/checkout")
    metadata = requests.get(
        "https://pypi.org/pypi/percolation-inversion-compiler/1.1.0/json", timeout=30
    )
    metadata.raise_for_status()
    data = metadata.json()
    write(setup / "pypi.json", data)
    wheel = next(f for f in data["urls"] if f["packagetype"] == "bdist_wheel")
    if wheel["digests"]["sha256"] != cfg["pic_distribution_hash"]:
        raise ValueError("PyPI identity differs from fixed protocol")
    wheel_path = setup / wheel["filename"]
    if not wheel_path.exists():
        download = requests.get(wheel["url"], timeout=60)
        download.raise_for_status()
        wheel_path.write_bytes(download.content)
    if sha(wheel_path.read_bytes()) != cfg["pic_distribution_hash"]:
        raise ValueError("downloaded wheel hash mismatch")
    import percolation_inversion_compiler as pic

    if importlib.metadata.version("percolation-inversion-compiler") != cfg["pic_version"]:
        raise ValueError("installed PIC version mismatch")
    if not Path(pic.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise ValueError("PIC import is outside this environment")
    direct = json.loads(
        importlib.metadata.distribution("percolation-inversion-compiler").read_text(
            "direct_url.json"
        )
        or "{}"
    )
    if direct.get("dir_info", {}).get("editable"):
        raise ValueError("editable PIC is forbidden for this experiment")
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "uv": subprocess.check_output(["uv", "--version"], text=True).strip(),
        "pic_version": cfg["pic_version"],
        "pic_import": pic.__file__,
        "ram_bytes": psutil.virtual_memory().total,
        "logical_cpus": psutil.cpu_count(),
        "base_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "initial_git_status": subprocess.check_output(
            ["git", "status", "--short"], cwd=ROOT, text=True
        ),
    }
    try:
        tags = requests.get(cfg["ollama_url"] + "/api/tags", timeout=10)
        tags.raise_for_status()
        environment["tags"] = tags.json()
        version = requests.get(cfg["ollama_url"] + "/api/version", timeout=10)
        version.raise_for_status()
        environment["ollama"] = version.json()
        selected = next(
            (m for m in environment["tags"]["models"] if m["name"] == cfg["model"]), None
        )
        if selected is None or selected["digest"] != cfg["model_digest"]:
            raise ValueError("configured local model/digest is unavailable; no automatic pull")
    except (ValueError, requests.RequestException) as exc:
        write(setup / "environment_private.json", environment)
        write(setup / "blocked.json", {"status": "ENVIRONMENT_BLOCKED", "error": str(exc)})
        print("ENVIRONMENT_BLOCKED; no task inference performed")
        return 2
    write(setup / "environment_private.json", environment)
    payload = {
        "model": cfg["model"],
        "prompt": "Compute 17 + 26. Reply with only a JSON object containing key answer "
        "and the integer value.",
        "stream": False,
        "think": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0,
            "top_p": 1,
            "seed": 20261020,
            "num_predict": 64,
            "num_ctx": 8192,
        },
    }
    write(setup / "warmup_request.json", payload)
    started = time.perf_counter()
    try:
        response = requests.post(
            cfg["ollama_url"] + "/api/generate", json=payload, timeout=(10, 180)
        )
        response.raise_for_status()
        result = response.json()
    except (ValueError, requests.RequestException) as exc:
        result = {"error": str(exc)}
    result["wall_seconds"] = time.perf_counter() - started
    write(setup / "warmup_response.json", result)
    if not result.get("response") or not result.get("done"):
        print("ENVIRONMENT_BLOCKED: warmup failed; retained response")
        return 2
    print("Verified public wheel, model identity and bounded real local warmup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
