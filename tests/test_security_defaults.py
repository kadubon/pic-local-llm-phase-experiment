from pathlib import Path

from pic_local_llm_phase_experiment.public_audit import run_audit
from pic_local_llm_phase_experiment.schemas import ExperimentConfig


def test_no_cloud_llm_dependencies() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8").lower()

    assert "openai" not in pyproject
    assert "anthropic" not in pyproject
    assert "google-generativeai" not in pyproject


def test_default_config_requires_no_api_key() -> None:
    config = ExperimentConfig()

    assert config.ollama_url == "http://localhost:11434"
    assert config.model == "qwen3.5:35b-a3b"
    assert config.experiment_mode == "separate_initial"


def test_readme_explains_pic_for_first_time_readers() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    compact_readme = " ".join(readme.split())

    assert "## What Is PIC?" in readme
    assert "finite certificate/verifier-routing and residual-ledger runtime" in compact_readme
    assert "not an ASI detector" in readme
    assert "`accepted` means `settled`" in readme


def test_readme_documents_full_experiment_readiness() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "## Before The Full Run" in readme
    assert "50 local Ollama generations" in readme
    assert "20 PIC intake calls" in readme
    assert "a short local Ollama streaming generation returns non-empty text" in readme
    assert "generation_retries: 1" in readme
    assert "disable_ollama_thinking: true" in readme
    assert "abort_on_generation_error: true" in readme
    assert "## v0.2.0 Shared-Initial Experiment" in readme
    assert "40 local Ollama generations" in readme
    assert "configs/experiment.shared_initial.yaml" in readme
    assert "uv run python scripts/setup_pic.py" in readme
    assert "uv run python scripts/smoke_check.py" in readme
    assert (
        "uv run python scripts/run_experiment.py --config configs/experiment.default.yaml" in readme
    )
    assert (
        "uv run python scripts/run_experiment.py --config configs/experiment.shared_initial.yaml"
    ) in readme
    assert "no cloud LLM APIs" in readme


def test_public_release_docs_are_scientifically_bounded() -> None:
    report = Path("docs/EXPERIMENT_REPORT_v0.1.0.md").read_text(encoding="utf-8")
    audit = Path("docs/PUBLIC_SAFETY_AUDIT_v0.1.0.md").read_text(encoding="utf-8")
    release = Path("RELEASE_v0.1.0.md").read_text(encoding="utf-8")
    report_v2 = Path("docs/EXPERIMENT_REPORT_v0.2.0.md").read_text(encoding="utf-8")
    template = Path("docs/EXPERIMENT_REPORT_v0.2.0_TEMPLATE.md").read_text(encoding="utf-8")
    audit_v2 = Path("docs/PUBLIC_SAFETY_AUDIT_v0.2.0.md").read_text(encoding="utf-8")
    release_v2 = Path("RELEASE_v0.2.0.md").read_text(encoding="utf-8")

    assert "Important Negative Result" in report
    assert "did not reduce missing obligations" in report
    assert "does not measure real ASI" in report
    assert "PIC did not mark any repaired output as settled" in release
    assert "Generated raw outputs remain ignored by git" in audit
    assert "Status: completed run" in report_v2
    assert "Important Negative Result" in report_v2
    assert "one PIC-assisted repair round did not improve" in report_v2
    assert "PIC is not an ASI detector" in report_v2
    assert "Status: pending run" in template
    assert "no fabricated metric table" in template
    assert "Status: completed run" in audit_v2
    assert "does not publish a new full-run result" not in release_v2
    assert "Average PIC missing-obligation delta: `-0.200`" in release_v2


def test_public_safety_audit_passes() -> None:
    assert run_audit(Path(".")) == []


def test_public_files_do_not_contain_local_paths_or_cloud_api_assumptions() -> None:
    roots = [
        Path("CHANGELOG.md"),
        Path("README.md"),
        Path("RELEASE_v0.1.0.md"),
        Path("RELEASE_v0.2.0.md"),
        Path("pyproject.toml"),
        Path("configs"),
        Path("docs"),
        Path("scripts"),
        Path("src"),
        Path("tasks"),
        Path("tests"),
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        else:
            files.extend(
                path
                for path in root.rglob("*")
                if path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix in {".md", ".py", ".toml", ".yaml", ".json"}
            )

    forbidden = [
        "C:" + "\\",
        "C:/" + "Us" + "ers",
        "One" + "Drive",
        "OPEN" + "AI_API",
        "ANTH" + "ROPIC",
        "api." + "openai",
        "api." + "anthropic",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert not any(pattern in text for pattern in forbidden), path.as_posix()
