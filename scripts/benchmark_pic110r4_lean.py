"""Separately registered import-isolated cost replication; never edits PIC or R4."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROFILE = "pic110r4lean"


def generic_worker(path: Path) -> None:
    from pic_local_llm_phase_experiment.pic110r3_verifiers import verify
    from pic_local_llm_phase_experiment.pic110r4_common import read, sha, write

    started = time.perf_counter()
    job = read(path)
    data = read(Path(job["fixture"]))
    producer = job["mode"] == "producer"
    role = "producer" if producer else "consumer"
    task = {
        **data["task"],
        "task_id": f"{job['name']}:{role}",
        "receiver": f"{role}:lab",
        "evidence_id": f"ev:{job['name']}:{role}",
        "obligation_id": f"ob:{job['name']}:{role}",
    }
    cache = {}
    if not producer:
        source = Path(job["producer_file"])
        assert sha(source.read_bytes()) == job["producer_sha256"]
        if job["mode"] == "cached":
            cache = read(source)["cache"]
    results = []
    for _ in range(1 if producer else job["fanout"]):
        receipt = verify(
            task, data["delivery"], data["trust"], cache if job["mode"] != "no_cache" else None
        )
        results.append(
            {
                "decision": receipt.decision,
                "trusted": receipt.trusted,
                "sufficient": receipt.sufficient,
                "cache_hit": receipt.cache_hit,
                "domain_calls": receipt.domain_calls,
                "native_calls": 0,
                "pic_ready": None,
                "verified_packet_dependency": None,
            }
        )
    value = {
        "backend": "generic",
        "mode": job["mode"],
        "name": job["name"],
        "size": job["size"],
        "fanout": job["fanout"],
        "results": results,
        "core_elapsed_seconds": time.perf_counter() - started,
    }
    if producer:
        value.update(cache=cache, pic=None)
    write(Path(job["output"]), value, exclusive=True)


def worker(path: Path) -> None:
    job = json.loads(path.read_text())
    if job["backend"] == "generic":
        generic_worker(path)
    else:
        from pic_local_llm_phase_experiment.pic110r4_reuse import worker as original_worker

        original_worker(path)
    output = Path(job["output"])
    value = json.loads(output.read_text())
    loaded = any(name.startswith("percolation_inversion_compiler") for name in sys.modules)
    assert loaded == (job["backend"] == "pic")
    value.update(pic_module_imported=loaded, worker_pid=os.getpid())
    output.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def registration() -> dict:
    from datetime import UTC, datetime

    from pic_local_llm_phase_experiment.pic110r4_common import (
        OUT,
        ROOT,
        head,
        settings,
        sha,
    )
    from pic_local_llm_phase_experiment.pic110r4_reuse import grid

    files = [
        Path(__file__).resolve(),
        ROOT / "docs/PROTOCOL_PIC_1_1_0_R4_LEAN.md",
        ROOT / "src/pic_local_llm_phase_experiment/pic110r4_reuse.py",
        ROOT / "src/pic_local_llm_phase_experiment/pic110r4_common.py",
        ROOT / "src/pic_local_llm_phase_experiment/pic110r3_verifiers.py",
        ROOT / "src/pic_local_llm_phase_experiment/pic110r3_pic_adapter.py",
        OUT / "setup/installed_pic_hashes.json",
    ]
    return {
        "registered_utc": datetime.now(UTC).isoformat(),
        "git_head": head(),
        "scope": "Separate cost replication before any reuse results; no R4 amendment",
        "hashes": {
            p.relative_to(ROOT).as_posix(): sha(p.read_bytes().replace(b"\r\n", b"\n"))
            for p in files
        },
        "settings": settings(),
        "grid": grid(),
    }


def frozen() -> dict:
    from pic_local_llm_phase_experiment.pic110r4_common import ROOT, read, sha

    result = read(ROOT / "results" / PROFILE / "prereg.json")
    for name, expected in result["hashes"].items():
        assert sha((ROOT / name).read_bytes().replace(b"\r\n", b"\n")) == expected, name
    return result


def run() -> None:
    from pic_local_llm_phase_experiment.pic110r4_common import (
        ROOT,
        environment,
        preservation,
        read,
        settings,
        sha,
        write,
    )
    from pic_local_llm_phase_experiment.pic110r4_reuse import fixture

    registered = frozen()
    environment()
    preservation()
    folder = ROOT / "results" / PROFILE / "run"
    folder.mkdir(exist_ok=False)
    started = time.perf_counter()
    attempts: list[dict] = []
    cases = []
    status = "COMPLETED"
    error = None
    try:
        for index, item in enumerate(registered["grid"]):
            name = f"r4lean_{index:02d}"
            fd = folder / name
            fd.mkdir()
            write(fd / "fixture.json", fixture(item["size"], name), exclusive=True)
            runs = {}
            for mode in ["producer", *item["consumer_order"]]:
                if time.perf_counter() - started + 90 > settings()["reuse_wall_seconds"]:
                    raise TimeoutError("Predeclared lean cost wall limit")
                assert len(attempts) < 72
                job = {
                    **item,
                    "mode": mode,
                    "name": name,
                    "fixture": str(fd / "fixture.json"),
                    "output_dir": str(fd / mode),
                    "output": str(fd / f"{mode}.json"),
                }
                if mode != "producer":
                    job.update(
                        producer_file=str(fd / "producer.json"),
                        producer_sha256=sha((fd / "producer.json").read_bytes()),
                    )
                jobpath = fd / f"job_{mode}.json"
                write(jobpath, job, exclusive=True)
                record = {**item, "mode": mode, "status": "STARTED"}
                attempts.append(record)
                write(folder / "attempts.json", attempts)
                before = time.perf_counter()
                process = subprocess.run(
                    [sys.executable, str(Path(__file__).resolve()), "worker", str(jobpath)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=90,
                )
                record.update(
                    parent_wall_seconds=time.perf_counter() - before,
                    status="OK" if process.returncode == 0 else "ERROR",
                    exit_code=process.returncode,
                )
                write(folder / "attempts.json", attempts)
                (fd / f"{mode}_stderr.txt").write_text(process.stderr, encoding="utf-8")
                if process.returncode:
                    raise RuntimeError("Lean cost worker failed; raw stderr retained")
                runs[mode] = {
                    "parent_wall_seconds": record["parent_wall_seconds"],
                    "worker": read(Path(job["output"])),
                }
            cases.append({**item, "name": name, "runs": runs})
            write(folder / "cases.json", cases)
            print(
                f"lean cost {index + 1}/24 {item['backend']} n={item['size']} "
                f"fanout={item['fanout']}",
                flush=True,
            )
    except (OSError, RuntimeError, TimeoutError, subprocess.TimeoutExpired, AssertionError) as exc:
        status = "INCOMPLETE"
        error = str(exc)
    finally:
        write(
            folder / "panel.json",
            {
                "status": status,
                "stop_reason": error,
                "planned_processes": 72,
                "actual_processes": len(attempts),
                "planned_conditions": 24,
                "completed_conditions": len(cases),
                "elapsed_seconds": time.perf_counter() - started,
            },
        )
        frozen()
        environment()
        preservation()


def analyze() -> None:
    from pic_local_llm_phase_experiment.pic110r4_analysis import reuse_summary
    from pic_local_llm_phase_experiment.pic110r4_common import ROOT, read, write

    frozen()
    fd = ROOT / "results" / PROFILE / "run"
    rows = reuse_summary(read(fd / "cases.json"))
    imports = [
        {
            "name": c["name"],
            "backend": c["backend"],
            "all_workers_imported_pic": all(
                r["worker"]["pic_module_imported"] for r in c["runs"].values()
            ),
            "no_workers_imported_pic": all(
                not r["worker"]["pic_module_imported"] for r in c["runs"].values()
            ),
        }
        for c in read(fd / "cases.json")
    ]
    value = {
        "scope": "Separately preregistered import-isolated cost replication",
        "panel": read(fd / "panel.json"),
        "rows": rows,
        "imports": imports,
        "interpretation": "Two repeats per cell; not a general break-even estimate",
    }
    write(ROOT / "docs/PIC_1_1_0_R4_LEAN_RESULTS.json", value, exclusive=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "worker", "run", "analyze"])
    parser.add_argument("job", nargs="?")
    args = parser.parse_args()
    if args.action == "worker":
        worker(Path(args.job))
    elif args.action == "freeze":
        from pic_local_llm_phase_experiment.pic110r4_common import ROOT, write

        value = registration()
        write(ROOT / "results" / PROFILE / "prereg.json", value, exclusive=True)
        write(ROOT / "docs/PIC_1_1_0_R4_LEAN_PREREG.json", value, exclusive=True)
    elif args.action == "run":
        run()
    else:
        analyze()


if __name__ == "__main__":
    main()
