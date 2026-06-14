from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pic_local_llm_phase_experiment.paths import ensure_dir, write_json

PIC_REPO_URL = "https://github.com/kadubon/percolation-inversion-compiler"
PIC_DIR = Path("external") / "percolation-inversion-compiler"


def _tail(text: str, limit: int = 2000) -> str:
    return text[-limit:] if len(text) > limit else text


def _run(args: list[str], *, cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    return {
        "args": args,
        "returncode": completed.returncode,
        "stdout_tail": _tail(completed.stdout),
        "stderr_tail": _tail(completed.stderr),
    }


def _command_ok(step: dict[str, Any]) -> bool:
    return int(step.get("returncode", 1)) == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clone, install, and verify PIC locally.")
    parser.parse_args(argv)

    root = Path.cwd()
    ensure_dir(root / "external")
    ensure_dir(root / "results")

    steps: dict[str, Any] = {}
    manifest: dict[str, Any] = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "pic_repo_url": PIC_REPO_URL,
        "pic_checkout": PIC_DIR.as_posix(),
    }

    try:
        pic_path = root / PIC_DIR
        if pic_path.exists():
            steps["clone"] = {
                "skipped": True,
                "reason": "PIC checkout already exists; leaving it untouched.",
            }
            print("PIC checkout already exists; leaving it untouched.")
        else:
            steps["clone"] = _run(["git", "clone", PIC_REPO_URL, PIC_DIR.as_posix()], cwd=root)
            if not _command_ok(steps["clone"]):
                raise RuntimeError("git clone failed")

        steps["pic_commit"] = _run(
            ["git", "-C", PIC_DIR.as_posix(), "rev-parse", "HEAD"],
            cwd=root,
        )
        if _command_ok(steps["pic_commit"]):
            manifest["pic_commit"] = steps["pic_commit"]["stdout_tail"].strip()
            print(f"PIC commit: {manifest['pic_commit']}")
        else:
            manifest["pic_commit"] = "unknown"

        steps["install"] = _run(["uv", "pip", "install", "-e", PIC_DIR.as_posix()], cwd=root)
        if not _command_ok(steps["install"]):
            raise RuntimeError("uv editable install failed")

        steps["pic_help"] = _run(["pic", "--help"], cwd=root)
        if not _command_ok(steps["pic_help"]):
            raise RuntimeError("`pic --help` failed")

        steps["pic_version"] = _run(["pic", "--version"], cwd=root)
        if _command_ok(steps["pic_version"]):
            manifest["pic_version"] = steps["pic_version"]["stdout_tail"].strip()

        steps["pic_agent_explain"] = _run(["pic", "agent", "explain"], cwd=root)
        manifest["pic_agent_explain_available"] = _command_ok(steps["pic_agent_explain"])
        manifest["status"] = "ok"
    except RuntimeError as exc:
        manifest["status"] = "failed"
        manifest["error"] = str(exc)
        manifest["steps"] = steps
        write_json(root / "results" / "setup_manifest.json", manifest)
        print(f"Setup failed: {exc}")
        return 1

    manifest["steps"] = steps
    write_json(root / "results" / "setup_manifest.json", manifest)
    print("PIC setup verification complete. Wrote results/setup_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
