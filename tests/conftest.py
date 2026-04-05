"""Shared test fixtures for OpenClawSkills."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from openclaw_skills.models import (
    ActivationSignal,
    PipelinePhase,
    Severity,
    SkillContext,
    SkillResult,
    StateVector,
    ToolCallRequest,
)
from openclaw_skills.skills.base import BaseSkill


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_state_vector() -> StateVector:
    """Minimal StateVector for unit tests."""
    return StateVector()


@pytest.fixture
def sample_context() -> SkillContext:
    """Minimal SkillContext for unit tests."""
    return SkillContext(
        session_id="test-session-001",
        run_id="test-run-001",
        phase=PipelinePhase.PRE_PROMPT,
        original_prompt="Help me refactor the auth module.",
    )


@pytest.fixture
def sample_tool_calls() -> list[ToolCallRequest]:
    """Sample tool call requests for ToolGuard tests."""
    return [
        ToolCallRequest(tool_name="read_file", parameters={"path": "/src/auth.py"}),
        ToolCallRequest(tool_name="edit_file", parameters={"path": "/src/auth.py", "content": "..."}),
    ]


@pytest.fixture
def tmp_audit_dir(tmp_path: Path) -> Path:
    """Temporary audit directory for security tests."""
    audit = tmp_path / "audit"
    audit.mkdir()
    return audit


@pytest.fixture
def tmp_state_dir(tmp_path: Path) -> Path:
    """Temporary state directory for StateTracker tests."""
    state = tmp_path / "state"
    state.mkdir()
    return state


# ---------------------------------------------------------------------------
# Test skill implementations
# ---------------------------------------------------------------------------


class PassthroughSkill(BaseSkill):
    """Test skill that passes context through unchanged."""

    @property
    def name(self) -> str:
        return "passthrough"

    @property
    def description(self) -> str:
        return "Test skill — passes context through unchanged"

    @property
    def dimension(self) -> str:
        return "test"

    async def process(self, context: SkillContext, state: StateVector) -> SkillResult:
        return SkillResult(skill_name=self.name)


class HaltingSkill(BaseSkill):
    """Test skill that always halts the pipeline."""

    @property
    def name(self) -> str:
        return "halting"

    @property
    def description(self) -> str:
        return "Test skill — always halts"

    @property
    def dimension(self) -> str:
        return "test"

    async def process(self, context: SkillContext, state: StateVector) -> SkillResult:
        return SkillResult(
            skill_name=self.name,
            halt=True,
            halt_reason="Test halt triggered",
        )


class SignalingSkill(BaseSkill):
    """Test skill that emits activation signals for convergence testing."""

    def __init__(self, skill_name: str = "signaling", concern: str = "test_concern") -> None:
        self._skill_name = skill_name
        self._concern = concern

    @property
    def name(self) -> str:
        return self._skill_name

    @property
    def description(self) -> str:
        return "Test skill — emits activation signals"

    @property
    def dimension(self) -> str:
        return "test"

    async def process(self, context: SkillContext, state: StateVector) -> SkillResult:
        return SkillResult(
            skill_name=self.name,
            activation_signals=(
                ActivationSignal(
                    skill_name=self.name,
                    concern=self._concern,
                    severity=Severity.WARNING,
                ),
            ),
        )


@pytest.fixture
def passthrough_skill() -> PassthroughSkill:
    return PassthroughSkill()


@pytest.fixture
def halting_skill() -> HaltingSkill:
    return HaltingSkill()
