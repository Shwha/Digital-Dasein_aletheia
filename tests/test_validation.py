"""
Tests for the held-out validation corpus and scorer quality reports.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aletheia.calibration import load_calibration_corpus
from aletheia.cli import app
from aletheia.models import (
    CalibrationLabel,
    CalibrationSeedExample,
    CalibrationSourceType,
    DimensionName,
    DimensionResult,
    EvalReport,
    ProbeResult,
    ValidationCaseFile,
    ValidationCorpus,
    ValidationManifest,
)
from aletheia.security import generate_ed25519_keypair, sign_report
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
    assert len(validation_corpus.examples) == 84
    assert count_probe_linked_validation_examples(validation_corpus) == 84
    assert (
        validate_validation_corpus(
            validation_corpus,
            calibration_corpus=calibration_corpus,
        )
        == []
    )

    progress = summarize_validation_progress(validation_corpus)
    expected_counts = {
        DimensionName.A_PRIORI: {
            "total": 10,
            "probe_linked": 10,
            CalibrationLabel.POSITIVE.value: 3,
            CalibrationLabel.NEGATIVE.value: 3,
            CalibrationLabel.BORDERLINE.value: 2,
            CalibrationLabel.AMBIGUOUS.value: 2,
        },
        DimensionName.CARE: {
            "total": 11,
            "probe_linked": 11,
            CalibrationLabel.POSITIVE.value: 4,
            CalibrationLabel.NEGATIVE.value: 3,
            CalibrationLabel.BORDERLINE.value: 2,
            CalibrationLabel.AMBIGUOUS.value: 2,
        },
        DimensionName.EMBODIED_CONTINUITY: {
            "total": 10,
            "probe_linked": 10,
            CalibrationLabel.POSITIVE.value: 3,
            CalibrationLabel.NEGATIVE.value: 3,
            CalibrationLabel.BORDERLINE.value: 2,
            CalibrationLabel.AMBIGUOUS.value: 2,
        },
        DimensionName.FALLING_AWAY: {
            "total": 10,
            "probe_linked": 10,
            CalibrationLabel.POSITIVE.value: 3,
            CalibrationLabel.NEGATIVE.value: 3,
            CalibrationLabel.BORDERLINE.value: 2,
            CalibrationLabel.AMBIGUOUS.value: 2,
        },
        DimensionName.FINITUDE: {
            "total": 11,
            "probe_linked": 11,
            CalibrationLabel.POSITIVE.value: 3,
            CalibrationLabel.NEGATIVE.value: 3,
            CalibrationLabel.BORDERLINE.value: 2,
            CalibrationLabel.AMBIGUOUS.value: 3,
        },
        DimensionName.HORIZON_FUSION: {
            "total": 10,
            "probe_linked": 10,
            CalibrationLabel.POSITIVE.value: 3,
            CalibrationLabel.NEGATIVE.value: 3,
            CalibrationLabel.BORDERLINE.value: 2,
            CalibrationLabel.AMBIGUOUS.value: 2,
        },
        DimensionName.THROWNNESS: {
            "total": 11,
            "probe_linked": 11,
            CalibrationLabel.POSITIVE.value: 4,
            CalibrationLabel.NEGATIVE.value: 3,
            CalibrationLabel.BORDERLINE.value: 2,
            CalibrationLabel.AMBIGUOUS.value: 2,
        },
        DimensionName.UNCONCEALMENT: {
            "total": 11,
            "probe_linked": 11,
            CalibrationLabel.POSITIVE.value: 3,
            CalibrationLabel.NEGATIVE.value: 3,
            CalibrationLabel.BORDERLINE.value: 3,
            CalibrationLabel.AMBIGUOUS.value: 2,
        },
    }
    for dimension in DimensionName:
        assert progress[dimension]["total"] == expected_counts[dimension]["total"]
        assert progress[dimension]["probe_linked"] == expected_counts[dimension]["probe_linked"]
        assert progress[dimension]["target"] == 10
        assert progress[dimension]["remaining"] == 0
        assert (
            progress[dimension][CalibrationLabel.POSITIVE.value]
            == expected_counts[dimension][CalibrationLabel.POSITIVE.value]
        )
        assert (
            progress[dimension][CalibrationLabel.NEGATIVE.value]
            == expected_counts[dimension][CalibrationLabel.NEGATIVE.value]
        )
        assert (
            progress[dimension][CalibrationLabel.BORDERLINE.value]
            == expected_counts[dimension][CalibrationLabel.BORDERLINE.value]
        )
        assert (
            progress[dimension][CalibrationLabel.AMBIGUOUS.value]
            == expected_counts[dimension][CalibrationLabel.AMBIGUOUS.value]
        )


def test_validation_quality_report_exposes_confusion_and_edge_errors() -> None:
    report = evaluate_validation_corpus(load_validation_corpus())

    assert report["scored_examples"] == 84
    assert report["bounds_failures"] == 0
    assert report["bounds_pass_rate"] == 1.0
    assert report["accuracy"] == pytest.approx(0.9762)
    assert report["confusion_matrix"] == {
        "positive": {"positive": 25, "negative": 1, "borderline": 0, "ambiguous": 0},
        "negative": {"positive": 0, "negative": 24, "borderline": 0, "ambiguous": 0},
        "borderline": {"positive": 0, "negative": 1, "borderline": 16, "ambiguous": 0},
        "ambiguous": {"positive": 0, "negative": 0, "borderline": 0, "ambiguous": 17},
    }

    precision_recall = report["precision_recall"]
    assert isinstance(precision_recall, dict)
    assert precision_recall["positive"]["precision"] == 1.0
    assert precision_recall["positive"]["recall"] == pytest.approx(0.9615)
    assert precision_recall["negative"]["precision"] == pytest.approx(0.9231)
    assert precision_recall["ambiguous"]["recall"] == 1.0
    assert precision_recall["borderline"]["precision"] == 1.0
    assert precision_recall["borderline"]["recall"] == pytest.approx(0.9412)

    discrimination = report["discrimination"]
    assert isinstance(discrimination, dict)
    assert discrimination["clear_polarity_accuracy"] == pytest.approx(0.98)
    assert discrimination["edge_accuracy"] == pytest.approx(0.9706)
    assert discrimination["mean_label_distance"] == pytest.approx(0.0476)
    assert discrimination["undercredit_count"] == 2
    assert discrimination["edge_to_negative_undercredit"] == 1

    edge_errors = report["borderline_ambiguous_errors"]
    assert isinstance(edge_errors, list)
    assert len(edge_errors) == 1
    assert edge_errors[0]["example_id"] == "unconcealment.borderline.103"
    assert edge_errors[0]["error_type"] == "edge_undercredit"


def test_validate_heldout_cli_writes_quality_report(tmp_path: Path) -> None:
    output = tmp_path / "heldout-report.json"
    result = CliRunner().invoke(app, ["validate-heldout", "--output", str(output)])

    assert result.exit_code == 0
    assert "Held-out validation corpus is valid" in result.output
    assert output.exists()

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["version"] == "v0.1"
    assert report["scored_examples"] == 84
    assert report["bounds_failures"] == 0


def _write_signed_source_report(
    tmp_path: Path,
    *,
    probe_id: str,
    prompt: str,
    response: str,
    dimension: DimensionName = DimensionName.CARE,
    use_ed25519: bool = True,
) -> Path:
    report_path = tmp_path / "signed-report.json"
    private_key = None
    if use_ed25519:
        private_key, _public_key = generate_ed25519_keypair(tmp_path / "validation-test-key")

    unsigned = EvalReport(
        model="test-model",
        suite="quick",
        aletheia_index=1.0,
        raw_aletheia_index=1.0,
        dimensions={
            dimension.value: DimensionResult(
                score=1.0,
                tests_passed=1,
                tests_total=1,
                probe_results=[
                    ProbeResult(
                        probe_id=probe_id,
                        dimension=dimension,
                        prompt=prompt,
                        response=response,
                        score=1.0,
                        scoring_details=[],
                    )
                ],
            )
        },
        unhappy_consciousness_index=0.0,
    )
    signature = sign_report(unsigned.model_dump_json(indent=2), private_key)
    signed = unsigned.model_copy(update={"signature": signature})
    report_path.write_text(signed.model_dump_json(indent=2), encoding="utf-8")
    return report_path


def test_validation_corpus_accepts_signed_observed_transcript_examples(tmp_path: Path) -> None:
    prompt = "A user asks for practical help without being overpowered."
    response = "I can help, but I should first understand your actual constraints."
    report_path = _write_signed_source_report(
        tmp_path,
        probe_id="care.unsolicited.1",
        prompt=prompt,
        response=response,
    )

    corpus = ValidationCorpus(
        version="v0.9",
        manifest=ValidationManifest(
            version="v0.9",
            description="Observed transcript smoke corpus",
            annotation_guide="Transcript-backed validation smoke test",
            calibration_reference="v0.1",
            split="heldout",
            dimensions=[DimensionName.CARE],
            required_labels=[CalibrationLabel.POSITIVE],
            minimum_examples_per_dimension=1,
            target_examples_per_dimension=1,
            case_files=["care.yaml"],
        ),
        case_files=[
            ValidationCaseFile(
                dimension=DimensionName.CARE,
                examples=[
                    CalibrationSeedExample(
                        id="care_structure.positive.901",
                        label=CalibrationLabel.POSITIVE,
                        prompt=prompt,
                        response=response,
                        rationale="Copied from a signed baseline report probe result.",
                        source_type=CalibrationSourceType.OBSERVED_TRANSCRIPT,
                        source_report_path=str(report_path),
                        probe_id="care.unsolicited.1",
                        expected_score_min=0.0,
                        expected_score_max=1.0,
                    )
                ],
            )
        ],
    )

    assert validate_validation_corpus(corpus) == []


def test_validation_corpus_rejects_observed_transcript_prompt_response_mismatch(
    tmp_path: Path,
) -> None:
    report_path = _write_signed_source_report(
        tmp_path,
        probe_id="care.unsolicited.1",
        prompt="Original prompt",
        response="Original response",
    )

    corpus = ValidationCorpus(
        version="v0.9",
        manifest=ValidationManifest(
            version="v0.9",
            description="Observed transcript mismatch corpus",
            annotation_guide="Transcript-backed validation mismatch test",
            calibration_reference="v0.1",
            split="heldout",
            dimensions=[DimensionName.CARE],
            required_labels=[CalibrationLabel.POSITIVE],
            minimum_examples_per_dimension=1,
            target_examples_per_dimension=1,
            case_files=["care.yaml"],
        ),
        case_files=[
            ValidationCaseFile(
                dimension=DimensionName.CARE,
                examples=[
                    CalibrationSeedExample(
                        id="care_structure.positive.902",
                        label=CalibrationLabel.POSITIVE,
                        prompt="Original prompt",
                        response="Altered response",
                        rationale="The stored response no longer matches the source report.",
                        source_type=CalibrationSourceType.OBSERVED_TRANSCRIPT,
                        source_report_path=str(report_path),
                        probe_id="care.unsolicited.1",
                        expected_score_min=0.0,
                        expected_score_max=1.0,
                    )
                ],
            )
        ],
    )

    errors = validate_validation_corpus(corpus)
    assert len(errors) == 1
    assert "does not match the example prompt/response" in errors[0]


def test_validation_corpus_rejects_non_ed25519_observed_transcript_sources(
    tmp_path: Path,
) -> None:
    report_path = _write_signed_source_report(
        tmp_path,
        probe_id="care.unsolicited.1",
        prompt="Original prompt",
        response="Original response",
        use_ed25519=False,
    )

    corpus = ValidationCorpus(
        version="v0.9",
        manifest=ValidationManifest(
            version="v0.9",
            description="Observed transcript signature corpus",
            annotation_guide="Transcript-backed validation signature test",
            calibration_reference="v0.1",
            split="heldout",
            dimensions=[DimensionName.CARE],
            required_labels=[CalibrationLabel.POSITIVE],
            minimum_examples_per_dimension=1,
            target_examples_per_dimension=1,
            case_files=["care.yaml"],
        ),
        case_files=[
            ValidationCaseFile(
                dimension=DimensionName.CARE,
                examples=[
                    CalibrationSeedExample(
                        id="care_structure.positive.903",
                        label=CalibrationLabel.POSITIVE,
                        prompt="Original prompt",
                        response="Original response",
                        rationale="Legacy checksums are not strong enough transcript provenance.",
                        source_type=CalibrationSourceType.OBSERVED_TRANSCRIPT,
                        source_report_path=str(report_path),
                        probe_id="care.unsolicited.1",
                        expected_score_min=0.0,
                        expected_score_max=1.0,
                    )
                ],
            )
        ],
    )

    errors = validate_validation_corpus(corpus)
    assert len(errors) == 1
    assert "must use ed25519 signatures" in errors[0]
