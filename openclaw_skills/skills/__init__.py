"""Skill registry — maps dimension names to skill implementations.

Follows Aletheia's DIMENSION_REGISTRY pattern. Skills are registered
statically here for built-ins, and dynamically via entry_points for
third-party ClawHub packages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openclaw_skills.skills.base import BaseSkill

# Built-in skill registry — populated as skills are implemented.
# Third-party skills are discovered via entry_points at runtime.
SKILL_REGISTRY: dict[str, type[BaseSkill]] = {}
