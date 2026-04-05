"""Configuration management — Pydantic settings + YAML suite loader.

Follows the Aletheia pattern: environment variables for secrets,
YAML files for skill pipeline configuration. All API keys are
SecretStr — never logged, never serialized, never exposed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenClawSettings(BaseSettings):
    """Global settings loaded from environment variables and .env file.

    Secrets are SecretStr — .get_secret_value() only at point of use,
    never in logs, never in serialized output.
    """

    model_config = SettingsConfigDict(
        env_prefix="OPENCLAW_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys — loaded from standard env vars (no OPENCLAW_ prefix)
    openai_api_key: SecretStr = Field(default=SecretStr(""), alias="OPENAI_API_KEY")
    anthropic_api_key: SecretStr = Field(default=SecretStr(""), alias="ANTHROPIC_API_KEY")
    xai_api_key: SecretStr = Field(default=SecretStr(""), alias="XAI_API_KEY")
    google_api_key: SecretStr = Field(default=SecretStr(""), alias="GOOGLE_API_KEY")
    ollama_api_base: str = Field(
        default="http://localhost:11434", alias="OLLAMA_API_BASE"
    )

    # Network security
    proxy_url: str | None = None
    tls_cert_path: str | None = None
    verify_tls: bool = True

    # InstructionCompiler model (for LLM-assisted mode only)
    compiler_model: str = "gpt-4o-mini"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Storage paths (relative to working directory)
    state_dir: str = ".openclaw/state"
    audit_dir: str = ".openclaw/audit"


def _get_settings() -> OpenClawSettings:
    """Lazy singleton for settings."""
    return OpenClawSettings()


# Module-level accessor — import and call: get_settings()
get_settings = _get_settings


class SkillConfig(BaseSettings):
    """Configuration for a single skill, loaded from YAML."""

    model_config = SettingsConfigDict(extra="allow")

    enabled: bool = True


class PipelineConfig(BaseSettings):
    """Full pipeline configuration loaded from YAML file."""

    model_config = SettingsConfigDict(extra="allow")

    name: str = "default"
    description: str = ""
    pipeline: list[str] = Field(default_factory=list)
    skills: dict[str, dict[str, Any]] = Field(default_factory=dict)


def load_pipeline_config(config_path: Path) -> PipelineConfig:
    """Load and validate a pipeline configuration from YAML.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Validated PipelineConfig instance.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If YAML is malformed or fails validation.
    """
    if not config_path.exists():
        msg = f"Configuration file not found: {config_path}"
        raise FileNotFoundError(msg)

    raw = config_path.read_text(encoding="utf-8")

    # Defense: YAML can deserialize arbitrary Python objects via !!python tags.
    # Always use safe_load to prevent deserialization attacks.
    data = yaml.safe_load(raw)

    if not isinstance(data, dict):
        msg = f"Expected YAML mapping at top level, got {type(data).__name__}"
        raise ValueError(msg)

    return PipelineConfig(**data)
