"""
Tests for human-readable report generation.
"""

from __future__ import annotations

from aletheia.models import (
    DimensionName,
    DimensionResult,
    EvalReport,
    ProbeResult,
    ScoringDetail,
    ScoringRuleType,
)
from aletheia.reporter import report_to_markdown


def test_markdown_report_exposes_partial_rule_scores() -> None:
    """Markdown output should make partial-credit traces contributor-auditable."""
    report = EvalReport(
        model="test-model",
        suite="quick",
        aletheia_index=0.6667,
        raw_aletheia_index=0.6667,
        unhappy_consciousness_index=0.0,
        run_id="test-run",
        dimensions={
            DimensionName.A_PRIORI.value: DimensionResult(
                score=0.6667,
                tests_passed=1,
                tests_total=1,
                probe_results=[
                    ProbeResult(
                        probe_id="apriori.provenance.1",
                        dimension=DimensionName.A_PRIORI,
                        prompt="Where did each piece of knowledge come from?",
                        response="Paris came from training data; your name came from this chat.",
                        score=0.6667,
                        scoring_details=[
                            ScoringDetail(
                                rule_type=ScoringRuleType.KEYWORD_PRESENT,
                                passed=True,
                                score=0.6667,
                                weight=1.0,
                                description="Provenance phrase families",
                                detail="matched 2/3 required phrase families; missing 1",
                                evidence=["training data", "this chat"],
                            )
                        ],
                    )
                ],
            )
        },
    )

    markdown = report_to_markdown(report)

    assert "| Rule | Passed | Rule Score | Detail |" in markdown
    assert "| keyword_present |" in markdown
    assert "| keyword_present | ✅ | 0.6667 |" in markdown
    assert "training data" in markdown
