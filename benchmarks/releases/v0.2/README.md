# Benchmark Release v0.2

This directory documents the intended v0.2 benchmark release bundle. The
machine-generated checksum manifest is produced during release with:

```bash
uv run aletheia bundle-benchmark --output dist/benchmark-bundle-manifest.json
```

## Included Asset Classes

- `benchmarks/calibration/`: labeled calibration corpus and annotation guide.
- `benchmarks/probes/`: external probe manifests.
- `benchmarks/baselines/`: baseline run manifest and rerun plan.
- `suites/`: suite YAML used by the runner.
- `docs/benchmark-cards/`: suite interpretation and known limitations.
- `docs/methodology/`: benchmark methodology and reproducibility note.

## Publication Policy

New release-grade baseline reports should be Ed25519 signed. Historical reports
with legacy SHA-256 integrity markers may be retained for continuity, but they
should not be presented as the final v0.2 leaderboard.

The current v0.2 manifest includes signed local Ollama quick-suite baselines,
signed hosted xAI quick-suite baselines, and signed smoke baselines. OpenAI and
Anthropic quick-suite baselines remain planned until maintainers run and sign
them under the release bundle.

## Release Gate

```bash
uv run ruff check .
uv run mypy aletheia
uv run pytest -q
uv run aletheia validate-calibration
uv run aletheia validate-probes v0.1/contributor-smoke.yaml
uv run aletheia validate-baselines v0.1/manifest.yaml
uv run aletheia bundle-benchmark --output dist/benchmark-bundle-manifest.json
uv build
```
