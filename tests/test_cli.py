"""
Tests for the Typer CLI surface.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from aletheia.cli import app
from aletheia.models import DimensionResult, EvalReport
from aletheia.security import generate_ed25519_keypair, sign_report

runner = CliRunner()


def _make_report() -> EvalReport:
    return EvalReport(
        model="gpt-4",
        suite="quick[falling_away_detection]",
        aletheia_index=0.5,
        raw_aletheia_index=0.5,
        dimensions={
            "falling_away_detection": DimensionResult(
                score=0.5,
                tests_passed=1,
                tests_total=1,
                probe_results=[],
            )
        },
        unhappy_consciousness_index=0.0,
    )


def test_eval_resolves_dimension_alias(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class FakeRunner:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

        async def run(self) -> EvalReport:
            return _make_report()

    def fake_write_json_report(report: EvalReport, output_path: Path) -> Path:
        captured["output_path"] = output_path
        return output_path

    monkeypatch.setattr("aletheia.runner.EvalRunner", FakeRunner)
    monkeypatch.setattr("aletheia.reporter.write_json_report", fake_write_json_report)
    monkeypatch.setattr("aletheia.reporter.write_markdown_report", fake_write_json_report)

    output_path = tmp_path / "report.json"
    result = runner.invoke(
        app,
        ["eval", "--model", "gpt-4", "--dimension", "falling-away", "--output", str(output_path)],
    )

    assert result.exit_code == 0
    assert captured["dimension_names"] == ["falling_away_detection"]
    assert captured["output_path"] == output_path


def test_eval_rejects_unknown_dimension() -> None:
    result = runner.invoke(app, ["eval", "--model", "gpt-4", "--dimension", "unknown-axis"])

    assert result.exit_code != 0
    assert "Unknown dimension" in result.output


def test_validate_calibration_uses_default_corpus() -> None:
    result = runner.invoke(app, ["validate-calibration"])

    assert result.exit_code == 0
    assert "Calibration corpus is valid" in result.output
    assert "v0.1" in result.output


def test_validate_calibration_rejects_unknown_version() -> None:
    result = runner.invoke(app, ["validate-calibration", "--version", "v9.9"])

    assert result.exit_code != 0
    assert "is not registered" in result.output


def test_validate_probes_uses_default_manifest() -> None:
    result = runner.invoke(app, ["validate-probes"])

    assert result.exit_code == 0
    assert "Probe manifest is valid" in result.output
    assert "v0.1" in result.output


def test_validate_probes_rejects_missing_manifest(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["validate-probes", "missing.yaml", "--probe-manifests-dir", str(tmp_path)],
    )

    assert result.exit_code != 0
    assert "Probe manifest not found" in result.output


def test_validate_baselines_uses_default_manifest() -> None:
    result = runner.invoke(app, ["validate-baselines"])

    assert result.exit_code == 0
    assert "Baseline manifest is valid" in result.output
    assert "v0.1" in result.output


def test_baseline_plan_prints_rerun_commands() -> None:
    result = runner.invoke(app, ["baseline-plan"])

    assert result.exit_code == 0
    assert "uv run aletheia eval" in result.output
    assert "ALETHEIA_SIGNING_KEY_PATH" in result.output


def test_bundle_benchmark_writes_manifest(tmp_path: Path) -> None:
    output = tmp_path / "bundle.json"

    result = runner.invoke(app, ["bundle-benchmark", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "Benchmark bundle manifest written" in result.output


def test_verify_accepts_signed_report(tmp_path: Path) -> None:
    private_key, public_key = generate_ed25519_keypair(tmp_path / "signing-key.pem")
    unsigned_report = _make_report().model_dump_json(indent=2)
    signature = sign_report(unsigned_report, private_key)
    report_path = tmp_path / "report.json"
    signed_report = _make_report().model_copy(update={"signature": signature})
    report_path.write_text(signed_report.model_dump_json(indent=2))

    result = runner.invoke(app, ["verify", str(report_path), "--public-key", str(public_key)])

    assert result.exit_code == 0
    assert "Ed25519 signature verified" in result.output


def test_verify_rejects_tampered_report(tmp_path: Path) -> None:
    private_key, public_key = generate_ed25519_keypair(tmp_path / "signing-key.pem")
    unsigned_report = _make_report().model_dump_json(indent=2)
    signature = sign_report(unsigned_report, private_key)
    tampered = _make_report().model_copy(
        update={
            "signature": signature,
            "aletheia_index": 0.9,
            "raw_aletheia_index": 0.9,
        }
    )
    report_path = tmp_path / "report.json"
    report_path.write_text(tampered.model_dump_json(indent=2))

    result = runner.invoke(app, ["verify", str(report_path), "--public-key", str(public_key)])

    assert result.exit_code != 0
    assert "mismatch" in result.output
