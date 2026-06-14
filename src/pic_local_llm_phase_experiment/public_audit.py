from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".csv",
    ".gitignore",
    ".json",
    ".lock",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

PUBLIC_ROOTS = (
    ".gitattributes",
    ".gitignore",
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
    "RELEASE_v0.1.0.md",
    "configs",
    "docs",
    "pyproject.toml",
    "scripts",
    "src",
    "tasks",
    "tests",
    "uv.lock",
)

ALLOWED_TRACKED_ARTIFACTS = {
    "results/.gitkeep",
    "reports/.gitkeep",
}


@dataclass(frozen=True)
class AuditFinding:
    path: str
    label: str
    line: int | None = None

    def render(self) -> str:
        if self.line is None:
            return f"{self.path}: {self.label}"
        return f"{self.path}:{self.line}: {self.label}"


def _repo_files_from_git(root: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [root / line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _repo_files_from_roots(root: Path) -> list[Path]:
    files: list[Path] = []
    for raw in PUBLIC_ROOTS:
        path = root / raw
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
            continue
        files.extend(child for child in path.rglob("*") if child.is_file())
    return sorted(set(files))


def _public_files(root: Path) -> list[Path]:
    files = set(_repo_files_from_git(root))
    files.update(_repo_files_from_roots(root))
    return sorted(
        path
        for path in files
        if path.exists()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and path.suffix in TEXT_SUFFIXES
    )


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _forbidden_patterns() -> list[tuple[str, re.Pattern[str]]]:
    return [
        ("Windows absolute path", re.compile(re.escape("C:" + "\\"))),
        ("local home path fragment", re.compile("Us" + "ers", re.IGNORECASE)),
        ("local sync path fragment", re.compile("One" + "Drive", re.IGNORECASE)),
        ("cloud LLM key environment variable", re.compile("OPEN" + "AI_API")),
        ("cloud LLM key environment variable", re.compile("ANTH" + "ROPIC")),
        ("cloud LLM endpoint", re.compile(r"api\." + "openai", re.IGNORECASE)),
        ("cloud LLM endpoint", re.compile(r"api\." + "anthropic", re.IGNORECASE)),
        ("possible secret token", re.compile("sk-" + r"[A-Za-z0-9]")),
    ]


def scan_public_files(root: Path) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    patterns = _forbidden_patterns()
    for path in _public_files(root):
        rel = _relative(path, root)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(AuditFinding(rel, "non-UTF-8 public file"))
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in patterns:
                if pattern.search(line):
                    findings.append(AuditFinding(rel, label, line_number))
    return findings


def scan_tracked_artifacts(root: Path) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for path in _repo_files_from_git(root):
        rel = _relative(path, root)
        if rel in ALLOWED_TRACKED_ARTIFACTS:
            continue
        if rel.startswith(("external/", "results/", "reports/")):
            findings.append(AuditFinding(rel, "generated/local artifact is tracked"))
    return findings


def scan_release_version(root: Path, version: str) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    pyproject = root / "pyproject.toml"
    init_file = root / "src" / "pic_local_llm_phase_experiment" / "__init__.py"
    if pyproject.exists() and f'version = "{version}"' not in pyproject.read_text(encoding="utf-8"):
        findings.append(AuditFinding("pyproject.toml", f"version is not {version}"))
    if init_file.exists() and f'__version__ = "{version}"' not in init_file.read_text(
        encoding="utf-8"
    ):
        findings.append(
            AuditFinding(
                "src/pic_local_llm_phase_experiment/__init__.py",
                f"version is not {version}",
            )
        )
    return findings


def run_audit(root: Path, version: str = "0.1.0") -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    findings.extend(scan_public_files(root))
    findings.extend(scan_tracked_artifacts(root))
    findings.extend(scan_release_version(root, version))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the public-release safety audit.")
    parser.add_argument("--version", default="0.1.0")
    args = parser.parse_args(argv)

    root = Path.cwd()
    findings = run_audit(root=root, version=args.version)
    if findings:
        print("Public safety audit failed:")
        for finding in findings:
            print(f"- {finding.render()}")
        return 1

    scanned = len(_public_files(root))
    print(f"Public safety audit passed for v{args.version}. Scanned {scanned} public files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
