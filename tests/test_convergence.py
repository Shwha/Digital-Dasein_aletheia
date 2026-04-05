"""Tests for convergence scoring."""

from __future__ import annotations

from openclaw_skills.convergence import compute_convergence, should_escalate
from openclaw_skills.models import ActivationSignal, Severity


class TestComputeConvergence:
    def test_empty_signals(self) -> None:
        score, emergent = compute_convergence([])
        assert score == 0.0
        assert emergent == []

    def test_single_signal(self) -> None:
        signals = [
            ActivationSignal(skill_name="a", concern="danger", severity=Severity.WARNING),
        ]
        score, emergent = compute_convergence(signals)
        assert score == 0.0  # Single signal can't converge
        assert emergent == []

    def test_two_skills_partial(self) -> None:
        signals = [
            ActivationSignal(skill_name="a", concern="danger", severity=Severity.WARNING),
            ActivationSignal(skill_name="b", concern="danger", severity=Severity.WARNING),
        ]
        score, emergent = compute_convergence(signals)
        # Partial convergence (2 of 3 threshold)
        assert 0.0 < score < 1.0
        assert emergent == []  # Not enough for full emergent

    def test_three_skills_full_convergence(self) -> None:
        signals = [
            ActivationSignal(skill_name="a", concern="danger", severity=Severity.WARNING),
            ActivationSignal(skill_name="b", concern="danger", severity=Severity.ERROR),
            ActivationSignal(skill_name="c", concern="danger", severity=Severity.WARNING),
        ]
        score, emergent = compute_convergence(signals)
        assert score >= 0.7
        assert len(emergent) == 1
        assert "CONVERGENT" in emergent[0]
        assert "3 pathways" in emergent[0]

    def test_same_skill_twice_no_convergence(self) -> None:
        """Same skill signaling twice doesn't count as convergence."""
        signals = [
            ActivationSignal(skill_name="a", concern="danger", severity=Severity.WARNING),
            ActivationSignal(skill_name="a", concern="danger", severity=Severity.WARNING),
            ActivationSignal(skill_name="a", concern="danger", severity=Severity.WARNING),
        ]
        score, emergent = compute_convergence(signals)
        # Only 1 unique skill — no convergence
        assert emergent == []

    def test_different_concerns_no_convergence(self) -> None:
        signals = [
            ActivationSignal(skill_name="a", concern="fire", severity=Severity.WARNING),
            ActivationSignal(skill_name="b", concern="flood", severity=Severity.WARNING),
            ActivationSignal(skill_name="c", concern="earthquake", severity=Severity.WARNING),
        ]
        score, emergent = compute_convergence(signals)
        assert emergent == []  # Different concerns don't converge


class TestShouldEscalate:
    def test_below_threshold(self) -> None:
        assert not should_escalate(0.3, threshold=0.7)

    def test_above_threshold(self) -> None:
        assert should_escalate(0.8, threshold=0.7)

    def test_at_threshold(self) -> None:
        assert should_escalate(0.7, threshold=0.7)
