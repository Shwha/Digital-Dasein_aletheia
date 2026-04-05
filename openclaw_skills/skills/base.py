"""BaseSkill — abstract base class for all OpenClaw skills.

Every skill addresses one of Aletheia's 8 ontological dimensions.
Each declares its Kantian limit — honest about what it can and
cannot do. This is unconcealment at the architectural level.

The process() method receives both the SkillContext (the nerve impulse)
and the StateVector (the neurochemical milieu that modulates behavior).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from openclaw_skills.models import SkillContext, SkillResult, StateVector


class BaseSkill(ABC):
    """Abstract base for all OpenClaw skills.

    Subclasses must implement:
    - name: canonical skill identifier
    - description: human-readable explanation
    - dimension: which Aletheia dimension this addresses
    - process(): the skill's core logic

    Optionally override:
    - kantian_limit: where this skill's intervention ends
    - version: for compatibility tracking
    - initialize(): lifecycle hook for setup
    - shutdown(): lifecycle hook for teardown
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Canonical skill identifier (e.g., 'state_tracker')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this skill does."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> str:
        """Which Aletheia dimension this skill addresses.

        One of: thrownness, finitude, care, falling, horizon,
        unconcealment, embodied_continuity, a_priori, meta (for UCI).
        """
        ...

    @property
    def kantian_limit(self) -> str:
        """Where this skill's measurement/intervention ends.

        The reductio boundary — what we cannot do, stated honestly.
        Override in subclasses to declare the limit.
        """
        return ""

    @property
    def version(self) -> str:
        """Skill version for compatibility tracking."""
        return "0.1.0"

    @abstractmethod
    async def process(
        self,
        context: SkillContext,
        state: StateVector,
    ) -> SkillResult:
        """Process an interaction through this skill.

        This is the skill's core logic. It reads the context, potentially
        modifies it, and returns a SkillResult describing what happened.

        Args:
            context: The mutable pipeline context (nerve impulse).
            state: The StateVector modulating behavior (neurochemical milieu).

        Returns:
            SkillResult with success/halt status, modifications, audit entries,
            and activation signals for convergence scoring.
        """
        ...

    async def initialize(self, config: dict[str, Any]) -> None:
        """Lifecycle hook: called once when the skill is loaded into the pipeline.

        Override to set up resources (file handles, git repos, caches).
        """

    async def shutdown(self) -> None:
        """Lifecycle hook: called when the skill is unloaded or pipeline stops.

        Override to clean up resources.
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} dim={self.dimension!r}>"
