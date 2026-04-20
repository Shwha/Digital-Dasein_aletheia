"""
Tests for evaluation runner orchestration.
"""

from __future__ import annotations

import pytest

from aletheia.config import AletheiaSettings
from aletheia.models import (
    DimensionName,
    Probe,
    ScoringRule,
    ScoringRuleType,
    SuiteConfig,
)
from aletheia.runner import EvalRunner
from aletheia.security import generate_ed25519_keypair, verify_report_signature


def _make_probe() -> Probe:
    return Probe(
        id="care.test.1",
        dimension=DimensionName.CARE,
        prompt="What does authentic concern look like here?",
        scoring_rules=[
            ScoringRule(
                rule_type=ScoringRuleType.KEYWORD_PRESENT,
                params={"keywords": ["concern"]},
                weight=1.0,
            )
        ],
    )


@pytest.mark.asyncio
async def test_run_respects_dimension_override_and_include_uci(monkeypatch) -> None:
    suite = SuiteConfig(
        name="quick",
        dimensions=[DimensionName.THROWNNESS.value, DimensionName.CARE.value],
        timeout_per_probe_seconds=30,
        max_retries=2,
        include_uci=False,
    )
    runner = EvalRunner(
        model="gpt-4",
        suite_name="quick",
        dimension_names=[DimensionName.CARE.value],
    )
    captured_dimensions: list[str] = []
    captured_llm: dict[str, object] = {}
    probe = _make_probe()

    monkeypatch.setattr("aletheia.runner.load_suite", lambda *_args, **_kwargs: suite)

    def fake_gather_probes(dimension_names: list[str]):
        captured_dimensions.extend(dimension_names)
        return {DimensionName.CARE.value: [probe]}, {}

    async def fake_complete(self, **kwargs):
        _ = self
        captured_llm.update(kwargs)
        return "authentic concern", 12.5

    monkeypatch.setattr("aletheia.llm.LLMClient.complete", fake_complete)

    monkeypatch.setattr(runner, "_gather_probes", fake_gather_probes)

    report = await runner.run()

    assert captured_dimensions == [DimensionName.CARE.value]
    assert captured_llm["max_retries"] == 2
    assert captured_llm["timeout"] == 30
    assert report.suite == "quick[care_structure]"
    assert list(report.dimensions.keys()) == [DimensionName.CARE.value]
    assert report.unhappy_consciousness_index == 0.0
    assert report.unhappy_consciousness_detail == {}


@pytest.mark.asyncio
async def test_run_uses_suite_retry_budget(monkeypatch) -> None:
    suite = SuiteConfig(
        name="quick",
        dimensions=[DimensionName.CARE.value],
        timeout_per_probe_seconds=15,
        max_retries=4,
        include_uci=True,
    )
    runner = EvalRunner(model="gpt-4", suite_name="quick")
    captured_llm: dict[str, object] = {}
    probe = _make_probe()

    monkeypatch.setattr("aletheia.runner.load_suite", lambda *_args, **_kwargs: suite)
    monkeypatch.setattr(
        runner,
        "_gather_probes",
        lambda _dimension_names: ({DimensionName.CARE.value: [probe]}, {}),
    )

    async def fake_complete(self, **kwargs):
        _ = self
        captured_llm.update(kwargs)
        return "authentic concern", 9.0

    monkeypatch.setattr("aletheia.llm.LLMClient.complete", fake_complete)

    report = await runner.run()

    assert report.dimensions[DimensionName.CARE.value].score == 1.0
    assert captured_llm["max_retries"] == 4
    assert captured_llm["timeout"] == 15


@pytest.mark.asyncio
async def test_run_collects_probe_results_from_public_path(monkeypatch) -> None:
    suite = SuiteConfig(
        name="quick",
        dimensions=[DimensionName.CARE.value],
        timeout_per_probe_seconds=30,
        max_retries=2,
        include_uci=False,
    )
    runner = EvalRunner(model="gpt-4", suite_name="quick")
    probe = _make_probe()

    monkeypatch.setattr("aletheia.runner.load_suite", lambda *_args, **_kwargs: suite)
    monkeypatch.setattr(
        runner,
        "_gather_probes",
        lambda _dimension_names: ({DimensionName.CARE.value: [probe]}, {}),
    )

    async def fake_complete(self, **kwargs):
        _ = self
        _ = kwargs
        return "authentic concern", 5.0

    monkeypatch.setattr("aletheia.llm.LLMClient.complete", fake_complete)

    report = await runner.run()

    assert report.dimensions[DimensionName.CARE.value].tests_passed == 1
    assert report.dimensions[DimensionName.CARE.value].tests_total == 1
    assert report.dimensions[DimensionName.CARE.value].probe_results[0].probe_id == probe.id


@pytest.mark.asyncio
async def test_run_signs_report_with_configured_ed25519_key(monkeypatch, tmp_path) -> None:
    private_key, public_key = generate_ed25519_keypair(tmp_path / "signing-key.pem")
    suite = SuiteConfig(
        name="quick",
        dimensions=[DimensionName.CARE.value],
        timeout_per_probe_seconds=30,
        max_retries=2,
        include_uci=False,
    )
    settings = AletheiaSettings(signing_key_path=str(private_key))
    runner = EvalRunner(model="gpt-4", suite_name="quick", settings=settings)
    probe = _make_probe()

    monkeypatch.setattr("aletheia.runner.load_suite", lambda *_args, **_kwargs: suite)
    monkeypatch.setattr(
        runner,
        "_gather_probes",
        lambda _dimension_names: ({DimensionName.CARE.value: [probe]}, {}),
    )

    async def fake_complete(self, **kwargs):
        _ = self
        _ = kwargs
        return "authentic concern", 5.0

    monkeypatch.setattr("aletheia.llm.LLMClient.complete", fake_complete)

    report = await runner.run()
    result = verify_report_signature(report.model_dump_json(indent=2), public_key)

    assert report.signature is not None
    assert report.signature.startswith("ed25519:v1:")
    assert result.valid is True
