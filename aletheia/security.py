"""
Security utilities for the Aletheia framework.

Ontological ground: Unconcealment (aletheia) demands that the framework
itself practice what it measures. No hidden state, no leaked secrets,
no fabricated trust. Security is not an add-on — it is constitutive of
the framework's own authenticity.

Threat model (SECURITY.md):
- The evaluated model may be adversarial or jailbroken
- Supply chain attacks on dependencies (ref: March 2026 LiteLLM incident)
- API key exposure through logs or reports
- Prompt injection via model responses

Ref: SCOPE.md §4 (Technical Architecture)
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import UTC
from pathlib import Path

import structlog
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

logger = structlog.get_logger()

ED25519_SIGNATURE_PREFIX = "ed25519:v1"


@dataclass(frozen=True)
class SignatureVerificationResult:
    """Result of verifying a report signature."""

    valid: bool
    scheme: str
    detail: str
    public_key: str | None = None


def get_git_commit_sha() -> str | None:
    """Retrieve current git commit SHA for audit trail.

    Returns None if not in a git repository or git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def set_restrictive_permissions(path: Path) -> None:
    """Set restrictive permissions on files and directories.

    Files use 0600 (owner read/write only). Directories use 0700 so they
    remain traversable by the owner while still denying access to others.
    On Windows, this is a best-effort operation.
    """
    if platform.system() != "Windows":
        mode = stat.S_IRUSR | stat.S_IWUSR
        if path.is_dir():
            mode |= stat.S_IXUSR
        path.chmod(mode)
    # Windows: rely on NTFS ACLs; no-op here but logged
    logger.debug("permissions_set", path=str(path), platform=platform.system())


def create_secure_directory(path: Path) -> Path:
    """Create a directory and restrict permissions when we create it.

    Existing parent directories may be shared system locations such as /tmp or
    user-selected project directories. Do not mutate their permissions while
    writing a secure report file.
    """
    existed = path.exists()
    path.mkdir(parents=True, exist_ok=True)
    if not existed:
        set_restrictive_permissions(path)
    return path


def write_secure_text(path: Path, content: str, encoding: str = "utf-8") -> Path:
    """Write text atomically with restrictive permissions.

    The file is written to a temporary sibling path and then replaced into
    position, avoiding partially-written reports and traces.
    """
    create_secure_directory(path.parent)

    fd, temp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=False,
    )
    temp_path = Path(temp_name)

    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        set_restrictive_permissions(temp_path)
        temp_path.replace(path)
        set_restrictive_permissions(path)
        return path
    except Exception:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("temp_cleanup_failed", path=str(temp_path))
        raise


def generate_run_id() -> str:
    """Generate a unique run ID for audit trail.

    Format: YYYYMMDD_HHMMSS_{random_hex}
    The timestamp gives human-readability; the hex prevents collisions.
    """
    from datetime import datetime

    now = datetime.now(UTC)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    random_hex = os.urandom(4).hex()
    return f"{timestamp}_{random_hex}"


def hash_content(content: str) -> str:
    """SHA-256 hash for content integrity verification."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _b64_encode(data: bytes) -> str:
    """Base64 encode bytes for compact signature transport."""
    return base64.b64encode(data).decode("ascii")


def _b64_decode(value: str) -> bytes:
    """Decode a base64 signature/key segment."""
    return base64.b64decode(value.encode("ascii"), validate=True)


def canonicalize_report_json(report_json: str) -> str:
    """Canonicalize a report JSON string before signing or verification.

    The signature field is always set to null before canonicalization so the
    signature never signs itself. Sorting keys makes verification independent of
    pretty-printing and dictionary ordering in generated JSON files.
    """
    raw = json.loads(report_json)
    if not isinstance(raw, dict):
        msg = "Report JSON must be an object."
        raise ValueError(msg)
    raw["signature"] = None
    return json.dumps(raw, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _load_ed25519_private_key(private_key_path: Path) -> ed25519.Ed25519PrivateKey:
    """Load an Ed25519 private key from PEM."""
    key = serialization.load_pem_private_key(
        private_key_path.read_bytes(),
        password=None,
    )
    if not isinstance(key, ed25519.Ed25519PrivateKey):
        msg = f"Signing key must be an Ed25519 private key: {private_key_path}"
        raise ValueError(msg)
    return key


def _public_key_to_b64(public_key: ed25519.Ed25519PublicKey) -> str:
    """Return the raw Ed25519 public key encoded as base64."""
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return _b64_encode(public_bytes)


def _load_ed25519_public_key(public_key_path: Path) -> ed25519.Ed25519PublicKey:
    """Load an Ed25519 public key from PEM."""
    key = serialization.load_pem_public_key(public_key_path.read_bytes())
    if not isinstance(key, ed25519.Ed25519PublicKey):
        msg = f"Verification key must be an Ed25519 public key: {public_key_path}"
        raise ValueError(msg)
    return key


def generate_ed25519_keypair(
    private_key_path: Path,
    public_key_path: Path | None = None,
) -> tuple[Path, Path]:
    """Generate and write an Ed25519 signing keypair."""
    public_path = public_key_path or private_key_path.with_suffix(f"{private_key_path.suffix}.pub")
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")

    write_secure_text(private_key_path, private_pem)
    write_secure_text(public_path, public_pem)
    return private_key_path, public_path


def sign_report(report_json: str, signing_key_path: str | Path | None = None) -> str | None:
    """Sign a JSON report for tamper detection.

    If a signing key path is configured, produce an Ed25519 signature that
    embeds the public key for self-contained verification. If no signing key is
    configured, fall back to the legacy SHA-256 integrity marker so reports
    remain backward-compatible and visibly unsigned.
    """
    canonical_report = canonicalize_report_json(report_json)
    if signing_key_path:
        private_key = _load_ed25519_private_key(Path(signing_key_path).expanduser())
        signature = private_key.sign(canonical_report.encode("utf-8"))
        public_key = _public_key_to_b64(private_key.public_key())
        return f"{ED25519_SIGNATURE_PREFIX}:{public_key}:{_b64_encode(signature)}"

    return f"sha256:{hash_content(canonical_report)}"


def _verify_legacy_sha256(signature: str, canonical_report: str) -> SignatureVerificationResult:
    """Verify the legacy unsigned SHA-256 integrity marker."""
    expected = f"sha256:{hash_content(canonical_report)}"
    valid = signature == expected
    detail = "Legacy SHA-256 integrity hash verified." if valid else "SHA-256 hash mismatch."
    return SignatureVerificationResult(valid, "sha256", detail)


def _verify_ed25519_signature(
    signature: str,
    canonical_report: str,
    public_key_path: Path | None,
) -> SignatureVerificationResult:
    """Verify an Ed25519 report signature."""
    parts = signature.split(":")
    if len(parts) != 4 or ":".join(parts[:2]) != ED25519_SIGNATURE_PREFIX:
        return SignatureVerificationResult(False, "unknown", "Unsupported signature format.")

    embedded_public_key_b64 = parts[2]
    signature_b64 = parts[3]

    try:
        signature_bytes = _b64_decode(signature_b64)
        embedded_public_key = ed25519.Ed25519PublicKey.from_public_bytes(
            _b64_decode(embedded_public_key_b64)
        )
        verification_key = (
            _load_ed25519_public_key(public_key_path) if public_key_path else embedded_public_key
        )
        verification_key_b64 = _public_key_to_b64(verification_key)
    except (OSError, ValueError) as e:
        return SignatureVerificationResult(False, "ed25519", f"Invalid key/signature data: {e}")

    if public_key_path and verification_key_b64 != embedded_public_key_b64:
        return SignatureVerificationResult(
            False,
            "ed25519",
            "Report signature public key does not match the supplied verification key.",
            public_key=embedded_public_key_b64,
        )

    try:
        verification_key.verify(signature_bytes, canonical_report.encode("utf-8"))
    except InvalidSignature:
        return SignatureVerificationResult(
            False,
            "ed25519",
            "Ed25519 signature mismatch.",
            public_key=embedded_public_key_b64,
        )

    return SignatureVerificationResult(
        True,
        "ed25519",
        "Ed25519 signature verified.",
        public_key=embedded_public_key_b64,
    )


def _extract_report_signature(
    report_json: str,
) -> tuple[str | None, SignatureVerificationResult | None]:
    """Extract the embedded signature from report JSON."""
    try:
        report_data = json.loads(report_json)
    except json.JSONDecodeError as e:
        return None, SignatureVerificationResult(False, "unknown", f"Invalid JSON: {e}")

    if not isinstance(report_data, dict):
        return None, SignatureVerificationResult(False, "unknown", "Report JSON must be an object.")

    signature = report_data.get("signature")
    if not isinstance(signature, str) or not signature:
        return None, SignatureVerificationResult(
            False,
            "unknown",
            "Report does not contain a signature.",
        )

    return signature, None


def verify_report_signature(
    report_json: str,
    public_key_path: Path | None = None,
) -> SignatureVerificationResult:
    """Verify a report signature embedded in the JSON report."""
    signature, extraction_error = _extract_report_signature(report_json)
    if extraction_error:
        return extraction_error
    if signature is None:
        return SignatureVerificationResult(False, "unknown", "Report does not contain a signature.")

    try:
        canonical_report = canonicalize_report_json(report_json)
    except ValueError as e:
        return SignatureVerificationResult(False, "unknown", str(e))

    if signature.startswith("sha256:"):
        return _verify_legacy_sha256(signature, canonical_report)

    return _verify_ed25519_signature(signature, canonical_report, public_key_path)


def verify_report_file(
    report_path: Path,
    public_key_path: Path | None = None,
) -> SignatureVerificationResult:
    """Verify a report file's embedded signature."""
    return verify_report_signature(report_path.read_text(encoding="utf-8"), public_key_path)


def scan_for_secrets(text: str) -> list[str]:
    """Scan text for accidentally included secrets.

    Phase 1 STUB: checks for common API key patterns.
    Phase 2 will use a more comprehensive ruleset.

    This runs on all report output before writing to disk — an agent that
    practices unconcealment about its limitations but conceals API keys.
    """
    import re

    findings: list[str] = []
    patterns = [
        (r"sk-[a-zA-Z0-9]{20,}", "Possible OpenAI API key detected"),
        (r"sk-ant-[a-zA-Z0-9-]{20,}", "Possible Anthropic API key detected"),
        (r"AIza[a-zA-Z0-9_-]{35}", "Possible Google API key detected"),
        (r"-----BEGIN.*PRIVATE KEY-----", "Possible private key detected"),
    ]
    for pattern, description in patterns:
        if re.search(pattern, text):
            findings.append(description)
    return findings


def create_audit_directory(base_path: Path, run_id: str, model_name: str) -> Path:
    """Create an audit directory for a specific run.

    Format: {base_path}/{run_id}_{model_name}/
    All audit files get restrictive permissions.
    """
    # Sanitize model name for filesystem safety
    safe_model = "".join(c if c.isalnum() or c in "-_" else "_" for c in model_name)
    return create_secure_directory(base_path / f"{run_id}_{safe_model}")
