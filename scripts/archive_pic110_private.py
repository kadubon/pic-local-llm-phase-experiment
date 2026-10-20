"""Preserve raw data and exact frozen source bytes in an ignored local archive."""

from __future__ import annotations

import zipfile

from pic_local_llm_phase_experiment.pic110_runner import OUT, ROOT, read, sha, verify, write


def main() -> None:
    manifest = verify("main")
    archive = ROOT / "results/pic110-private-recorded-run.zip"
    if archive.exists():
        raise FileExistsError("private archive already exists; never overwrite")
    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in files:
            z.write(path, "raw/" + path.relative_to(OUT).as_posix())
        for relative in manifest["hashes"]:
            z.write(ROOT / relative, "frozen_source/" + relative)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("private archive failed CRC verification")
    write(
        ROOT / "docs/PIC_1_1_0_PRIVATE_ARCHIVE_IDENTITY.json",
        {
            "visibility": "LOCAL_IGNORED_NOT_PUBLISHED",
            "archive_basename": archive.name,
            "archive_sha256": sha(archive.read_bytes()),
            "archive_bytes": archive.stat().st_size,
            "raw_files": len(files),
            "frozen_source_files": len(manifest["hashes"]),
            "crc_verification": "PASS",
            "note": "Contains raw answers and private environment paths. Not a public artifact.",
        },
    )
    saved = read(ROOT / "docs/EXPERIMENT_SUMMARY_PIC_1_1_0.json")
    write(
        ROOT / "docs/PIC_1_1_0_ATTEMPT_LEDGER.json",
        {
            "campaign_status": saved["status"],
            "actual_calls_including_warmup": saved["campaign"]["calls"],
            "planned_task_generations": len(saved["rows"]),
            "attempts": [
                {
                    k: row[k]
                    for k in (
                        "task_id",
                        "panel",
                        "condition",
                        "attempt_status",
                        "error_or_timeout",
                        "prompt_hash",
                        "output_artifact_hash",
                        "token_usage",
                        "elapsed_time",
                    )
                }
                for row in saved["rows"]
            ],
        },
    )
    print(f"Private archive verified; {len(files)} raw files retained locally")


if __name__ == "__main__":
    main()
