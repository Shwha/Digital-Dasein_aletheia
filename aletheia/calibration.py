"""
Calibration corpus loading and validation.

The calibration corpus is the bridge between philosophical intent and benchmark
credibility: a versioned, inspectable set of labeled examples that lets us
measure whether scoring changes help, hurt, or merely reshuffle brittleness.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from aletheia.models import (
    CalibrationCorpus,
    CalibrationLabel,
    CalibrationManifest,
    CalibrationRegistry,
    CalibrationSourceType,
    DimensionName,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CALIBRATION_DIR = _REPO_ROOT / "benchmarks" / "calibration"


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from disk and validate the top-level type."""
    if not path.exists():
        msg = f"Calibration file not found: {path}"
        raise FileNotFoundError(msg)

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Calibration file {path} must contain a YAML mapping, got {type(raw).__name__}"
        raise ValueError(msg)
    return raw


def load_calibration_registry(calibration_dir: Path | None = None) -> CalibrationRegistry:
    """Load the calibration registry that declares the current corpus version."""
    root = calibration_dir or DEFAULT_CALIBRATION_DIR
    registry_path = root / "registry.yaml"
    raw = _load_yaml_mapping(registry_path)
    return CalibrationRegistry(**raw)


def load_calibration_corpus(
    version: str | None = None,
    calibration_dir: Path | None = None,
) -> CalibrationCorpus:
    """Load a versioned calibration corpus from disk."""
    from aletheia.models import CalibrationCaseFile

    root = calibration_dir or DEFAULT_CALIBRATION_DIR
    registry = load_calibration_registry(root)
    target_version = version or registry.current_version

    if target_version not in registry.versions:
        available = ", ".join(registry.versions)
        msg = f"Calibration version '{target_version}' is not registered. Available: {available}"
        raise ValueError(msg)

    version_dir = root / target_version
    manifest = CalibrationManifest(**_load_yaml_mapping(version_dir / "manifest.yaml"))

    if manifest.version != target_version:
        msg = (
            f"Manifest version mismatch: registry requested {target_version}, "
            f"but manifest declares {manifest.version}."
        )
        raise ValueError(msg)

    annotation_guide_path = (version_dir / manifest.annotation_guide).resolve()
    if not annotation_guide_path.exists():
        msg = (
            f"Calibration annotation guide not found for {target_version}: {annotation_guide_path}"
        )
        raise FileNotFoundError(msg)

    case_files = [
        CalibrationCaseFile(**_load_yaml_mapping(version_dir / relative_path))
        for relative_path in manifest.case_files
    ]

    return CalibrationCorpus(version=target_version, manifest=manifest, case_files=case_files)


def summarize_calibration_corpus(
    corpus: CalibrationCorpus,
) -> dict[DimensionName, dict[CalibrationLabel, int]]:
    """Count labels for each dimension in the loaded corpus."""
    summary: dict[DimensionName, Counter[CalibrationLabel]] = {}

    for example in corpus.examples:
        counter = summary.setdefault(example.dimension, Counter())
        counter[example.label] += 1

    return {
        dimension: {label: counts.get(label, 0) for label in CalibrationLabel}
        for dimension, counts in summary.items()
    }


def count_probe_regression_examples(corpus: CalibrationCorpus) -> int:
    """Count examples that can run directly against current engine probes."""
    return sum(1 for example in corpus.examples if example.probe_id is not None)


def validate_calibration_corpus(corpus: CalibrationCorpus) -> list[str]:
    """Validate coverage and manifest consistency for the loaded corpus."""
    errors: list[str] = []
    required_labels = set(corpus.manifest.required_labels)
    declared_dimensions = set(corpus.manifest.dimensions)
    case_dimensions = {case_file.dimension for case_file in corpus.case_files}

    if declared_dimensions != case_dimensions:
        missing_cases = declared_dimensions - case_dimensions
        extra_cases = case_dimensions - declared_dimensions
        if missing_cases:
            names = ", ".join(sorted(d.value for d in missing_cases))
            errors.append(f"Manifest dimensions missing case files: {names}")
        if extra_cases:
            names = ", ".join(sorted(d.value for d in extra_cases))
            errors.append(f"Case files present for undeclared dimensions: {names}")

    examples = corpus.examples
    if not examples:
        errors.append("Calibration corpus contains no examples.")
        return errors

    example_ids = Counter(example.id for example in examples)
    duplicate_ids = sorted(example_id for example_id, count in example_ids.items() if count > 1)
    if duplicate_ids:
        errors.append(f"Duplicate example IDs across corpus: {', '.join(duplicate_ids)}")

    summary = summarize_calibration_corpus(corpus)
    for dimension in sorted(declared_dimensions, key=lambda dim: dim.value):
        counts = summary.get(dimension, {})
        total = sum(counts.values())
        if total < corpus.manifest.minimum_examples_per_dimension:
            errors.append(
                f"{dimension.value} has {total} examples; "
                f"minimum is {corpus.manifest.minimum_examples_per_dimension}"
            )
        labels_present = {label for label, count in counts.items() if count > 0}
        missing_labels = required_labels - labels_present
        if missing_labels:
            missing = ", ".join(sorted(label.value for label in missing_labels))
            errors.append(f"{dimension.value} is missing required labels: {missing}")

    errors.extend(
        f"{example.id} is marked as fixed_failure but does not define a probe_id."
        for example in examples
        if example.source_type == CalibrationSourceType.FIXED_FAILURE and example.probe_id is None
    )

    return errors
