"""Real finite verification cost, persisted producers and fresh consumer processes."""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
import time
from pathlib import Path

from pic_local_llm_phase_experiment.pic110r3_pic_adapter import diagnose
from pic_local_llm_phase_experiment.pic110r3_verifiers import verify
from pic_local_llm_phase_experiment.pic110r4_common import (
    OUT,
    ROOT,
    canonical,
    environment,
    frozen,
    preservation,
    read,
    settings,
    sha,
    write,
)


def fixture(size: int, name: str) -> dict:
    sid = f"source:{name}"
    payload = {
        "source_id": sid,
        "scope": f"scope:{name}",
        "issuer": "r4-finite-lab",
        "receiver_contexts": ["producer:lab", "consumer:lab"],
        "produced_at": "2026-01-01T00:00:00+00:00",
        "expires_at": "2100-01-01T00:00:00+00:00",
        "domain": "telemetry",
        "data": {"samples": [0] * size},
    }
    digest = sha(canonical(payload))
    task = {
        "source_id": sid,
        "scope": payload["scope"],
        "family": "telemetry",
        "parameters": {"references": [0] * size, "tolerance": 0.25},
    }
    return {
        "task": task,
        "delivery": {"payload": payload, "advertised_sha256": digest},
        "trust": {
            sid: {
                "sha256": digest,
                "issuer": payload["issuer"],
                "scope": payload["scope"],
                "permitted_tasks": [f"{name}:producer", f"{name}:consumer"],
            }
        },
    }


def worker(jobfile: Path) -> None:
    started = time.perf_counter()
    job = read(jobfile)
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
    previous = None
    if not producer:
        stored = Path(job["producer_file"])
        assert sha(stored.read_bytes()) == job["producer_sha256"]
        previous = read(stored)
        if job["mode"] == "cached":
            cache = previous["cache"]
    results = []
    last_pic = None
    for index in range(1 if producer else job["fanout"]):
        receipt = verify(
            task, data["delivery"], data["trust"], cache if job["mode"] != "no_cache" else None
        )
        pic = None
        if job["backend"] == "pic":
            saved = previous.get("pic") if previous and job["mode"] == "cached" else None
            pic = diagnose(
                task,
                data["delivery"],
                receipt,
                Path(job["output_dir"]) / f"check_{index}",
                cached_native=saved["native"] if saved else None,
                producer_packet=saved["protected_packet"] if saved else None,
            )
            last_pic = pic
        results.append(
            {
                "decision": receipt.decision,
                "trusted": receipt.trusted,
                "sufficient": receipt.sufficient,
                "cache_hit": receipt.cache_hit,
                "domain_calls": receipt.domain_calls,
                "native_calls": pic["native_calls"] if pic else 0,
                "pic_ready": pic["pic_ready"] if pic else None,
                "verified_packet_dependency": pic["reused_verified_packet_id"] if pic else None,
            }
        )
    result = {
        "backend": job["backend"],
        "mode": job["mode"],
        "name": job["name"],
        "size": job["size"],
        "fanout": job["fanout"],
        "results": results,
        "core_elapsed_seconds": time.perf_counter() - started,
    }
    if producer:
        result.update(cache=cache, pic=last_pic)
    write(Path(job["output"]), result, exclusive=True)


def grid() -> list[dict]:
    rng = random.Random(settings()["order_seed"] + 1)
    jobs = []
    for size in settings()["reuse_sizes"]:
        for fanout in settings()["reuse_fanouts"]:
            for repeat in range(settings()["reuse_repeats"]):
                arms = ["generic", "pic"]
                rng.shuffle(arms)
                for arm in arms:
                    modes = ["cached", "no_cache"]
                    rng.shuffle(modes)
                    jobs.append(
                        {
                            "size": size,
                            "fanout": fanout,
                            "repeat": repeat,
                            "backend": arm,
                            "consumer_order": modes,
                        }
                    )
    return jobs


def run() -> None:
    frozen("main")
    environment()
    preservation()
    folder = OUT / "reuse"
    folder.mkdir(exist_ok=False)
    start = time.perf_counter()
    records: list[dict] = []
    cases = []
    status = "COMPLETED"
    error = None
    try:
        for index, item in enumerate(grid()):
            name = f"r4reuse_{index:02d}"
            fd = folder / name
            fd.mkdir()
            write(fd / "fixture.json", fixture(item["size"], name), exclusive=True)
            runs = {}
            for mode in ["producer", *item["consumer_order"]]:
                if (
                    time.perf_counter() - start + settings()["worker_timeout_seconds"]
                    > settings()["reuse_wall_seconds"]
                ):
                    raise TimeoutError("Fixed reuse wall budget exhausted")
                assert len(records) < settings()["max_reuse_processes"]
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
                before = time.perf_counter()
                record = {**item, "mode": mode, "status": "STARTED"}
                records.append(record)
                write(folder / "attempts.json", records)
                try:
                    process = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pic_local_llm_phase_experiment.pic110r4_reuse",
                            "worker",
                            str(jobpath),
                        ],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        timeout=settings()["worker_timeout_seconds"],
                    )
                    record.update(
                        elapsed_seconds=time.perf_counter() - before,
                        exit_code=process.returncode,
                        status="OK" if process.returncode == 0 else "ERROR",
                    )
                    (fd / f"{mode}_stdout.txt").write_text(process.stdout, encoding="utf-8")
                    (fd / f"{mode}_stderr.txt").write_text(process.stderr, encoding="utf-8")
                    if process.returncode:
                        raise RuntimeError("Reuse worker failed; raw stderr retained")
                    runs[mode] = {
                        "parent_wall_seconds": record["elapsed_seconds"],
                        "worker": read(fd / f"{mode}.json"),
                    }
                except subprocess.TimeoutExpired:
                    record.update(elapsed_seconds=time.perf_counter() - before, status="TIMEOUT")
                    raise
                finally:
                    write(folder / "attempts.json", records)
            cases.append({**item, "name": name, "runs": runs})
            write(folder / "cases.json", cases)
            print(
                f"reuse {index + 1}/{len(grid())} {item['backend']} "
                f"n={item['size']} fanout={item['fanout']}",
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
                "actual_processes": len(records),
                "planned_conditions": len(grid()),
                "completed_conditions": len(cases),
                "elapsed_seconds": time.perf_counter() - start,
            },
        )
        preservation()
        environment()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["worker", "run"])
    parser.add_argument("job", nargs="?")
    args = parser.parse_args()
    worker(Path(args.job)) if args.action == "worker" else run()
