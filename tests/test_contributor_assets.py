"""
Tests for Milestone 2 contributor-facing benchmark assets.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from aletheia import __version__
from aletheia.config import load_suite
from aletheia.manifests import load_probe_manifest

_REPO_ROOT = Path(__file__).resolve().parent.parent


def test_required_contributor_assets_exist() -> None:
    required_paths = [
        _REPO_ROOT / "docs" / "contributors" / "README.md",
        _REPO_ROOT / "docs" / "contributors" / "probe-template.yaml",
        _REPO_ROOT / "docs" / "contributors" / "suite-template.yaml",
        _REPO_ROOT / "docs" / "contributors" / "dimension-guide.md",
        _REPO_ROOT / "docs" / "contributors" / "rubric-template.md",
        _REPO_ROOT / "docs" / "contributors" / "benchmark-quality-bar.md",
        _REPO_ROOT / "docs" / "contributors" / "suite-manifests.md",
        _REPO_ROOT / "docs" / "RELEASES.md",
        _REPO_ROOT / "docs" / "VERSIONING.md",
        _REPO_ROOT / "docs" / "providers.md",
        _REPO_ROOT / ".github" / "pull_request_template.md",
        _REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "probe.yml",
        _REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "benchmark-change.yml",
        _REPO_ROOT / "examples" / "providers" / "run-openai.sh",
        _REPO_ROOT / "examples" / "providers" / "run-anthropic.sh",
        _REPO_ROOT / "examples" / "providers" / "run-ollama.sh",
        _REPO_ROOT / "examples" / "providers" / "run-comparison.sh",
    ]

    for path in required_paths:
        assert path.exists(), f"Missing contributor asset: {path}"
        assert path.read_text(encoding="utf-8").strip()


def test_probe_template_is_valid_manifest() -> None:
    template_path = _REPO_ROOT / "docs" / "contributors" / "probe-template.yaml"
    manifest = load_probe_manifest(str(template_path.resolve()))

    assert manifest.version == "v0.1"
    assert manifest.probes[0].id == "care.example.1"
    assert manifest.probes[0].metadata["source"] == "external_manifest"


def test_suite_template_is_valid_suite_config() -> None:
    contributors_dir = _REPO_ROOT / "docs" / "contributors"
    suite = load_suite("suite-template", contributors_dir)

    assert suite.name == "contributor-template"
    assert suite.probe_manifest == "v0.1/contributor-smoke.yaml"
    assert suite.probe_ids == ["care.manifest.1"]


def test_package_version_matches_runtime_version() -> None:
    pyproject = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["version"] == __version__
