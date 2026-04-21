"""
Tests for Milestone 3 baseline manifests and benchmark bundle tooling.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aletheia.baselines import (
    BaselineManifest,
    BaselinePublicationStatus,
    BaselineSignaturePolicy,
    check_baseline_reports,
    create_benchmark_bundle_manifest,
    load_baseline_manifest,
    render_baseline_commands,
    resolve_baseline_manifest_path,
    summarize_baseline_manifest,
    validate_baseline_manifest,
    write_benchmark_bundle_manifest,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent


def test_load_default_baseline_manifest() -> None:
    manifest = load_baseline_manifest()

    assert manifest.version == "v0.1"
    assert len(manifest.runs) == 14
    assert {run.provider.value for run in manifest.runs} == {
        "anthropic",
        "ollama",
        "openai",
        "xai",
    }


def test_baseline_manifest_summarizes_coverage() -> None:
    manifest = load_baseline_manifest()
    summary = summarize_baseline_manifest(manifest)

    assert summary["providers"]["ollama"] == 8
    assert summary["providers"]["xai"] == 4
    assert summary["statuses"]["historical"] == 4
    assert summary["statuses"]["planned"] == 3
    assert summary["statuses"]["published"] == 7
    assert summary["signature_policies"]["none"] == 4
    assert summary["signature_policies"]["ed25519"] == 10


def test_baseline_manifest_validates_existing_historical_reports() -> None:
    manifest = load_baseline_manifest()

    errors = validate_baseline_manifest(manifest)
    checks = check_baseline_reports(manifest)

    assert errors == []
    historical_checks = [
        check
        for check in checks
        if check.report_path is not None and check.signature_scheme is None
    ]
    published_checks = [check for check in checks if check.signature_scheme == "ed25519"]

    assert len(historical_checks) == 4
    assert all(check.signature_valid is None for check in historical_checks)
    assert all(check.policy_satisfied is True for check in historical_checks)
    assert len(published_checks) == 7
    assert all(check.signature_valid is True for check in published_checks)
    assert all(check.policy_satisfied is True for check in published_checks)


def test_baseline_commands_include_signing_for_ed25519_runs() -> None:
    manifest = load_baseline_manifest()

    commands = render_baseline_commands(manifest, Path("tmp/baselines"))

    assert len(commands) == len(manifest.runs)
    assert any("ALETHEIA_SIGNING_KEY_PATH" in command for command in commands)
    assert any("--model ollama/llama3.2:3b" in command for command in commands)
    assert any("--model ollama/gemma3:4b" in command for command in commands)
    assert any("--model xai/grok-3-mini" in command for command in commands)
    assert any(
        "--model xai/grok-4.20-0309-non-reasoning" in command for command in commands
    )
    assert any("--timeout-per-probe 120" in command for command in commands)
    assert any("--max-retries 0" in command for command in commands)
    assert any("--model replace-with-xai-litellm-model-id" in command for command in commands)
    assert all("uv run aletheia eval" in command for command in commands)


def test_published_baseline_requires_result_path() -> None:
    raw = {
        "version": "v0.1",
        "description": "Invalid publication manifest",
        "methodology": "docs/methodology/benchmark-release-v0.2.md",
        "runbook": "benchmarks/baselines/README.md",
        "runs": [
            {
                "id": "missing-report",
                "provider": "ollama",
                "model": "ollama/example",
                "suite": "quick",
                "family": "example",
                "benchmark_card": "docs/benchmark-cards/quick.md",
                "publication_status": BaselinePublicationStatus.PUBLISHED,
                "signature_policy": BaselineSignaturePolicy.ED25519,
            }
        ],
    }

    with pytest.raises(ValueError, match="must include result_path"):
        BaselineManifest(**raw)


def test_resolve_baseline_manifest_prefers_existing_relative_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_path = tmp_path / "baseline.yaml"
    manifest_path.write_text("version: v0.1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    resolved = resolve_baseline_manifest_path("baseline.yaml", tmp_path / "unused-root")

    assert resolved == Path("baseline.yaml")


def test_create_benchmark_bundle_manifest_hashes_requested_files(tmp_path: Path) -> None:
    asset = tmp_path / "asset.txt"
    asset.write_text("aletheia\n", encoding="utf-8")

    bundle = create_benchmark_bundle_manifest(
        include_paths=["asset.txt"],
        repo_root=tmp_path,
    )

    assert bundle["file_count"] == 1
    assert bundle["missing_paths"] == []
    assert bundle["files"][0]["path"] == "asset.txt"
    assert len(bundle["files"][0]["sha256"]) == 64


def test_write_benchmark_bundle_manifest(tmp_path: Path) -> None:
    asset = tmp_path / "asset.txt"
    output = tmp_path / "bundle.json"
    asset.write_text("aletheia\n", encoding="utf-8")

    write_benchmark_bundle_manifest(output, include_paths=["asset.txt"], repo_root=tmp_path)

    bundle = json.loads(output.read_text(encoding="utf-8"))
    assert bundle["schema_version"] == "benchmark-bundle-manifest/v1"
    assert bundle["file_count"] == 1
