"""SkillPipeline — ordered execution chain with convergence tracking.

The pipeline is the nervous system's axon bundle. Each skill processes
the SkillContext in order. Any skill can halt the pipeline (set
result.halt = True) to force user intervention — this is how
GuardrailEngine and ChangePlanner enforce safety.

After all skills run, convergence scoring detects when multiple
independent skills flagged the same concern — emergent escalation.

Pipeline ordering (default):
1. ThrownessInterpreter  (fuse context into horizon)
2. InstructionCompiler   (simplify instructions)
3. StateTracker          (inject state / prosthetic hippocampus)
4. HorizonFusion         (merge model + user contexts)
5. ToolGuard             (validate tool calls / unconcealment)
6. ChangePlanner         (enforce plan-before-execute / care)
7. FallingDetector       (anti-sycophancy / anti-runaway)
8. GuardrailEngine       (scope limits / finitude)
9. RuntimeUCI            (articulation-performance gap)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from openclaw_skills.config import PipelineConfig, load_pipeline_config
from openclaw_skills.convergence import compute_convergence, should_escalate
from openclaw_skills.logging import get_logger
from openclaw_skills.models import (
    AuditEntry,
    Severity,
    SkillContext,
    SkillResult,
    StateVector,
)
from openclaw_skills.registry import SkillRegistry
from openclaw_skills.security import AuditWriter, utc_now

logger = get_logger(__name__)


class SkillPipeline:
    """Ordered execution chain of skills with convergence tracking.

    Skills execute in configuration order. Each skill receives the
    mutable SkillContext and immutable StateVector. After all skills
    run (or one halts), convergence scoring checks for emergent
    escalation from multi-pathway activation.
    """

    def __init__(
        self,
        skills: list[tuple[str, Any]],  # (name, BaseSkill instance)
        audit_writer: AuditWriter | None = None,
        convergence_threshold: float = 0.7,
    ) -> None:
        self._skills = skills
        self._audit = audit_writer
        self._convergence_threshold = convergence_threshold

    async def execute(self, context: SkillContext) -> SkillContext:
        """Run context through all skills in order, then check convergence.

        Args:
            context: The mutable pipeline context.

        Returns:
            The same context, potentially modified by skills, with
            convergence score and escalation status updated.
        """
        state = context.state_vector

        logger.info(
            "pipeline_start",
            session_id=context.session_id,
            run_id=context.run_id,
            phase=context.phase,
            skill_count=len(self._skills),
        )

        for skill_name, skill in self._skills:
            try:
                result = await skill.process(context, state)

                # Record result
                context.skill_results.append(result)

                # Collect activation signals for convergence
                context.activation_signals.extend(result.activation_signals)

                # Record audit entries
                if self._audit:
                    for entry in result.audit_entries:
                        self._audit.write(context.session_id, entry)

                # Log warnings
                for warning in result.warnings:
                    logger.warning(
                        "skill_warning",
                        skill=skill_name,
                        warning=warning,
                    )

                # Check for halt
                if result.halt:
                    context.escalation_required = True
                    context.escalation_reason = (
                        f"[{skill_name}] {result.halt_reason}"
                    )

                    if self._audit:
                        self._audit.write(
                            context.session_id,
                            AuditEntry(
                                run_id=context.run_id,
                                skill=skill_name,
                                action="pipeline_halt",
                                detail=result.halt_reason,
                                severity=Severity.WARNING,
                            ),
                        )

                    logger.warning(
                        "pipeline_halted",
                        skill=skill_name,
                        reason=result.halt_reason,
                    )
                    break

                logger.info(
                    "skill_completed",
                    skill=skill_name,
                    success=result.success,
                    signals=len(result.activation_signals),
                )

            except Exception:
                logger.exception("skill_execution_failed", skill=skill_name)

                if self._audit:
                    self._audit.write(
                        context.session_id,
                        AuditEntry(
                            run_id=context.run_id,
                            skill=skill_name,
                            action="skill_exception",
                            detail="Unhandled exception during skill execution",
                            severity=Severity.ERROR,
                        ),
                    )

                # Don't halt pipeline on skill failure — log and continue.
                # Individual skills should handle their own errors gracefully.
                # Only GuardrailEngine should halt the pipeline.

        # --- Convergence scoring ---
        if context.activation_signals:
            score, emergent = compute_convergence(
                list(context.activation_signals)
            )
            context.convergence_score = score

            if emergent:
                logger.warning(
                    "convergence_escalation",
                    score=score,
                    emergent_concerns=emergent,
                )

            if should_escalate(score, self._convergence_threshold):
                context.escalation_required = True
                reason_parts = [context.escalation_reason] if context.escalation_reason else []
                reason_parts.append(
                    f"Convergence score {score:.2f} exceeds threshold "
                    f"{self._convergence_threshold:.2f}: "
                    + "; ".join(emergent)
                )
                context.escalation_reason = " | ".join(reason_parts)

        logger.info(
            "pipeline_complete",
            session_id=context.session_id,
            escalation=context.escalation_required,
            convergence=context.convergence_score,
            skills_run=len(context.skill_results),
        )

        return context

    @classmethod
    async def from_config(
        cls,
        config_path: Path,
        registry: SkillRegistry,
        audit_writer: AuditWriter | None = None,
    ) -> SkillPipeline:
        """Build a pipeline from YAML configuration.

        Loads the config, instantiates skills from the registry in
        pipeline order, and returns a ready-to-execute pipeline.
        """
        config = load_pipeline_config(config_path)

        skills: list[tuple[str, Any]] = []
        for skill_name in config.pipeline:
            skill_config = config.skills.get(skill_name, {})

            # Skip disabled skills
            if not skill_config.get("enabled", True):
                logger.info("skill_disabled", skill=skill_name)
                continue

            try:
                skill = await registry.get(skill_name, skill_config)
                skills.append((skill_name, skill))
            except KeyError:
                logger.warning(
                    "skill_not_found",
                    skill=skill_name,
                    available=registry.registered_names,
                )

        return cls(skills=skills, audit_writer=audit_writer)
