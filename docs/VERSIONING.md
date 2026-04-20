# Versioning Policy

Aletheia has two version surfaces: the engine and the benchmark content. They
move together when needed, but they should be reviewed separately.

## Engine Version

The Python package version in `pyproject.toml` follows semantic versioning.

- Patch: bug fixes, docs, tests, non-breaking reporting additions.
- Minor: new CLI commands, new optional fields, new scoring primitives.
- Major: breaking report schema, suite schema, or scoring semantics.

## Benchmark Content Version

Versioned benchmark assets live under directories such as:

```text
benchmarks/calibration/v0.1/
benchmarks/probes/v0.1/
```

Benchmark content versions should change when probe meaning changes, not only
when files move.

Baseline manifests are also benchmark content. Updating a baseline manifest can
be patch-level when it only adds a newly signed report for the same suite, but
it should be called out in release notes when it changes provider coverage,
signature policy, suite composition, or interpretation guidance.

## Stable IDs

Probe IDs are public benchmark API.

- Do not reuse a probe ID for a materially different prompt.
- Do not silently change scoring semantics under a published ID.
- Deprecate old IDs before removal.
- Preserve migrated Python probe IDs when moving them into manifests.

## Migration Rules

Use the smallest migration that keeps old reports interpretable.

- Metadata-only changes can stay in the same benchmark version.
- Prompt or scoring changes should create a new probe ID or benchmark version.
- Suite composition changes should be noted in the benchmark card.
- Removed probes should appear in release notes with a replacement if one exists.
- Historical baseline artifacts should remain labeled historical until rerun
  under the current signing and bundle policy.

## Compatibility Expectations

- Old signed reports should remain verifiable.
- New report fields should be additive where possible.
- Suite YAML should prefer explicit `probe_ids` for release suites.
- Contributor smoke suites can change faster than published benchmark suites.
