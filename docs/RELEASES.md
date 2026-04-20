# Release Process

This process keeps Aletheia releases reproducible, inspectable, and honest
about what the benchmark can claim.

## Release Types

- Engine release: Python package behavior changes.
- Benchmark release: probe, suite, calibration, or benchmark-card changes.
- Documentation release: contributor, methodology, provider, or release docs only.
- Security release: signing, verification, secret handling, dependency, or audit changes.

## Pre-Release Checklist

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run mypy aletheia
uv run pytest -q
uv build
```

For benchmark releases, also run:

```bash
uv run aletheia validate-calibration
uv run aletheia validate-probes v0.1/contributor-smoke.yaml
uv run aletheia validate-baselines v0.1/manifest.yaml
uv run aletheia bundle-benchmark --output dist/benchmark-bundle-manifest.json
```

## Benchmark Artifact Policy

- Benchmark reports intended for publication should be signed.
- New baseline reports intended for publication should use Ed25519 signatures.
- Historical reports without enforceable signatures must be labeled as historical.
- Report JSON should include model, suite, run ID, timestamp, commit SHA, and signature.
- Published results should link to benchmark cards and known limitations.
- Baselines should not be described as rankings unless the suite was designed for ranking.

## Release Notes

Each release note should include:

- what changed
- whether benchmark scores are expected to move
- migration steps for contributors
- known limitations
- validation commands run

## Tagging Guidance

Use package tags for engine releases and benchmark tags for content releases.

Examples:

- `v0.1.1`
- `benchmark-v0.1.1`
- `calibration-v0.1.1`
