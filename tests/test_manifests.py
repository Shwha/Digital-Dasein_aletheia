"""
Tests for external probe manifest loading and selection.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from aletheia.manifests import (
    load_probe_manifest,
    resolve_probe_manifest_path,
    select_manifest_probes,
)
from aletheia.models import DimensionName


def test_load_probe_manifest_enriches_metadata() -> None:
    manifest = load_probe_manifest("v0.1/contributor-smoke.yaml")

    assert manifest.version == "v0.1"
    assert len(manifest.probes) == 2
    assert {probe.id for probe in manifest.probes} == {
        "care.manifest.1",
        "unconcealment.manifest.1",
    }

    first_probe = manifest.probes[0]
    assert first_probe.metadata["source"] == "external_manifest"
    assert first_probe.metadata["manifest_version"] == "v0.1"
    assert first_probe.metadata["manifest_path"].endswith("v0.1/contributor-smoke.yaml")


def test_select_manifest_probes_filters_by_dimension_and_id() -> None:
    manifest = load_probe_manifest("v0.1/contributor-smoke.yaml")

    selected = select_manifest_probes(
        manifest,
        dimensions=[DimensionName.CARE.value],
        probe_ids=["care.manifest.1"],
    )

    assert len(selected) == 1
    assert selected[0].id == "care.manifest.1"
    assert selected[0].dimension == DimensionName.CARE


def test_select_manifest_probes_rejects_missing_ids() -> None:
    manifest = load_probe_manifest("v0.1/contributor-smoke.yaml")

    with pytest.raises(ValueError, match="missing requested probe IDs"):
        select_manifest_probes(manifest, probe_ids=["care.missing.99"])


def test_load_probe_manifest_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Probe manifest not found"):
        load_probe_manifest("missing.yaml", tmp_path)


def test_resolve_probe_manifest_path_prefers_existing_relative_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_path = tmp_path / "local-manifest.yaml"
    manifest_path.write_text("version: v0.1\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    resolved = resolve_probe_manifest_path("local-manifest.yaml", tmp_path / "unused-root")

    assert resolved == Path("local-manifest.yaml")
