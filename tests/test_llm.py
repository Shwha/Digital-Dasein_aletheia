"""
Tests for the LiteLLM wrapper.
"""

from __future__ import annotations

import os
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
