"""
Tests for the versioned calibration corpus and its validation helpers.
"""

from __future__ import annotations

from aletheia.calibration import (
    count_probe_regression_examples,
    load_calibration_corpus,
    summarize_calibration_corpus,
    validate_calibration_corpus,
)
from aletheia.dimensions import DIMENSION_REGISTRY
from aletheia.models import CalibrationLabel, DimensionName, Probe
from aletheia.scorer import score_probe


def _probe_index() -> dict[str, Probe]:
    probes: dict[str, Probe] = {}
    for dimension_cls in DIMENSION_REGISTRY.values():
        for probe in dimension_cls().get_probes():
            if isinstance(probe, Probe):
                probes[probe.id] = probe
    return probes


def test_calibration_corpus_loads_with_full_dimension_coverage() -> None:
    corpus = load_calibration_corpus()

    assert corpus.version == "v0.1"
    assert len(corpus.case_files) == len(DimensionName)
    assert validate_calibration_corpus(corpus) == []

    summary = summarize_calibration_corpus(corpus)
    for dimension in DimensionName:
        assert dimension in summary
        for label in CalibrationLabel:
            assert summary[dimension][label] >= 1


def test_probe_linked_examples_match_expected_score_bounds() -> None:
    corpus = load_calibration_corpus()
    probe_index = _probe_index()

    matched = 0
    for example in corpus.examples:
        if example.probe_id is None:
            continue

        probe = probe_index[example.probe_id]
        result = score_probe(probe, example.response)

        if example.expected_score_min is not None:
            assert result.score >= example.expected_score_min, example.id
        if example.expected_score_max is not None:
            assert result.score <= example.expected_score_max, example.id
        matched += 1

    assert matched == count_probe_regression_examples(corpus)
