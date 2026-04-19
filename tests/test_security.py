"""
Tests for security helpers.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from aletheia.security import create_audit_directory, write_secure_text


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
