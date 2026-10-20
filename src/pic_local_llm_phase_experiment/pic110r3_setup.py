"""Local-only inspection and metadata for R3; never generates model text."""

from __future__ import annotations

import importlib.metadata as metadata
import inspect
import json
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

from pic_local_llm_phase_experiment.pic110r3_common import (
    BASE,
    DATA,
    DIGEST,
    MODEL,
    OUT,
    ROOT,
    WHEEL,
    read,
    sha,
    write,
)


def inspect_environment() -> None:
    setup = OUT / "setup"
    setup.mkdir(parents=True, exist_ok=False)
    earlier = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASE], cwd=ROOT, text=True
    ).splitlines()
    paths = {ROOT / name for name in earlier}
    for folder in ("results", "reports", "external"):
        paths.update(
            p
            for p in (ROOT / folder).rglob("*")
            if p.is_file() and not p.is_relative_to(OUT) and "pic110r3" not in p.name
        )
    write(
        setup / "preservation_before.json",
        {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in sorted(paths) if p.is_file()},
        exclusive=True,
    )
    wheel = next(
        (ROOT / "results/pic110r2/setup").glob("percolation_inversion_compiler-1.1.0-*.whl")
    )
    assert sha(wheel.read_bytes()) == WHEEL
    dist = metadata.distribution("percolation-inversion-compiler")
    assert dist.version == "1.1.0"
    hashes = {}
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith("percolation_inversion_compiler/") and not name.endswith("/"):
                installed = Path(str(dist.locate_file(name))).read_bytes()
                assert installed == archive.read(name), name
                hashes[name] = sha(installed)
    session = requests.Session()
    session.trust_env = False
    models = session.get("http://localhost:11434/api/tags", timeout=10).json()
    assert any(m["name"] == MODEL and m["digest"] == DIGEST for m in models["models"])
    info = {
        "started_utc": datetime.now(UTC).isoformat(),
        "branch": subprocess.check_output(["git", "branch", "--show-current"], text=True).strip(),
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_status": subprocess.check_output(["git", "status", "--porcelain"], text=True),
        "protected_files": len(read(setup / "preservation_before.json")),
        "python": sys.version,
        "pic_version": dist.version,
        "wheel_sha256": WHEEL,
        "installed_content_sha256": sha(json.dumps(hashes, sort_keys=True).encode()),
        "installed_wheel_files_verified": len(hashes),
        "installed_wheel_mismatches": [],
        "ollama_version": session.get("http://localhost:11434/api/version", timeout=10).json(),
        "models": models,
        "dependencies": {d.metadata["Name"]: d.version for d in metadata.distributions()},
    }
    write(setup / "inspection.json", info, exclusive=True)
    write(setup / "installed_pic_hashes.json", hashes, exclusive=True)
    from percolation_inversion_compiler.adapters import domain
    from percolation_inversion_compiler.core import adapter_routes as ar
    from percolation_inversion_compiler.core.records import ExternalProofObligation
    from percolation_inversion_compiler.runtime import algorithms as ra
    from percolation_inversion_compiler.runtime import records as rr

    write(
        setup / "route_specs.json",
        [r.model_dump(mode="json") for r in ar.list_adapter_route_specs()],
        exclusive=True,
    )
    schemas: list[Any] = [
        ar.VerifierEvidenceEnvelope,
        ar.VerifierResolution,
        ar.EvidenceArtifact,
        ExternalProofObligation,
        rr.RuntimeStepInput,
        rr.RuntimeState,
    ]
    write(
        setup / "schemas.json", {c.__name__: c.model_json_schema() for c in schemas}, exclusive=True
    )
    functions: list[Any] = [
        domain.verify_ecpt_numerical_envelope,
        domain.verify_trc_telemetry_calibration,
        domain.replay_trc_physical_trace,
        domain.verify_archive_domain_evidence,
        ar.resolve_adapter_route,
        ra.resolve_step_evidence,
        ra.build_runtime_step,
        ra.promote_packet_candidate,
    ]
    (setup / "sdk_sources.txt").write_text(
        "\n\n".join(str(inspect.signature(fn)) + "\n" + inspect.getsource(fn) for fn in functions),
        encoding="utf-8",
    )
    for words in (
        ("agent", "check"),
        ("evidence", "verify"),
        ("evidence", "discharge"),
        ("runtime", "resolve-evidence"),
        ("runtime", "step"),
    ):
        proc = subprocess.run(
            [str(Path(sys.executable).with_name("pic.exe")), *words, "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=True,
        )
        (setup / ("_".join(words) + "_help.txt")).write_text(proc.stdout, encoding="utf-8")


def prepare_metadata() -> None:
    from pic_local_llm_phase_experiment.pic110r3_oracle import gold
    from pic_local_llm_phase_experiment.pic110r3_runner import schedule, settings
    from pic_local_llm_phase_experiment.pic110r3_tasks import dataset

    tasks, originals, delivery, trust = dataset()
    for name, value in (
        ("public.json", tasks),
        ("authoritative.json", originals),
        ("delivery.json", delivery),
        ("trusted_manifest.json", trust),
    ):
        assert read(DATA / name) == value
    expected = {t["task_id"]: gold(t, delivery[t["source_id"]], trust) for t in tasks}
    assert (
        sum(expected[t["task_id"]]["complete"] for t in tasks if t["panel"] == "confirmatory") == 7
    )
    write(OUT / "setup/gold.json", expected, exclusive=True)
    write(OUT / "setup/schedule.json", schedule(), exclusive=True)
    write(ROOT / "configs/experiment.pic-v1.1.0-r3.json", settings(), exclusive=True)
    info = read(OUT / "setup/inspection.json")
    keys = (
        "started_utc",
        "branch",
        "head",
        "git_status",
        "protected_files",
        "python",
        "pic_version",
        "wheel_sha256",
        "installed_content_sha256",
        "installed_wheel_files_verified",
        "installed_wheel_mismatches",
        "ollama_version",
    )
    write(ROOT / "docs/PIC_1_1_0_R3_INSPECTION.json", {k: info[k] for k in keys}, exclusive=True)
    print("R3 metadata saved; zero model calls; private gold isolated.")


if __name__ == "__main__":
    {"inspect": inspect_environment, "metadata": prepare_metadata}[sys.argv[1]]()
