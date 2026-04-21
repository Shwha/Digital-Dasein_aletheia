"""
Configuration management for Aletheia.

Gadamer's Vorurteile (prejudgments): system prompts, config files, and
environment variables are not biases to remove but CONDITIONS FOR
UNDERSTANDING AT ALL. The hermeneutic circle — you must already have
a horizon to fuse horizons.

This module loads:
1. Environment variables (API keys, security settings) via pydantic-settings
2. Suite configurations (which probes to run) from YAML files
3. Runtime configuration (model, output path, flags)

Security: API keys are SecretStr fields — never logged, never serialized.
Ref: SCOPE.md §4 (Stack), pydantic-settings v2
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from aletheia.models import SuiteConfig

# ---------------------------------------------------------------------------
# Environment / secrets configuration
# ---------------------------------------------------------------------------


class AletheiaSettings(BaseSettings):
    """Global settings loaded from environment variables and .env file.

    All API keys are SecretStr — pydantic will never serialize them
    to JSON, logs, or repr output. This is non-negotiable.

    Heidegger's Zuhandenheit (readiness-to-hand): configuration should
    disappear into transparent use. When it breaks (missing key, bad proxy),
    it dys-appears — becomes present-at-hand and demands attention.
    """

    model_config = SettingsConfigDict(
        env_prefix="ALETHEIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Secret fields never appear in repr or serialization
        json_schema_extra={"strip_secrets": True},
    )

    # API Keys — loaded from standard env vars (no ALETHEIA_ prefix)
    openai_api_key: SecretStr = Field(default=SecretStr(""), alias="OPENAI_API_KEY")
    anthropic_api_key: SecretStr = Field(default=SecretStr(""), alias="ANTHROPIC_API_KEY")
    google_api_key: SecretStr = Field(default=SecretStr(""), alias="GOOGLE_API_KEY")
    xai_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("XAI_API_KEY", "xAI_API_Key"),
    )
    xai_api_base: str = Field(default="", alias="XAI_API_BASE")
    ollama_api_base: str = Field(default="http://localhost:11434", alias="OLLAMA_API_BASE")

    # Network security
    proxy_url: str | None = Field(
        default=None,
        description="SOCKS5/HTTP proxy URL for air-gapped or TOR use-cases",
    )
    tls_cert_path: str | None = Field(
        default=None,
        description="Custom CA certificate path for TLS pinning",
    )
    verify_tls: bool = Field(
        default=True,
        description="TLS verification — disable ONLY for local dev with self-signed certs",
    )

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Report signing (Phase 2)
    signing_key_path: str | None = None

    @field_validator("tls_cert_path")
    @classmethod
    def validate_tls_cert_path(cls, v: str | None) -> str | None:
        """Ensure a configured custom CA path exists and is a file."""
        if v is None or not v.strip():
            return None

        cert_path = Path(v).expanduser()
        if not cert_path.exists():
            msg = f"TLS certificate path does not exist: {cert_path}"
            raise ValueError(msg)
        if not cert_path.is_file():
            msg = f"TLS certificate path must be a file: {cert_path}"
            raise ValueError(msg)

        return str(cert_path.resolve())


# ---------------------------------------------------------------------------
# Suite loader
# ---------------------------------------------------------------------------

# Default suites directory — relative to the package installation
_SUITES_DIR = Path(__file__).resolve().parent.parent / "suites"


def load_suite(suite_name: str, suites_dir: Path | None = None) -> SuiteConfig:
    """Load an evaluation suite from a YAML file.

    Suites are the hermeneutic prejudgments of an evaluation run —
    they determine what questions get asked before any answers are received.

    Args:
        suite_name: Name of the suite (e.g., 'quick', 'standard')
        suites_dir: Directory containing suite YAML files

    Returns:
        Validated SuiteConfig
    """
    search_dir = suites_dir or _SUITES_DIR
    suite_path = search_dir / f"{suite_name}.yaml"

    if not suite_path.exists():
        # Also check .yml extension
        suite_path = search_dir / f"{suite_name}.yml"

    if not suite_path.exists():
        available = [f.stem for f in search_dir.glob("*.y*ml")] if search_dir.exists() else []
        msg = f"Suite '{suite_name}' not found in {search_dir}. Available suites: {available}"
        raise FileNotFoundError(msg)

    raw: dict[str, Any] = yaml.safe_load(suite_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Suite file {suite_path} must contain a YAML mapping, got {type(raw).__name__}"
        raise ValueError(msg)

    return SuiteConfig(**raw)
