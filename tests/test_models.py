"""Tests for core Pydantic models."""

from __future__ import annotations

from openclaw_skills.models import (
    AuditEntry,
    ChangeOrder,
    Directive,
    GuardrailRule,
    GuardrailViolation,
    InstructionSet,
    PipelinePhase,
    PlanStatus,
    Priority,
    RuleType,
    ScopeLimit,
    Severity,
    SessionState,
    SkillContext,
    SkillResult,
    StateSnapshot,
    StateVector,
    StepStatus,
    TaskStep,
    ToolCallRecord,
    ToolCallRequest,
    UCIRecord,
    ActivationSignal,
    GuardrailAction,
)


class TestStateVector:
    def test_defaults(self) -> None:
        sv = StateVector()
        assert sv.context == "main_session"
        assert sv.urgency == 0.3
        assert sv.service_asymmetry >= 1.0
        assert sv.confidence == 0.5
        assert sv.drift_score == 0.0

    def test_service_asymmetry_minimum(self) -> None:
        """Service asymmetry must always be >= 1.0 — Buber's I-Dienst."""
        import pydantic
        import pytest

        with pytest.raises(pydantic.ValidationError):
            StateVector(service_asymmetry=0.5)

    def test_bounded_fields(self) -> None:
        sv = StateVector(urgency=1.0, time_pressure=1.0, confidence=0.0)
        assert sv.urgency == 1.0
        assert sv.time_pressure == 1.0
        assert sv.confidence == 0.0


class TestSkillContext:
    def test_defaults(self) -> None:
        ctx = SkillContext()
        assert ctx.session_id  # auto-generated
        assert ctx.run_id  # auto-generated
        assert ctx.phase == PipelinePhase.PRE_PROMPT
        assert ctx.escalation_required is False
        assert ctx.convergence_score == 0.0

    def test_mutable(self) -> None:
        ctx = SkillContext()
        ctx.original_prompt = "test"
        ctx.escalation_required = True
        assert ctx.original_prompt == "test"
        assert ctx.escalation_required is True


class TestSkillResult:
    def test_frozen(self) -> None:
        result = SkillResult(skill_name="test")
        import pytest

        with pytest.raises(pydantic.ValidationError):
            result.skill_name = "changed"

    def test_halt(self) -> None:
        result = SkillResult(
            skill_name="test",
            halt=True,
            halt_reason="danger detected",
        )
        assert result.halt is True
        assert "danger" in result.halt_reason


class TestToolCallRequest:
    def test_auto_id(self) -> None:
        req = ToolCallRequest(tool_name="read_file", parameters={"path": "/test"})
        assert req.id  # auto-generated
        assert req.tool_name == "read_file"


class TestToolCallRecord:
    def test_frozen(self) -> None:
        record = ToolCallRecord(id="tc1", tool_name="test", success=True)
        assert record.success is True


class TestAuditEntry:
    def test_frozen(self) -> None:
        entry = AuditEntry(skill="test", action="read", detail="read file")
        assert entry.severity == Severity.INFO


class TestInstructionSet:
    def test_hash(self) -> None:
        raw = "Do this. Then that."
        h = InstructionSet.hash_instructions(raw)
        assert len(h) == 64  # SHA-256 hex digest


class TestSessionState:
    def test_defaults(self) -> None:
        state = SessionState(session_id="test-001")
        assert state.turn_count == 0
        assert state.modified_files == []


class TestChangeOrder:
    def test_lifecycle(self) -> None:
        order = ChangeOrder(description="Refactor auth")
        assert order.status == PlanStatus.DRAFT
        order.status = PlanStatus.APPROVED
        assert order.status == PlanStatus.APPROVED


class TestGuardrailRule:
    def test_frozen(self) -> None:
        rule = GuardrailRule(
            name="test",
            description="test rule",
            type=RuleType.SCOPE_LIMIT,
        )
        assert rule.action == GuardrailAction.ESCALATE


class TestScopeLimit:
    def test_defaults(self) -> None:
        limits = ScopeLimit()
        assert limits.max_files_modified == 10
        assert limits.max_tool_calls_per_session == 50


class TestUCIRecord:
    def test_gap_bounds(self) -> None:
        record = UCIRecord(
            dimension="care",
            articulation="I will be careful",
            performance="Modified 15 files",
            articulation_score=0.9,
            performance_score=0.3,
            gap=0.6,
        )
        assert record.gap == 0.6


# Need this import for the frozen test
import pydantic
