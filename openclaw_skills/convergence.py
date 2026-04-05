"""Convergence scoring — emergent insight from multi-pathway activation.

When multiple independent skills flag the same concern simultaneously,
that's convergence. Like biological ETC where the proton gradient
stores potential energy, convergence stores escalation energy.

The key insight: emergent escalation is stronger than any single signal.
Three independent warnings about the same thing = one critical alert.
This is NOT hardcoded — it's topological, arising from the structure
of activation, not from explicit rules.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from openclaw_skills.logging import get_logger
from openclaw_skills.models import ActivationSignal, Severity

logger = get_logger(__name__)

# When this many independent pathways converge on the same concern,
# the combined severity escalates regardless of individual severities.
CONVERGENCE_THRESHOLD = 3

# Severity escalation ladder
_SEVERITY_ORDER: dict[Severity, int] = {
    Severity.INFO: 0,
    Severity.WARNING: 1,
    Severity.ERROR: 2,
    Severity.CRITICAL: 3,
}


def compute_convergence(
    signals: list[ActivationSignal],
) -> tuple[float, list[str]]:
    """Compute convergence score from activation signals.

    Groups signals by concern keyword, computes weighted convergence,
    and identifies emergent escalations.

    Args:
        signals: All activation signals from the current pipeline run.

    Returns:
        Tuple of (convergence_score, list of emergent concern descriptions).
        Score is 0.0 (no convergence) to 1.0 (maximum convergence).
    """
    if not signals:
        return 0.0, []

    # Group signals by normalized concern
    concern_groups: defaultdict[str, list[ActivationSignal]] = defaultdict(list)
    for signal in signals:
        key = _normalize_concern(signal.concern)
        concern_groups[key].append(signal)

    # Compute per-concern convergence
    emergent_concerns: list[str] = []
    max_convergence = 0.0

    for concern, group in concern_groups.items():
        # Count unique skills contributing to this concern
        unique_skills = {s.skill_name for s in group}
        pathway_count = len(unique_skills)

        if pathway_count >= CONVERGENCE_THRESHOLD:
            # Emergent escalation — multiple independent pathways converged
            total_weight = sum(s.weight for s in group)
            max_severity = max(
                (_SEVERITY_ORDER.get(s.severity, 0) for s in group),
                default=0,
            )
            convergence = min(1.0, total_weight / CONVERGENCE_THRESHOLD)

            emergent_concerns.append(
                f"CONVERGENT [{pathway_count} pathways]: {concern} "
                f"(skills: {', '.join(sorted(unique_skills))})"
            )

            logger.warning(
                "convergence_detected",
                concern=concern,
                pathways=pathway_count,
                skills=sorted(unique_skills),
                convergence=convergence,
            )

            max_convergence = max(max_convergence, convergence)

        elif pathway_count >= 2:
            # Partial convergence — note but don't escalate
            total_weight = sum(s.weight for s in group)
            convergence = total_weight / CONVERGENCE_THRESHOLD
            max_convergence = max(max_convergence, min(0.6, convergence))

    return max_convergence, emergent_concerns


def _normalize_concern(concern: str) -> str:
    """Normalize a concern string for grouping.

    Concerns from different skills may describe the same issue
    with different words. This does basic normalization.
    More sophisticated NLP-based matching could be added later.
    """
    return concern.lower().strip()


def should_escalate(convergence_score: float, threshold: float = 0.7) -> bool:
    """Determine if convergence warrants escalation to user.

    Args:
        convergence_score: Output of compute_convergence().
        threshold: Minimum score to trigger escalation.

    Returns:
        True if convergence exceeds threshold.
    """
    return convergence_score >= threshold
