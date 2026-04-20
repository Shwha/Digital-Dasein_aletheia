# Probe Manifests

This directory contains versioned, contributor-editable probe manifests.

Python dimension modules remain the canonical source for the existing benchmark
content, but Milestone 2 begins the migration toward external benchmark assets.
Manifest-backed probes can already be loaded by suites and executed by the
normal runner without editing engine internals.

## Layout

```text
benchmarks/probes/
└── v0.1/
    └── contributor-smoke.yaml
```

## Suite Integration

A suite can opt into manifest probes with:

```yaml
probe_manifest: v0.1/contributor-smoke.yaml
include_builtin_probes: false
include_reflexive_probes: false
```

Use `include_builtin_probes: true` to append manifest probes to the existing
Python-defined probes.

## Manifest Rules

- Probe IDs must stay stable once published.
- Probe IDs must follow `dimension.slug.number`, for example
  `care.manifest.1`.
- Each probe must declare a valid Aletheia dimension.
- Scoring rules use the same schema as Python-defined probes.
- Metadata is preserved into `ProbeResult.metadata` and report JSON.

## Validation

```bash
uv run aletheia validate-probes v0.1/contributor-smoke.yaml
uv run aletheia eval --model "$ALETHEIA_MODEL" --suite manifest-smoke
```

Contributor templates and review guidance live in `docs/contributors/`.
