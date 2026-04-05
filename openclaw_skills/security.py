"""Security utilities — audit, secret scanning, file permissions, run IDs.

Follows Aletheia's security model: no telemetry, no phone-home, restrictive
file permissions, secret scanning on all outputs, structured audit trail.
Every action is unconcealment — visible, traceable, honest.

Threat model considerations:
- API keys must never appear in logs, state files, or audit trails
- State files may contain sensitive context (file paths, code snippets)
- Model responses are untrusted data — sanitize before storage
- Dependency chain is pinned — no supply-chain drift
"""

from __future__ import annotations

import json
import os
import platform
import re
import secrets
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openclaw_skills.models import AuditEntry


# ---------------------------------------------------------------------------
# Run ID generation
# ---------------------------------------------------------------------------


def generate_run_id() -> str:
    """Generate a cryptographically random run ID.

    Uses secrets module (CSPRNG), not random module.
    """
    return secrets.token_hex(16)


# ---------------------------------------------------------------------------
# File permissions
# ---------------------------------------------------------------------------


def set_restrictive_permissions(path: Path) -> None:
    """Set file permissions to owner-only read/write (0600).

    On Windows, this uses NTFS ACL best-effort via icacls.
    On Unix, this uses standard chmod.
    """
    if platform.system() == "Windows":
        # NTFS: remove inherited permissions, grant owner full control only.
        # This is best-effort — NTFS ACLs are more complex than Unix perms.
        try:
            os.system(  # noqa: S605
                f'icacls "{path}" /inheritance:r /grant:r "%USERNAME%":F'
            )
        except OSError:
            pass  # Best-effort on Windows
    else:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600


def ensure_secure_directory(dir_path: Path) -> Path:
    """Create a directory with restrictive permissions if it doesn't exist.

    Returns the directory path for chaining.
    """
    dir_path.mkdir(parents=True, exist_ok=True)
    if platform.system() != "Windows":
        dir_path.chmod(stat.S_IRWXU)  # 0700 for directories
    return dir_path


# ---------------------------------------------------------------------------
# Secret scanning
# ---------------------------------------------------------------------------

# Patterns that indicate leaked secrets. These are intentionally broad —
# false positives are acceptable (we warn), false negatives are not.
_SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.ASCII),          # OpenAI keys
    re.compile(r"sk-ant-[a-zA-Z0-9\-]{20,}", re.ASCII),    # Anthropic keys
    re.compile(r"xai-[a-zA-Z0-9]{20,}", re.ASCII),         # xAI keys
    re.compile(r"AIza[a-zA-Z0-9\-_]{35}", re.ASCII),       # Google API keys
    re.compile(r"ghp_[a-zA-Z0-9]{36}", re.ASCII),          # GitHub PATs
    re.compile(r"gho_[a-zA-Z0-9]{36}", re.ASCII),          # GitHub OAuth
    re.compile(r"glpat-[a-zA-Z0-9\-]{20,}", re.ASCII),     # GitLab PATs
    re.compile(r"AKIA[A-Z0-9]{16}", re.ASCII),             # AWS access keys
    re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        re.ASCII,
    ),
    re.compile(r"Bearer [a-zA-Z0-9\-_.]{20,}", re.ASCII),  # Bearer tokens
    re.compile(r"token[\"']?\s*[:=]\s*[\"'][a-zA-Z0-9\-_.]{20,}[\"']", re.ASCII | re.IGNORECASE),
]


def scan_for_secrets(text: str) -> list[str]:
    """Scan text for potential leaked secrets.

    Returns a list of matched pattern descriptions. Empty list = clean.
    This is a defense-in-depth measure — the primary defense is SecretStr.
    """
    findings: list[str] = []
    for pattern in _SECRET_PATTERNS:
        if pattern.search(text):
            # Report the pattern name, NOT the matched value
            findings.append(f"Potential secret detected matching pattern: {pattern.pattern[:40]}...")
    return findings


# ---------------------------------------------------------------------------
# Input sanitization
# ---------------------------------------------------------------------------


# Control characters that should never appear in stored data.
# Keeps \n, \r, \t — strips everything else in C0/C1 ranges.
_CONTROL_CHAR_RE = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]"
)

# Maximum length for sanitized model responses (50KB — matches Aletheia)
MAX_RESPONSE_LENGTH = 50_000


def sanitize_text(text: str, max_length: int = MAX_RESPONSE_LENGTH) -> str:
    """Sanitize external text (model responses, tool outputs) for safe storage.

    - Strips control characters (except newline, carriage return, tab)
    - Enforces length limit to prevent memory exhaustion
    - Does NOT strip HTML/JS — that's the responsibility of the presentation layer
    """
    cleaned = _CONTROL_CHAR_RE.sub("", text)
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + f"\n[TRUNCATED at {max_length} chars]"
    return cleaned


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------


class AuditWriter:
    """Append-only audit trail writer.

    Writes JSONL (one JSON object per line) to the audit directory.
    Each session gets its own audit file. Files are created with
    restrictive permissions (0600).

    The audit trail IS unconcealment — it cannot be disabled, only
    configured for verbosity level.
    """

    def __init__(self, audit_dir: str | Path) -> None:
        self._audit_dir = ensure_secure_directory(Path(audit_dir))

    def write(self, session_id: str, entry: AuditEntry) -> None:
        """Append an audit entry to the session's audit log."""
        audit_file = self._audit_dir / f"{session_id}.jsonl"

        # Serialize — use model_dump for Pydantic v2
        record = entry.model_dump(mode="json")

        # Secret scan the serialized record
        record_str = json.dumps(record, default=str)
        findings = scan_for_secrets(record_str)
        if findings:
            # Redact the detail field if secrets found
            record["detail"] = "[REDACTED — secret detected in audit output]"
            record["_redaction_reason"] = findings[0]
            record_str = json.dumps(record, default=str)

        # Append atomically
        with audit_file.open("a", encoding="utf-8") as f:
            f.write(record_str + "\n")

        # Set permissions on first write
        set_restrictive_permissions(audit_file)

    def read_session(self, session_id: str) -> list[dict[str, object]]:
        """Read all audit entries for a session."""
        audit_file = self._audit_dir / f"{session_id}.jsonl"
        if not audit_file.exists():
            return []

        entries: list[dict[str, object]] = []
        for line in audit_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
        return entries

    def list_sessions(self) -> list[str]:
        """List all session IDs with audit trails."""
        return [
            p.stem
            for p in self._audit_dir.glob("*.jsonl")
            if p.is_file()
        ]


# ---------------------------------------------------------------------------
# Timestamp utilities
# ---------------------------------------------------------------------------


def utc_now() -> datetime:
    """Return current UTC datetime — always timezone-aware."""
    return datetime.now(timezone.utc)
