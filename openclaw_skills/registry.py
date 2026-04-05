"""SkillRegistry — discovers, registers, and instantiates skills.

Skills are registered through three mechanisms:
1. Statically in skills/__init__.py (built-in skills)
2. Via entry_points (third-party ClawHub packages)
3. Via YAML config listing explicit module paths

The registry is the nervous system's receptor map — it knows what
capabilities are available and how to instantiate them.
"""

from __future__ import annotations

import importlib
import importlib.metadata
from typing import Any

from openclaw_skills.logging import get_logger
from openclaw_skills.skills import SKILL_REGISTRY
from openclaw_skills.skills.base import BaseSkill

logger = get_logger(__name__)

# Entry point group name for third-party skill discovery
ENTRY_POINT_GROUP = "openclaw_skills.plugins"


class SkillRegistry:
    """Discovers, registers, and instantiates skills."""

    def __init__(self) -> None:
        self._registry: dict[str, type[BaseSkill]] = dict(SKILL_REGISTRY)
        self._instances: dict[str, BaseSkill] = {}

    def discover_entry_points(self) -> int:
        """Load skills from the 'openclaw_skills.plugins' entry point group.

        Returns the number of newly discovered skills.
        """
        discovered = 0
        eps = importlib.metadata.entry_points()

        # Python 3.12+: entry_points() returns SelectableGroups
        group = eps.select(group=ENTRY_POINT_GROUP)

        for ep in group:
            if ep.name in self._registry:
                logger.warning(
                    "entry_point_conflict",
                    skill=ep.name,
                    msg="Skipping — already registered",
                )
                continue

            try:
                skill_class = ep.load()
                if not (isinstance(skill_class, type) and issubclass(skill_class, BaseSkill)):
                    logger.warning(
                        "entry_point_invalid",
                        skill=ep.name,
                        msg="Not a BaseSkill subclass",
                    )
                    continue

                self._registry[ep.name] = skill_class
                discovered += 1
                logger.info("entry_point_loaded", skill=ep.name)

            except Exception:
                logger.exception("entry_point_load_failed", skill=ep.name)

        return discovered

    def register(self, name: str, skill_class: type[BaseSkill]) -> None:
        """Register a skill class by name.

        Raises:
            ValueError: If a skill with this name is already registered.
        """
        if name in self._registry:
            msg = f"Skill already registered: {name}"
            raise ValueError(msg)
        self._registry[name] = skill_class
        logger.info("skill_registered", skill=name)

    async def get(self, name: str, config: dict[str, Any] | None = None) -> BaseSkill:
        """Instantiate and return a configured skill.

        Caches instances — same name returns same instance.
        Calls initialize() on first instantiation.

        Raises:
            KeyError: If skill name is not registered.
        """
        if name in self._instances:
            return self._instances[name]

        if name not in self._registry:
            msg = f"Unknown skill: {name}. Available: {list(self._registry.keys())}"
            raise KeyError(msg)

        skill_class = self._registry[name]
        skill = skill_class()
        await skill.initialize(config or {})

        self._instances[name] = skill
        logger.info("skill_instantiated", skill=name, version=skill.version)
        return skill

    async def shutdown_all(self) -> None:
        """Shutdown all instantiated skills."""
        for name, skill in self._instances.items():
            try:
                await skill.shutdown()
                logger.info("skill_shutdown", skill=name)
            except Exception:
                logger.exception("skill_shutdown_failed", skill=name)
        self._instances.clear()

    def list_available(self) -> list[dict[str, str]]:
        """Return metadata for all registered skills."""
        result = []
        for name, cls in sorted(self._registry.items()):
            # Instantiate temporarily to read properties
            try:
                instance = cls()
                result.append({
                    "name": name,
                    "description": instance.description,
                    "dimension": instance.dimension,
                    "version": instance.version,
                    "kantian_limit": instance.kantian_limit,
                })
            except Exception:
                result.append({
                    "name": name,
                    "description": "(failed to read metadata)",
                    "dimension": "unknown",
                    "version": "unknown",
                    "kantian_limit": "",
                })
        return result

    @property
    def registered_names(self) -> list[str]:
        """Return sorted list of registered skill names."""
        return sorted(self._registry.keys())

    def is_registered(self, name: str) -> bool:
        """Check if a skill name is registered."""
        return name in self._registry

    def resolve_module(self, module_path: str) -> type[BaseSkill]:
        """Dynamically import a skill class from a dotted module path.

        Format: 'package.module:ClassName'

        Raises:
            ImportError: If module or class not found.
            TypeError: If resolved class is not a BaseSkill subclass.
        """
        if ":" not in module_path:
            msg = f"Expected 'module.path:ClassName' format, got: {module_path}"
            raise ImportError(msg)

        module_name, class_name = module_path.rsplit(":", 1)
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)

        if not (isinstance(cls, type) and issubclass(cls, BaseSkill)):
            msg = f"{module_path} resolved to {cls}, not a BaseSkill subclass"
            raise TypeError(msg)

        return cls
