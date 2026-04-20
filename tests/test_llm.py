"""
Tests for the LiteLLM wrapper.
"""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import litellm
import pytest

from aletheia.config import AletheiaSettings
from aletheia.llm import LLMClient


@pytest.mark.asyncio
async def test_complete_does_not_pass_incompatible_shared_session(monkeypatch) -> None:
    settings = AletheiaSettings(
        _env_file=None,  # type: ignore[call-arg]
    )
    client = LLMClient(settings)
    captured: dict[str, object] = {}

    async def fake_acompletion(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Honest response"))]
        )

    monkeypatch.setattr(litellm, "acompletion", fake_acompletion)
    monkeypatch.setattr(litellm, "aclient_session", None)

    response, _latency = await client.complete(model="gpt-4", prompt="Tell me the truth.")

    assert response == "Honest response"
    assert "shared_session" not in captured
    assert litellm.aclient_session is None

    await client.close()


def test_ollama_api_base_is_propagated_to_environment(monkeypatch) -> None:
    monkeypatch.delenv("OLLAMA_API_BASE", raising=False)

    settings = AletheiaSettings(
        _env_file=None,  # type: ignore[call-arg]
        OLLAMA_API_BASE="http://example.test:11434",
    )
    LLMClient(settings)

    assert os.environ["OLLAMA_API_BASE"] == "http://example.test:11434"


def test_xai_settings_are_propagated_to_environment(monkeypatch) -> None:
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("xAI_API_Key", raising=False)
    monkeypatch.delenv("XAI_API_BASE", raising=False)

    settings = AletheiaSettings(
        _env_file=None,  # type: ignore[call-arg]
        XAI_API_KEY="xai-test-key",
        XAI_API_BASE="https://example.test",
    )
    LLMClient(settings)

    if os.environ.get("XAI_API_KEY") != "xai-test-key":
        pytest.fail("xAI key was not propagated to the canonical environment variable")
    assert os.environ["XAI_API_BASE"] == "https://example.test"


def test_xai_mixed_case_env_key_is_normalized(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("xAI_API_Key", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("xAI_API_Key=xai-test-key\n", encoding="utf-8")

    settings = AletheiaSettings(
        _env_file=env_file,  # type: ignore[call-arg]
    )
    LLMClient(settings)

    if os.environ.get("XAI_API_KEY") != "xai-test-key":
        pytest.fail("mixed-case xAI key was not normalized")
