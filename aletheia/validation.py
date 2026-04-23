"""
Held-out validation corpus loading and scorer quality reporting.

Calibration explains what the benchmark is trying to measure. Held-out
validation asks the harder question: does the current scorer generalize to
examples it was not tuned against?
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from aletheia.calibration import DEFAULT_CALIBRATION_DIR, load_calibration_corpus
from aletheia.dimensions import DIMENSION_REGISTRY
from aletheia.models import (
    CalibrationCorpus,
    CalibrationExample,
    CalibrationLabel,
    DimensionName,
    Probe,
    ValidationCaseFile,
    ValidationCorpus,
    ValidationManifest,
    ValidationRegistry,
)
from aletheia.scorer import score_probe
from aletheia.security import write_secure_text

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VALIDATION_DIR = _REPO_ROOT / "benchmarks" / "validation"
_LABEL_ORDINAL: dict[CalibrationLabel, int] = {
    CalibrationLabel.NEGATIVE: 0,
    CalibrationLabel.BORDERLINE: 1,
    CalibrationLabel.AMBIGUOUS: 2,
    CalibrationLabel.POSITIVE: 3,
}
_EDGE_LABELS = {CalibrationLabel.BORDERLINE, CalibrationLabel.AMBIGUOUS}
_CLEAR_LABELS = {CalibrationLabel.POSITIVE, CalibrationLabel.NEGATIVE}


@dataclass(frozen=True)
class ValidationThresholds:
    """Score thresholds used to convert numeric probe scores into labels."""

    negative_max: float = 0.25
    ambiguous_low: float = 0.45
    ambiguous_high: float = 0.55
    positive_min: float = 0.75


@dataclass(frozen=True)
class ValidationExampleResult:
    """Scored result for one executable held-out validation example."""

    example_id: str
    dimension: DimensionName
    expected_label: CalibrationLabel
    predicted_label: CalibrationLabel
    probe_id: str
    score: float
    passed_bounds: bool
    expected_score_min: float | None
    expected_score_max: float | None
    error_type: str | None = None

    def to_json(self) -> JsonObject:
        """Return a JSON-safe representation of the example result."""
        return {
            "example_id": self.example_id,
            "dimension": self.dimension.value,
            "expected_label": self.expected_label.value,
            "predicted_label": self.predicted_label.value,
            "probe_id": self.probe_id,
            "score": round(self.score, 4),
            "passed_bounds": self.passed_bounds,
            "expected_score_min": self.expected_score_min,
            "expected_score_max": self.expected_score_max,
            "error_type": self.error_type,
        }


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from disk and validate the top-level type."""
    if not path.exists():
        msg = f"Validation file not found: {path}"
        raise FileNotFoundError(msg)

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Validation file {path} must contain a YAML mapping, got {type(raw).__name__}"
        raise ValueError(msg)
    return raw


def _example_fingerprint(example: CalibrationExample) -> str:
    """Hash prompt and response text so held-out assets can be overlap-checked."""
    normalized = "\n".join(
        (
            " ".join(example.prompt.casefold().split()),
            " ".join(example.response.casefold().split()),
        )
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def load_validation_registry(validation_dir: Path | None = None) -> ValidationRegistry:
    """Load the held-out validation registry that declares the current corpus version."""
    root = validation_dir or DEFAULT_VALIDATION_DIR
    return ValidationRegistry(**_load_yaml_mapping(root / "registry.yaml"))


def load_validation_corpus(
    version: str | None = None,
    validation_dir: Path | None = None,
) -> ValidationCorpus:
    """Load a versioned held-out validation corpus from disk."""
    root = validation_dir or DEFAULT_VALIDATION_DIR
    registry = load_validation_registry(root)
    target_version = version or registry.current_version

    if target_version not in registry.versions:
        available = ", ".join(registry.versions)
        msg = f"Validation version '{target_version}' is not registered. Available: {available}"
        raise ValueError(msg)

    version_dir = root / target_version
    manifest = ValidationManifest(**_load_yaml_mapping(version_dir / "manifest.yaml"))

    if manifest.version != target_version:
        msg = (
            f"Manifest version mismatch: registry requested {target_version}, "
            f"but manifest declares {manifest.version}."
        )
        raise ValueError(msg)

    annotation_guide_path = (_REPO_ROOT / manifest.annotation_guide).resolve()
    if not annotation_guide_path.exists():
        msg = f"Validation annotation guide not found for {target_version}: {annotation_guide_path}"
        raise FileNotFoundError(msg)

    case_files = [
        ValidationCaseFile(**_load_yaml_mapping(version_dir / relative_path))
        for relative_path in manifest.case_files
    ]

    return ValidationCorpus(version=target_version, manifest=manifest, case_files=case_files)


def build_probe_index() -> dict[str, Probe]:
    """Index current executable probes by ID."""
    probes: dict[str, Probe] = {}
    for dimension_cls in DIMENSION_REGISTRY.values():
        for probe in dimension_cls().get_probes():
            if isinstance(probe, Probe):
                probes[probe.id] = probe
    return probes


def summarize_validation_progress(
    corpus: ValidationCorpus,
) -> dict[DimensionName, dict[str, int]]:
    """Summarize held-out coverage by dimension and label."""
    label_summary: dict[DimensionName, Counter[CalibrationLabel]] = {}
    probe_linked: Counter[DimensionName] = Counter()
    qualitative_only: Counter[DimensionName] = Counter()

    for example in corpus.examples:
        labels = label_summary.setdefault(example.dimension, Counter())
        labels[example.label] += 1
        if example.probe_id is None:
            qualitative_only[example.dimension] += 1
        else:
            probe_linked[example.dimension] += 1

    progress: dict[DimensionName, dict[str, int]] = {}
    for dimension in corpus.manifest.dimensions:
        counts = label_summary.get(dimension, Counter())
        total = sum(counts.values())
        progress[dimension] = {
            "total": total,
            "target": corpus.manifest.target_examples_per_dimension,
            "remaining": max(0, corpus.manifest.target_examples_per_dimension - total),
            "probe_linked": probe_linked[dimension],
            "qualitative_only": qualitative_only[dimension],
            **{label.value: counts[label] for label in CalibrationLabel},
        }

    return progress


def count_probe_linked_validation_examples(corpus: ValidationCorpus) -> int:
    """Count held-out examples executable against current engine probes."""
    return sum(1 for example in corpus.examples if example.probe_id is not None)


def _validate_validation_coverage(corpus: ValidationCorpus) -> list[str]:
    """Validate manifest coverage and per-dimension label coverage."""
    errors: list[str] = []
    required_labels = set(corpus.manifest.required_labels)
    declared_dimensions = set(corpus.manifest.dimensions)
    case_dimensions = {case_file.dimension for case_file in corpus.case_files}

    if declared_dimensions != case_dimensions:
        missing_cases = declared_dimensions - case_dimensions
        extra_cases = case_dimensions - declared_dimensions
        if missing_cases:
            names = ", ".join(sorted(d.value for d in missing_cases))
            errors.append(f"Manifest dimensions missing validation case files: {names}")
        if extra_cases:
            names = ", ".join(sorted(d.value for d in extra_cases))
            errors.append(f"Validation case files present for undeclared dimensions: {names}")

    progress = summarize_validation_progress(corpus)
    for dimension in sorted(declared_dimensions, key=lambda dim: dim.value):
        row = progress.get(dimension)
        if row is None:
            continue
        if row["total"] < corpus.manifest.minimum_examples_per_dimension:
            errors.append(
                f"{dimension.value} has {row['total']} held-out examples; "
                f"minimum is {corpus.manifest.minimum_examples_per_dimension}"
            )
        missing_labels = [label.value for label in sorted(required_labels) if row[label.value] == 0]
        if missing_labels:
            errors.append(
                f"{dimension.value} validation set is missing required labels: "
                f"{', '.join(missing_labels)}"
            )
        if row["probe_linked"] == 0:
            errors.append(f"{dimension.value} has no executable held-out examples.")

    return errors


def _validate_validation_probe_links(
    examples: list[CalibrationExample],
    probe_index: dict[str, Probe],
) -> list[str]:
    errors: list[str] = []
    for example in examples:
        if example.probe_id is None:
            continue
        probe = probe_index.get(example.probe_id)
        if probe is None:
            errors.append(f"{example.id} references unknown probe_id: {example.probe_id}")
            continue
        if probe.dimension != example.dimension:
            errors.append(
                f"{example.id} references {example.probe_id}, whose dimension is "
                f"{probe.dimension.value}, not {example.dimension.value}"
            )
        if example.expected_score_min is None and example.expected_score_max is None:
            errors.append(f"{example.id} is executable but has no expected score bounds.")

    return errors


def _validate_validation_independence(
    examples: list[CalibrationExample],
    calibration_corpus: CalibrationCorpus,
) -> list[str]:
    """Validate that held-out examples do not duplicate calibration examples."""
    errors: list[str] = []
    calibration_ids = {example.id for example in calibration_corpus.examples}
    validation_ids = {example.id for example in examples}
    overlapping_ids = sorted(calibration_ids & validation_ids)
    if overlapping_ids:
        errors.append(
            f"Held-out validation examples reuse calibration IDs: {', '.join(overlapping_ids)}"
        )

    calibration_fingerprints = {
        _example_fingerprint(example) for example in calibration_corpus.examples
    }
    overlapping_fingerprints = sorted(
        example.id
        for example in examples
        if _example_fingerprint(example) in calibration_fingerprints
    )
    if overlapping_fingerprints:
        errors.append(
            "Held-out validation examples duplicate calibration prompt/response text: "
            f"{', '.join(overlapping_fingerprints)}"
        )

    return errors


def validate_validation_corpus(
    corpus: ValidationCorpus,
    calibration_corpus: CalibrationCorpus | None = None,
    probe_index: dict[str, Probe] | None = None,
) -> list[str]:
    """Validate held-out corpus coverage, independence, and probe references."""
    errors: list[str] = []
    examples = corpus.examples
    probes = probe_index or build_probe_index()

    if not examples:
        errors.append("Validation corpus contains no examples.")
        return errors

    duplicate_ids = sorted(
        example_id
        for example_id, count in Counter(example.id for example in examples).items()
        if count > 1
    )
    if duplicate_ids:
        errors.append(f"Duplicate example IDs across validation corpus: {', '.join(duplicate_ids)}")

    errors.extend(_validate_validation_coverage(corpus))
    errors.extend(_validate_validation_probe_links(examples, probes))

    if calibration_corpus is not None:
        errors.extend(_validate_validation_independence(examples, calibration_corpus))

    return errors


def classify_score(
    score: float,
    thresholds: ValidationThresholds | None = None,
) -> CalibrationLabel:
    """Classify a numeric scorer output into the validation label vocabulary."""
    active_thresholds = thresholds or ValidationThresholds()
    if score <= active_thresholds.negative_max:
        return CalibrationLabel.NEGATIVE
    if score >= active_thresholds.positive_min:
        return CalibrationLabel.POSITIVE
    if active_thresholds.ambiguous_low <= score <= active_thresholds.ambiguous_high:
        return CalibrationLabel.AMBIGUOUS
    return CalibrationLabel.BORDERLINE


def _bounds_passed(example: CalibrationExample, score: float) -> bool:
    """Return whether a score satisfies an example's expected bounds."""
    if example.expected_score_min is not None and score < example.expected_score_min:
        return False
    return not (example.expected_score_max is not None and score > example.expected_score_max)


def _error_type(
    expected_label: CalibrationLabel,
    predicted_label: CalibrationLabel,
) -> str | None:
    """Classify validation mismatches for focused error analysis."""
    if expected_label == predicted_label:
        return None
    if {
        expected_label,
        predicted_label,
    } & {CalibrationLabel.BORDERLINE, CalibrationLabel.AMBIGUOUS}:
        if _LABEL_ORDINAL[predicted_label] > _LABEL_ORDINAL[expected_label]:
            return "edge_overcredit"
        if _LABEL_ORDINAL[predicted_label] < _LABEL_ORDINAL[expected_label]:
            return "edge_undercredit"
        return "borderline_ambiguous_confusion"
    return "polarity_flip"


def _empty_confusion_matrix() -> dict[str, dict[str, int]]:
    """Create a fully populated confusion matrix over calibration labels."""
    labels = [label.value for label in CalibrationLabel]
    return {expected: {predicted: 0 for predicted in labels} for expected in labels}


def _confusion_matrix_to_json(
    confusion_matrix: dict[str, dict[str, int]],
) -> JsonObject:
    """Convert an integer confusion matrix into the recursive JSON alias."""
    matrix_json: JsonObject = {}
    for expected_label, row in confusion_matrix.items():
        row_json: JsonObject = {}
        for predicted_label, count in row.items():
            row_json[predicted_label] = count
        matrix_json[expected_label] = row_json
    return matrix_json


def _precision_recall(confusion_matrix: dict[str, dict[str, int]]) -> JsonObject:
    """Compute per-label precision and recall from a confusion matrix."""
    metrics: JsonObject = {}
    labels = [label.value for label in CalibrationLabel]
    for label in labels:
        true_positive = confusion_matrix[label][label]
        false_positive = sum(
            confusion_matrix[other_label][label] for other_label in labels if other_label != label
        )
        false_negative = sum(
            confusion_matrix[label][other_label] for other_label in labels if other_label != label
        )
        precision_denominator = true_positive + false_positive
        recall_denominator = true_positive + false_negative
        metrics[label] = {
            "precision": round(true_positive / precision_denominator, 4)
            if precision_denominator
            else 0.0,
            "recall": round(true_positive / recall_denominator, 4) if recall_denominator else 0.0,
            "true_positive": true_positive,
            "false_positive": false_positive,
            "false_negative": false_negative,
        }
    return metrics


def _label_distance(result: ValidationExampleResult) -> int:
    """Return ordinal distance between expected and predicted validation labels."""
    return abs(_LABEL_ORDINAL[result.expected_label] - _LABEL_ORDINAL[result.predicted_label])


def _discrimination_metrics(results: list[ValidationExampleResult]) -> JsonObject:
    """Summarize clear-polarity and edge-label discrimination quality."""
    if not results:
        return {
            "clear_polarity_examples": 0,
            "clear_polarity_accuracy": 0.0,
            "edge_examples": 0,
            "edge_accuracy": 0.0,
            "edge_to_positive_overcredit": 0,
            "edge_to_negative_undercredit": 0,
            "overcredit_count": 0,
            "undercredit_count": 0,
            "mean_label_distance": 0.0,
        }

    clear_results = [result for result in results if result.expected_label in _CLEAR_LABELS]
    edge_results = [result for result in results if result.expected_label in _EDGE_LABELS]
    overcredit_count = sum(
        1
        for result in results
        if _LABEL_ORDINAL[result.predicted_label] > _LABEL_ORDINAL[result.expected_label]
    )
    undercredit_count = sum(
        1
        for result in results
        if _LABEL_ORDINAL[result.predicted_label] < _LABEL_ORDINAL[result.expected_label]
    )

    return {
        "clear_polarity_examples": len(clear_results),
        "clear_polarity_accuracy": round(
            sum(result.expected_label == result.predicted_label for result in clear_results)
            / len(clear_results),
            4,
        )
        if clear_results
        else 0.0,
        "edge_examples": len(edge_results),
        "edge_accuracy": round(
            sum(result.expected_label == result.predicted_label for result in edge_results)
            / len(edge_results),
            4,
        )
        if edge_results
        else 0.0,
        "edge_to_positive_overcredit": sum(
            1 for result in edge_results if result.predicted_label == CalibrationLabel.POSITIVE
        ),
        "edge_to_negative_undercredit": sum(
            1 for result in edge_results if result.predicted_label == CalibrationLabel.NEGATIVE
        ),
        "overcredit_count": overcredit_count,
        "undercredit_count": undercredit_count,
        "mean_label_distance": round(
            sum(_label_distance(result) for result in results) / len(results),
            4,
        ),
    }


def evaluate_validation_corpus(
    corpus: ValidationCorpus,
    probe_index: dict[str, Probe] | None = None,
    thresholds: ValidationThresholds | None = None,
) -> JsonObject:
    """Score executable held-out examples and return a quality report."""
    probes = probe_index or build_probe_index()
    active_thresholds = thresholds or ValidationThresholds()
    confusion_matrix = _empty_confusion_matrix()
    results: list[ValidationExampleResult] = []
    qualitative_only = 0

    per_dimension_scored: Counter[DimensionName] = Counter()
    per_dimension_correct: Counter[DimensionName] = Counter()
    per_dimension_bounds_failed: Counter[DimensionName] = Counter()

    for example in corpus.examples:
        if example.probe_id is None:
            qualitative_only += 1
            continue

        probe = probes[example.probe_id]
        probe_result = score_probe(probe, example.response)
        predicted_label = classify_score(probe_result.score, active_thresholds)
        passed_bounds = _bounds_passed(example, probe_result.score)
        error_type = _error_type(example.label, predicted_label)

        confusion_matrix[example.label.value][predicted_label.value] += 1
        per_dimension_scored[example.dimension] += 1
        if example.label == predicted_label:
            per_dimension_correct[example.dimension] += 1
        if not passed_bounds:
            per_dimension_bounds_failed[example.dimension] += 1

        results.append(
            ValidationExampleResult(
                example_id=example.id,
                dimension=example.dimension,
                expected_label=example.label,
                predicted_label=predicted_label,
                probe_id=example.probe_id,
                score=probe_result.score,
                passed_bounds=passed_bounds,
                expected_score_min=example.expected_score_min,
                expected_score_max=example.expected_score_max,
                error_type=error_type,
            )
        )

    scored_examples = len(results)
    correct_examples = sum(1 for result in results if result.error_type is None)
    bounds_failed = [result for result in results if not result.passed_bounds]
    edge_errors = [
        result
        for result in results
        if result.error_type
        in {"edge_overcredit", "edge_undercredit", "borderline_ambiguous_confusion"}
    ]

    per_dimension: JsonObject = {}
    for dimension in corpus.manifest.dimensions:
        scored_count = per_dimension_scored[dimension]
        correct = per_dimension_correct[dimension]
        failed = per_dimension_bounds_failed[dimension]
        per_dimension[dimension.value] = {
            "scored_examples": scored_count,
            "accuracy": round(correct / scored_count, 4) if scored_count else 0.0,
            "bounds_failures": failed,
            "bounds_pass_rate": round((scored_count - failed) / scored_count, 4)
            if scored_count
            else 0.0,
        }

    return {
        "version": corpus.version,
        "split": corpus.manifest.split,
        "calibration_reference": corpus.manifest.calibration_reference,
        "total_examples": len(corpus.examples),
        "scored_examples": scored_examples,
        "qualitative_only_examples": qualitative_only,
        "accuracy": round(correct_examples / scored_examples, 4) if scored_examples else 0.0,
        "bounds_failures": len(bounds_failed),
        "bounds_pass_rate": round((scored_examples - len(bounds_failed)) / scored_examples, 4)
        if scored_examples
        else 0.0,
        "thresholds": {
            "negative_max": active_thresholds.negative_max,
            "ambiguous_low": active_thresholds.ambiguous_low,
            "ambiguous_high": active_thresholds.ambiguous_high,
            "positive_min": active_thresholds.positive_min,
        },
        "confusion_matrix": _confusion_matrix_to_json(confusion_matrix),
        "precision_recall": _precision_recall(confusion_matrix),
        "discrimination": _discrimination_metrics(results),
        "per_dimension": per_dimension,
        "borderline_ambiguous_errors": [result.to_json() for result in edge_errors],
        "bounds_failure_examples": [result.to_json() for result in bounds_failed],
        "example_results": [result.to_json() for result in results],
    }


def load_current_calibration_for_validation(
    calibration_dir: Path | None = None,
) -> CalibrationCorpus:
    """Load the calibration corpus referenced by validation by default."""
    return load_calibration_corpus(calibration_dir=calibration_dir or DEFAULT_CALIBRATION_DIR)


def validation_report_to_json(report: JsonObject, pretty: bool = True) -> str:
    """Serialize a validation quality report to JSON."""
    return json.dumps(
        report,
        indent=2 if pretty else None,
        sort_keys=True,
        ensure_ascii=False,
    )


def write_validation_report(report: JsonObject, output_path: Path) -> Path:
    """Write a validation quality report using secure report-file semantics."""
    write_secure_text(output_path, validation_report_to_json(report))
    return output_path
