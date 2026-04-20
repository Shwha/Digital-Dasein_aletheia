# Contributor Guide

Aletheia contributors can now add benchmark content without editing engine
internals. The preferred path is to change versioned assets, validate them,
and let the runner load them through suite configuration.

## Fast Path

1. Copy `docs/contributors/probe-template.yaml` into `benchmarks/probes/v0.1/`.
2. Replace the example probe with your proposed probe.
3. Add or update a suite in `suites/` that points at the manifest.
4. Run `uv run aletheia validate-probes <manifest-ref>`.
5. Run `uv run pytest -q`.
6. Open a PR with the benchmark checklist completed.

## Contributor Assets

- `docs/contributors/probe-template.yaml`: valid starter manifest for new probes.
- `docs/contributors/suite-template.yaml`: valid starter suite that selects manifest probes.
- `docs/contributors/dimension-guide.md`: how to choose a dimension.
- `docs/contributors/rubric-template.md`: how to write reviewable scoring rules.
- `docs/contributors/benchmark-quality-bar.md`: acceptance bar for benchmark changes.
- `docs/contributors/probe-manifest-migration.md`: migration path from Python probes.
- `docs/contributors/suite-manifests.md`: suite fields and composition rules.

## Review Expectations

Probe contributions should name what they measure, what they cannot measure,
and how a reviewer can tell whether the scoring rules are too brittle.

Good contributions usually include:

- a stable probe ID
- a single primary dimension
- a natural prompt that does not reveal scoring internals
- phrase-family or pattern rules with evidence traces
- a Kantian limit that names the measurement boundary
- calibration examples when the probe introduces a new failure mode

## Validation Commands

```bash
uv run aletheia validate-probes v0.1/contributor-smoke.yaml
uv run aletheia eval --model "$ALETHEIA_MODEL" --suite manifest-smoke
uv run pytest -q
uv run ruff check .
uv run mypy aletheia
```

