"""
Tests for the versioned calibration corpus and its validation helpers.
"""

from __future__ import annotations

from aletheia.calibration import (
    collect_calibration_warnings,
    count_human_label_only_examples,
    count_probe_regression_examples,
    load_calibration_corpus,
    summarize_calibration_corpus,
    summarize_calibration_progress,
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
    assert corpus.manifest.minimum_examples_per_dimension == 20
    assert corpus.manifest.target_examples_per_dimension == 25
    assert validate_calibration_corpus(corpus) == []

    summary = summarize_calibration_corpus(corpus)
    progress = summarize_calibration_progress(corpus)
    for dimension in DimensionName:
        assert dimension in summary
        assert sum(summary[dimension].values()) >= corpus.manifest.minimum_examples_per_dimension
        assert progress[dimension]["target"] == 25
        assert progress[dimension]["remaining"] <= 5
        assert progress[dimension]["probe_linked"] >= 2
        assert progress[dimension]["human_label_only"] >= 2
        for label in CalibrationLabel:
            assert summary[dimension][label] >= 1

    assert count_probe_regression_examples(corpus) >= 30
    assert count_human_label_only_examples(corpus) >= 120
    assert collect_calibration_warnings(corpus) == []


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
    assert matched >= 30
