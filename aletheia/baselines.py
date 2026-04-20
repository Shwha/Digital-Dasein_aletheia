"""
Baseline manifest and benchmark bundle utilities.

Milestone 3 turns Aletheia from a runnable evaluator into a reproducible
benchmark release surface. Baseline manifests describe what was run, how to
rerun it, and which signature policy applies to each published artifact.
Bundle manifests make benchmark releases auditable by hashing the assets that
define a release.
"""

from __future__ import annotations

import hashlib
import json
import shlex
from collections import Counter
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from aletheia import __version__
from aletheia.security import get_git_commit_sha, verify_report_file

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASELINES_DIR = _REPO_ROOT / "benchmarks" / "baselines"
DEFAULT_BUNDLE_PATHS = [
    "benchmarks/calibration",
    "benchmarks/probes",
    "benchmarks/baselines",
    "suites",
    "docs/benchmark-cards",
    "docs/methodology",
]


class BaselineProvider(StrEnum):
    """Supported provider classes for baseline manifest entries."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    XAI = "xai"
    OTHER = "other"


class BaselinePublicationStatus(StrEnum):
    """Publication state for a baseline run."""

    PLANNED = "planned"
    HISTORICAL = "historical"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class BaselineSignaturePolicy(StrEnum):
    """Expected signature scheme for a baseline report."""

    ED25519 = "ed25519"
    LEGACY_SHA256 = "legacy_sha256"
    NONE = "none"


class BaselineRun(BaseModel):
    """A single reproducible baseline run target."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_.-]+$")
    provider: BaselineProvider
    model: str = Field(min_length=1)
    suite: str = Field(min_length=1)
    family: str = Field(min_length=1)
    benchmark_card: str = Field(min_length=1)
    publication_status: BaselinePublicationStatus = BaselinePublicationStatus.PLANNED
    signature_policy: BaselineSignaturePolicy = BaselineSignaturePolicy.ED25519
    result_path: str | None = None
    expected_runtime_minutes: int | None = Field(default=None, ge=1, le=1440)
    audit: bool = False
    environment: dict[str, str] = Field(default_factory=dict)
    notes: str = ""

    @model_validator(mode="after")
    def validate_publication_state(self) -> BaselineRun:
        """Published runs must point at independently verifiable artifacts."""
        if self.publication_status == BaselinePublicationStatus.PUBLISHED:
            if self.result_path is None:
                msg = f"Published baseline {self.id} must include result_path."
                raise ValueError(msg)
            if self.signature_policy == BaselineSignaturePolicy.NONE:
                msg = f"Published baseline {self.id} must require a signature."
                raise ValueError(msg)
        return self


class BaselineManifest(BaseModel):
    """A versioned manifest for benchmark baseline runs."""

    model_config = ConfigDict(frozen=True)

    version: str = Field(pattern=r"^v\d+\.\d+$")
    description: str = Field(min_length=1)
    methodology: str = Field(min_length=1)
    runbook: str = Field(min_length=1)
    benchmark_bundle: str | None = None
    runs: list[BaselineRun] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_run_ids(self) -> BaselineManifest:
        """Baseline run IDs must be unique within a manifest."""
        seen: set[str] = set()
        duplicates: set[str] = set()
        for run in self.runs:
            if run.id in seen:
                duplicates.add(run.id)
            seen.add(run.id)
        if duplicates:
            msg = f"Duplicate baseline run IDs: {', '.join(sorted(duplicates))}"
            raise ValueError(msg)
        return self


class BaselineReportCheck(BaseModel):
    """Signature verification result for a baseline report artifact."""

    model_config = ConfigDict(frozen=True)

    run_id: str
    report_path: str | None
    exists: bool
    signature_valid: bool | None = None
    signature_scheme: str | None = None
    policy_satisfied: bool | None = None
    detail: str


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from disk and validate the top-level type."""
    if not path.exists():
        msg = f"Baseline manifest not found: {path}"
        raise FileNotFoundError(msg)

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Baseline manifest {path} must contain a YAML mapping, got {type(raw).__name__}"
        raise ValueError(msg)
    return raw


def resolve_baseline_manifest_path(
    manifest_ref: str,
    baselines_dir: Path | None = None,
) -> Path:
    """Resolve a baseline manifest reference to a concrete YAML path."""
    root = baselines_dir or DEFAULT_BASELINES_DIR
    path = Path(manifest_ref).expanduser()

    if path.is_absolute():
        return path
    if path.suffix in {".yaml", ".yml"}:
        if path.exists():
            return path
        return root / path
    return root / path / "manifest.yaml"


def load_baseline_manifest(
    manifest_ref: str = "v0.1/manifest.yaml",
    baselines_dir: Path | None = None,
) -> BaselineManifest:
    """Load and validate a baseline manifest."""
    manifest_path = resolve_baseline_manifest_path(manifest_ref, baselines_dir)
    return BaselineManifest(**_load_yaml_mapping(manifest_path))


def summarize_baseline_manifest(manifest: BaselineManifest) -> dict[str, Counter[str]]:
    """Summarize baseline coverage by provider, suite, and publication status."""
    return {
        "providers": Counter(run.provider.value for run in manifest.runs),
        "suites": Counter(run.suite for run in manifest.runs),
        "statuses": Counter(run.publication_status.value for run in manifest.runs),
        "signature_policies": Counter(run.signature_policy.value for run in manifest.runs),
    }


def _resolve_repo_path(path_ref: str, repo_root: Path) -> Path:
    """Resolve a repo-relative path unless the reference is absolute."""
    path = Path(path_ref).expanduser()
    return path if path.is_absolute() else repo_root / path


def _policy_satisfied(
    policy: BaselineSignaturePolicy,
    *,
    valid: bool,
    scheme: str,
) -> bool:
    """Return whether a verification result satisfies the manifest policy."""
    if policy == BaselineSignaturePolicy.NONE:
        return True
    if not valid:
        return False
    if policy == BaselineSignaturePolicy.ED25519:
        return scheme == "ed25519"
    if policy == BaselineSignaturePolicy.LEGACY_SHA256:
        return scheme == "sha256"
    return False


def check_baseline_reports(
    manifest: BaselineManifest,
    repo_root: Path | None = None,
) -> list[BaselineReportCheck]:
    """Verify baseline result artifacts that are referenced by a manifest."""
    root = repo_root or _REPO_ROOT
    checks: list[BaselineReportCheck] = []

    for run in manifest.runs:
        if run.result_path is None:
            checks.append(
                BaselineReportCheck(
                    run_id=run.id,
                    report_path=None,
                    exists=False,
                    detail="No result_path declared; run is not yet published.",
                )
            )
            continue

        report_path = _resolve_repo_path(run.result_path, root)
        if not report_path.exists():
            checks.append(
                BaselineReportCheck(
                    run_id=run.id,
                    report_path=str(report_path),
                    exists=False,
                    signature_valid=False,
                    policy_satisfied=False,
                    detail="Referenced report file does not exist.",
                )
            )
            continue

        if run.signature_policy == BaselineSignaturePolicy.NONE:
            checks.append(
                BaselineReportCheck(
                    run_id=run.id,
                    report_path=str(report_path),
                    exists=True,
                    policy_satisfied=True,
                    detail="Signature verification disabled by manifest policy.",
                )
            )
            continue

        result = verify_report_file(report_path)
        checks.append(
            BaselineReportCheck(
                run_id=run.id,
                report_path=str(report_path),
                exists=True,
                signature_valid=result.valid,
                signature_scheme=result.scheme,
                policy_satisfied=_policy_satisfied(
                    run.signature_policy,
                    valid=result.valid,
                    scheme=result.scheme,
                ),
                detail=result.detail,
            )
        )

    return checks


def validate_baseline_manifest(
    manifest: BaselineManifest,
    repo_root: Path | None = None,
) -> list[str]:
    """Return validation errors for paths and signature policies."""
    root = repo_root or _REPO_ROOT
    errors: list[str] = []

    for path_ref, label in (
        (manifest.methodology, "methodology"),
        (manifest.runbook, "runbook"),
    ):
        path = _resolve_repo_path(path_ref, root)
        if not path.exists():
            errors.append(f"{label} path does not exist: {path_ref}")

    if manifest.benchmark_bundle:
        bundle_path = _resolve_repo_path(manifest.benchmark_bundle, root)
        if not bundle_path.parent.exists():
            errors.append(f"benchmark_bundle parent does not exist: {bundle_path.parent}")

    for run in manifest.runs:
        card_path = _resolve_repo_path(run.benchmark_card, root)
        if not card_path.exists():
            errors.append(f"{run.id} benchmark_card does not exist: {run.benchmark_card}")

    for check in check_baseline_reports(manifest, root):
        if check.report_path is not None and not check.exists:
            errors.append(f"{check.run_id}: {check.detail}")
        if check.policy_satisfied is False:
            errors.append(f"{check.run_id}: signature policy not satisfied ({check.detail})")

    return errors


def render_baseline_commands(
    manifest: BaselineManifest,
    output_dir: Path = Path("results/baselines"),
) -> list[str]:
    """Render reproducible shell commands for every baseline run."""
    commands: list[str] = []
    for run in manifest.runs:
        output_path = output_dir / f"{run.id}.json"
        markdown_path = output_dir / f"{run.id}.md"
        command_parts = [
            "uv",
            "run",
            "aletheia",
            "eval",
            "--model",
            run.model,
            "--suite",
            run.suite,
            "--output",
            str(output_path),
            "--markdown",
            str(markdown_path),
        ]
        if run.audit:
            command_parts.append("--audit")

        command = " ".join(shlex.quote(part) for part in command_parts)
        if run.signature_policy == BaselineSignaturePolicy.ED25519:
            command = 'ALETHEIA_SIGNING_KEY_PATH="$ALETHEIA_SIGNING_KEY_PATH" ' + command

        commands.append(command)
    return commands


def _hash_file(path: Path) -> str:
    """Compute SHA-256 for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_bundle_files(paths: list[str], repo_root: Path) -> tuple[list[Path], list[str]]:
    """Collect files included in a bundle manifest."""
    files: list[Path] = []
    missing: list[str] = []

    for path_ref in paths:
        path = _resolve_repo_path(path_ref, repo_root)
        if not path.exists():
            missing.append(path_ref)
            continue
        if path.is_file():
            files.append(path)
            continue
        files.extend(item for item in path.rglob("*") if item.is_file())

    unique_files = sorted(set(files), key=lambda item: item.relative_to(repo_root).as_posix())
    return unique_files, missing


def create_benchmark_bundle_manifest(
    include_paths: list[str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Create a checksum manifest for benchmark release assets."""
    root = repo_root or _REPO_ROOT
    paths = include_paths or DEFAULT_BUNDLE_PATHS
    files, missing = _iter_bundle_files(paths, root)

    entries = [
        {
            "path": file_path.relative_to(root).as_posix(),
            "sha256": _hash_file(file_path),
            "size_bytes": file_path.stat().st_size,
        }
        for file_path in files
    ]

    return {
        "schema_version": "benchmark-bundle-manifest/v1",
        "aletheia_version": __version__,
        "git_commit_sha": get_git_commit_sha(),
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "include_paths": paths,
        "missing_paths": missing,
        "file_count": len(entries),
        "files": entries,
    }


def write_benchmark_bundle_manifest(
    output_path: Path,
    include_paths: list[str] | None = None,
    repo_root: Path | None = None,
) -> Path:
    """Write a benchmark bundle checksum manifest to disk."""
    bundle = create_benchmark_bundle_manifest(include_paths, repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path
