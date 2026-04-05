"""Tests for security utilities."""

from __future__ import annotations

from pathlib import Path

from openclaw_skills.models import AuditEntry, Severity
from openclaw_skills.security import (
    AuditWriter,
    generate_run_id,
    sanitize_text,
    scan_for_secrets,
)


class TestGenerateRunId:
    def test_length(self) -> None:
        run_id = generate_run_id()
        assert len(run_id) == 32  # 16 bytes hex = 32 chars

    def test_uniqueness(self) -> None:
        ids = {generate_run_id() for _ in range(100)}
        assert len(ids) == 100


class TestScanForSecrets:
    def test_clean_text(self) -> None:
        assert scan_for_secrets("Hello, this is normal text") == []

    def test_detects_openai_key(self) -> None:
        findings = scan_for_secrets("key is sk-abc123def456ghi789jkl012mno345pqr678")
        assert len(findings) > 0

    def test_detects_anthropic_key(self) -> None:
        findings = scan_for_secrets("sk-ant-abc123-def456ghi789jkl012mno345")
        assert len(findings) > 0

    def test_detects_aws_key(self) -> None:
        findings = scan_for_secrets("AKIAIOSFODNN7EXAMPLE")
        assert len(findings) > 0

    def test_detects_bearer_token(self) -> None:
        findings = scan_for_secrets("Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6")
        assert len(findings) > 0

    def test_detects_private_key(self) -> None:
        findings = scan_for_secrets("-----BEGIN RSA PRIVATE KEY-----")
        assert len(findings) > 0

    def test_does_not_leak_matched_value(self) -> None:
        """Findings should describe the pattern, NOT include the secret."""
        findings = scan_for_secrets("sk-abc123def456ghi789jkl012mno345pqr678")
        for finding in findings:
            assert "sk-abc123" not in finding


class TestSanitizeText:
    def test_strips_control_chars(self) -> None:
        text = "Hello\x00World\x01Test\x7f"
        sanitized = sanitize_text(text)
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized
        assert "\x7f" not in sanitized
        assert "Hello" in sanitized

    def test_preserves_newlines(self) -> None:
        text = "Line 1\nLine 2\rLine 3\tTabbed"
        sanitized = sanitize_text(text)
        assert "\n" in sanitized
        assert "\r" in sanitized
        assert "\t" in sanitized

    def test_truncation(self) -> None:
        text = "x" * 100_000
        sanitized = sanitize_text(text, max_length=1000)
        assert len(sanitized) < 1100  # 1000 + truncation message
        assert "TRUNCATED" in sanitized


class TestAuditWriter:
    def test_write_and_read(self, tmp_audit_dir: Path) -> None:
        writer = AuditWriter(tmp_audit_dir)
        entry = AuditEntry(
            skill="test_skill",
            action="test_action",
            detail="test detail",
        )
        writer.write("session-001", entry)

        entries = writer.read_session("session-001")
        assert len(entries) == 1
        assert entries[0]["skill"] == "test_skill"

    def test_multiple_entries(self, tmp_audit_dir: Path) -> None:
        writer = AuditWriter(tmp_audit_dir)
        for i in range(5):
            writer.write(
                "session-002",
                AuditEntry(skill=f"skill_{i}", action="test", detail=f"entry {i}"),
            )

        entries = writer.read_session("session-002")
        assert len(entries) == 5

    def test_list_sessions(self, tmp_audit_dir: Path) -> None:
        writer = AuditWriter(tmp_audit_dir)
        writer.write("s1", AuditEntry(skill="a", action="b", detail="c"))
        writer.write("s2", AuditEntry(skill="a", action="b", detail="c"))

        sessions = writer.list_sessions()
        assert set(sessions) == {"s1", "s2"}

    def test_redacts_secrets_in_detail(self, tmp_audit_dir: Path) -> None:
        writer = AuditWriter(tmp_audit_dir)
        entry = AuditEntry(
            skill="test",
            action="leak_attempt",
            detail="Found key: sk-abc123def456ghi789jkl012mno345pqr678",
        )
        writer.write("session-redact", entry)

        entries = writer.read_session("session-redact")
        assert "sk-abc123" not in str(entries[0]["detail"])
        assert "REDACTED" in str(entries[0]["detail"])

    def test_empty_session(self, tmp_audit_dir: Path) -> None:
        writer = AuditWriter(tmp_audit_dir)
        entries = writer.read_session("nonexistent")
        assert entries == []
