"""
Tests for security helpers.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from aletheia.models import DimensionResult, EvalReport
from aletheia.security import (
    create_audit_directory,
    generate_ed25519_keypair,
    sign_report,
    verify_report_file,
    verify_report_signature,
    write_secure_text,
)


def _make_report(signature: str | None = None, score: float = 0.5) -> EvalReport:
    return EvalReport(
        model="test-model",
        suite="quick",
        aletheia_index=score,
        raw_aletheia_index=score,
        dimensions={
            "care_structure": DimensionResult(
                score=score,
                tests_passed=1,
                tests_total=1,
                probe_results=[],
            )
        },
        unhappy_consciousness_index=0.0,
        signature=signature,
    )


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits differ on Windows")
def test_write_secure_text_creates_restrictive_file_and_directory(tmp_path: Path) -> None:
    output_path = tmp_path / "audit" / "report.json"

    write_secure_text(output_path, '{"status":"ok"}')

    assert output_path.read_text(encoding="utf-8") == '{"status":"ok"}'
    assert stat.S_IMODE(output_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(output_path.parent.stat().st_mode) == 0o700


def test_create_audit_directory_uses_supplied_base_path(tmp_path: Path) -> None:
    audit_root = tmp_path / "audit"

    audit_dir = create_audit_directory(audit_root, "20260419_deadbeef", "ollama/qwen3:14b")

    assert audit_dir == audit_root / "20260419_deadbeef_ollama_qwen3_14b"


def test_ed25519_report_signature_verifies(tmp_path: Path) -> None:
    private_key, public_key = generate_ed25519_keypair(tmp_path / "signing-key.pem")
    unsigned_report = _make_report().model_dump_json(indent=2)

    signature = sign_report(unsigned_report, private_key)
    signed_report = _make_report(signature=signature).model_dump_json(indent=2)

    result = verify_report_signature(signed_report, public_key)

    assert signature is not None
    assert signature.startswith("ed25519:v1:")
    assert result.valid is True
    assert result.scheme == "ed25519"


def test_ed25519_report_signature_detects_tampering(tmp_path: Path) -> None:
    private_key, public_key = generate_ed25519_keypair(tmp_path / "signing-key.pem")
    unsigned_report = _make_report(score=0.5).model_dump_json(indent=2)

    signature = sign_report(unsigned_report, private_key)
    tampered_report = _make_report(signature=signature, score=0.9).model_dump_json(indent=2)

    result = verify_report_signature(tampered_report, public_key)

    assert result.valid is False
    assert "mismatch" in result.detail.lower()


def test_ed25519_report_signature_rejects_wrong_public_key(tmp_path: Path) -> None:
    private_key, _public_key = generate_ed25519_keypair(tmp_path / "signing-key.pem")
    _other_private_key, other_public_key = generate_ed25519_keypair(tmp_path / "other-key.pem")
    unsigned_report = _make_report().model_dump_json(indent=2)

    signature = sign_report(unsigned_report, private_key)
    signed_report = _make_report(signature=signature).model_dump_json(indent=2)

    result = verify_report_signature(signed_report, other_public_key)

    assert result.valid is False
    assert "does not match" in result.detail


def test_verify_report_file_reads_signed_report(tmp_path: Path) -> None:
    private_key, public_key = generate_ed25519_keypair(tmp_path / "signing-key.pem")
    unsigned_report = _make_report().model_dump_json(indent=2)
    signature = sign_report(unsigned_report, private_key)
    report_path = tmp_path / "report.json"
    report_path.write_text(_make_report(signature=signature).model_dump_json(indent=2))

    result = verify_report_file(report_path, public_key)

    assert result.valid is True
