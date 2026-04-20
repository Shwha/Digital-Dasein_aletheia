"""
Versioned benchmark manifest loading.

Milestone 2 moves Aletheia toward contributor-owned benchmark content. This
module is the bridge: YAML probe manifests can be validated, selected by suite,
and executed by the existing runner without editing Python dimension modules.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from aletheia.models import DimensionName, Probe, ProbeManifest

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROBE_MANIFESTS_DIR = _REPO_ROOT / "benchmarks" / "probes"


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from disk and validate the top-level type."""
    if not path.exists():
        msg = f"Probe manifest not found: {path}"
        raise FileNotFoundError(msg)

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Probe manifest {path} must contain a YAML mapping, got {type(raw).__name__}"
        raise ValueError(msg)
    return raw


def resolve_probe_manifest_path(
    manifest_ref: str,
    manifests_dir: Path | None = None,
) -> Path:
    """Resolve a manifest reference to a concrete YAML path."""
    root = manifests_dir or DEFAULT_PROBE_MANIFESTS_DIR
    path = Path(manifest_ref).expanduser()

    if path.is_absolute():
        return path
    if path.suffix in {".yaml", ".yml"}:
        if path.exists():
            return path
        return root / path
    return root / path / "manifest.yaml"


def load_probe_manifest(
    manifest_ref: str,
    manifests_dir: Path | None = None,
) -> ProbeManifest:
    """Load and validate a versioned probe manifest."""
    manifest_path = resolve_probe_manifest_path(manifest_ref, manifests_dir)
    manifest = ProbeManifest(**_load_yaml_mapping(manifest_path))

    enriched_probes = []
    for probe in manifest.probes:
        metadata = {
            **probe.metadata,
            "source": "external_manifest",
            "manifest_version": manifest.version,
            "manifest_path": str(manifest_path),
        }
        enriched_probes.append(probe.model_copy(update={"metadata": metadata}))

    return manifest.model_copy(update={"probes": enriched_probes})


def select_manifest_probes(
    manifest: ProbeManifest,
    *,
    dimensions: list[str] | None = None,
    probe_ids: list[str] | None = None,
) -> list[Probe]:
    """Select manifest probes by dimension and/or explicit probe IDs."""
    dimension_filter = {DimensionName(dimension) for dimension in dimensions or []}
    probe_id_filter = set(probe_ids or [])

    selected = []
    for probe in manifest.probes:
        if dimension_filter and probe.dimension not in dimension_filter:
            continue
        if probe_id_filter and probe.id not in probe_id_filter:
            continue
        selected.append(probe)

    if probe_id_filter:
        selected_ids = {probe.id for probe in selected}
        missing = sorted(probe_id_filter - selected_ids)
        if missing:
            msg = f"Probe manifest is missing requested probe IDs: {', '.join(missing)}"
            raise ValueError(msg)

    return selected
