"""Tests for configuration management."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from openclaw_skills.config import (
    OpenClawSettings,
    PipelineConfig,
    load_pipeline_config,
)


class TestOpenClawSettings:
    def test_defaults(self) -> None:
        settings = OpenClawSettings()
        assert settings.verify_tls is True
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"

    def test_api_keys_are_secret(self) -> None:
        settings = OpenClawSettings()
        # SecretStr should NOT reveal value in repr/str
        assert "sk-" not in repr(settings.openai_api_key)
        assert "sk-" not in str(settings.openai_api_key)


class TestPipelineConfig:
    def test_from_dict(self) -> None:
        cfg = PipelineConfig(
            name="test",
            description="test config",
            pipeline=["state_tracker", "tool_guard"],
            skills={
                "state_tracker": {"enabled": True},
                "tool_guard": {"enabled": False},
            },
        )
        assert cfg.name == "test"
        assert len(cfg.pipeline) == 2
        assert cfg.skills["tool_guard"]["enabled"] is False


class TestLoadPipelineConfig:
    def test_load_valid(self, tmp_path: Path) -> None:
        config_file = tmp_path / "test.yaml"
        config_file.write_text(
            yaml.dump({
                "name": "test",
                "description": "test",
                "pipeline": ["a", "b"],
                "skills": {"a": {"enabled": True}},
            })
        )
        cfg = load_pipeline_config(config_file)
        assert cfg.name == "test"
        assert cfg.pipeline == ["a", "b"]

    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_pipeline_config(tmp_path / "nonexistent.yaml")

    def test_malformed_yaml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "bad.yaml"
        config_file.write_text("just a string")
        with pytest.raises(ValueError, match="Expected YAML mapping"):
            load_pipeline_config(config_file)

    def test_load_default_config(self) -> None:
        """Verify the shipped default.yaml loads correctly."""
        default = Path("configs/default.yaml")
        if default.exists():
            cfg = load_pipeline_config(default)
            assert cfg.name == "default"
            assert len(cfg.pipeline) >= 5
