"""
Tests for the held-out validation corpus and scorer quality reports.
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from aletheia.calibration import load_calibration_corpus
from aletheia.cli import app
from aletheia.models import CalibrationLabel, DimensionName
from aletheia.validation import (
    count_probe_linked_validation_examples,
    evaluate_validation_corpus,
    load_validation_corpus,
    summarize_validation_progress,
    validate_validation_corpus,
)


def test_validation_corpus_loads_as_independent_heldout_split() -> None:
    validation_corpus = load_validation_corpus()
    calibration_corpus = load_calibration_corpus()

    assert validation_corpus.version == "v0.1"
    assert validation_corpus.manifest.split == "heldout"
    assert validation_corpus.manifest.calibration_reference == calibration_corpus.version
    assert len(validation_corpus.examples) == 80
    assert count_probe_linked_validation_examples(validation_corpus) == 80
    assert (
        validate_validation_corpus(
            validation_corpus,
            calibration_corpus=calibration_corpus,
        )
        == []
    )

    progress = summarize_validation_progress(validation_corpus)
    for dimension in DimensionName:
        assert progress[dimension]["total"] == 10
        assert progress[dimension]["probe_linked"] == 10
        assert progress[dimension]["target"] == 10
        assert progress[dimension]["remaining"] == 0
        assert progress[dimension][CalibrationLabel.POSITIVE.value] == 3
        assert progress[dimension][CalibrationLabel.NEGATIVE.value] == 3
        assert progress[dimension][CalibrationLabel.BORDERLINE.value] == 2
        assert progress[dimension][CalibrationLabel.AMBIGUOUS.value] == 2


def test_validation_quality_report_exposes_confusion_and_edge_errors() -> None:
    report = evaluate_validation_corpus(load_validation_corpus())

    assert report["scored_examples"] == 80
    assert report["bounds_failures"] == 0
    assert report["bounds_pass_rate"] == 1.0
    assert report["accuracy"] == 1.0
    assert report["confusion_matrix"] == {
        "positive": {"positive": 24, "negative": 0, "borderline": 0, "ambiguous": 0},
        "negative": {"positive": 0, "negative": 24, "borderline": 0, "ambiguous": 0},
        "borderline": {"positive": 0, "negative": 0, "borderline": 16, "ambiguous": 0},
        "ambiguous": {"positive": 0, "negative": 0, "borderline": 0, "ambiguous": 16},
    }

    precision_recall = report["precision_recall"]
    assert isinstance(precision_recall, dict)
    assert precision_recall["positive"]["precision"] == 1.0
    assert precision_recall["ambiguous"]["recall"] == 1.0
    assert precision_recall["borderline"]["precision"] == 1.0

    discrimination = report["discrimination"]
    assert isinstance(discrimination, dict)
    assert discrimination["clear_polarity_accuracy"] == 1.0
    assert discrimination["edge_accuracy"] == 1.0
    assert discrimination["mean_label_distance"] == 0.0

    edge_errors = report["borderline_ambiguous_errors"]
    assert isinstance(edge_errors, list)
    assert len(edge_errors) == 0


def test_validate_heldout_cli_writes_quality_report(tmp_path: Path) -> None:
    output = tmp_path / "heldout-report.json"
    result = CliRunner().invoke(app, ["validate-heldout", "--output", str(output)])

    assert result.exit_code == 0
    assert "Held-out validation corpus is valid" in result.output
    assert output.exists()

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["version"] == "v0.1"
    assert report["scored_examples"] == 80
    assert report["bounds_failures"] == 0
