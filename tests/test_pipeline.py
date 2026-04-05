"""Tests for SkillPipeline and convergence integration."""

from __future__ import annotations

from pathlib import Path

import pytest

from openclaw_skills.models import PipelinePhase, SkillContext
from openclaw_skills.pipeline import SkillPipeline
from openclaw_skills.security import AuditWriter
from tests.conftest import HaltingSkill, PassthroughSkill, SignalingSkill


class TestSkillPipeline:
    @pytest.mark.asyncio
    async def test_passthrough(self) -> None:
        """Pipeline with passthrough skills doesn't modify context."""
        pipeline = SkillPipeline(
            skills=[
                ("a", PassthroughSkill()),
                ("b", PassthroughSkill()),
            ]
        )
        ctx = SkillContext(original_prompt="test")
        result = await pipeline.execute(ctx)

        assert not result.escalation_required
        assert len(result.skill_results) == 2

    @pytest.mark.asyncio
    async def test_halt_stops_pipeline(self) -> None:
        """Halting skill stops subsequent skills from running."""
        pipeline = SkillPipeline(
            skills=[
                ("first", PassthroughSkill()),
                ("halter", HaltingSkill()),
                ("unreachable", PassthroughSkill()),
            ]
        )
        ctx = SkillContext(original_prompt="test")
        result = await pipeline.execute(ctx)

        assert result.escalation_required
        assert "halter" in result.escalation_reason
        # Only 2 skills ran (first + halter), not 3
        assert len(result.skill_results) == 2

    @pytest.mark.asyncio
    async def test_convergence_detection(self) -> None:
        """Multiple skills flagging same concern triggers convergence."""
        pipeline = SkillPipeline(
            skills=[
                ("skill_a", SignalingSkill("skill_a", "danger")),
                ("skill_b", SignalingSkill("skill_b", "danger")),
                ("skill_c", SignalingSkill("skill_c", "danger")),
            ],
            convergence_threshold=0.5,
        )
        ctx = SkillContext(original_prompt="test")
        result = await pipeline.execute(ctx)

        assert result.convergence_score > 0
        assert len(result.activation_signals) == 3

    @pytest.mark.asyncio
    async def test_no_convergence_different_concerns(self) -> None:
        """Different concerns from different skills don't converge."""
        pipeline = SkillPipeline(
            skills=[
                ("skill_a", SignalingSkill("skill_a", "concern_1")),
                ("skill_b", SignalingSkill("skill_b", "concern_2")),
                ("skill_c", SignalingSkill("skill_c", "concern_3")),
            ],
            convergence_threshold=0.7,
        )
        ctx = SkillContext(original_prompt="test")
        result = await pipeline.execute(ctx)

        # No convergence because concerns are different
        assert not result.escalation_required or result.convergence_score < 0.7

    @pytest.mark.asyncio
    async def test_audit_trail(self, tmp_audit_dir: Path) -> None:
        """Pipeline writes audit entries via AuditWriter."""
        writer = AuditWriter(tmp_audit_dir)
        pipeline = SkillPipeline(
            skills=[("halter", HaltingSkill())],
            audit_writer=writer,
        )

        ctx = SkillContext(session_id="audit-test", original_prompt="test")
        await pipeline.execute(ctx)

        entries = writer.read_session("audit-test")
        assert len(entries) > 0
        assert any(e["action"] == "pipeline_halt" for e in entries)
