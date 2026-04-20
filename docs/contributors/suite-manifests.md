# Suite Manifests

Suites live in `suites/` as YAML files. A suite controls which dimensions and
probe sources are used for an evaluation run.

## Core Fields

```yaml
name: manifest-smoke
description: "Manifest-backed contributor smoke suite"
dimensions:
  - unconcealment
  - care_structure
timeout_per_probe_seconds: 30
max_retries: 2
include_uci: false
include_builtin_probes: false
include_reflexive_probes: false
probe_manifest: v0.1/contributor-smoke.yaml
probe_ids:
  - care.manifest.1
```

## Composition Rules

- `include_builtin_probes: true` runs Python-defined probes for selected dimensions.
- `include_builtin_probes: false` creates a manifest-only suite.
- `include_reflexive_probes: false` disables built-in multi-turn probes.
- `probe_manifest` points to a file under `benchmarks/probes/` unless an absolute path is used.
- `probe_ids` narrows a manifest to specific stable probe IDs.
- `dimensions` filters both built-in probes and manifest-backed probes.

## Recommended Suite Types

- Smoke suite: 1 to 3 probes for contributor validation.
- Focus suite: one dimension or one failure mode.
- Release suite: documented benchmark card, stable probe IDs, signed baseline results.
- Experimental suite: clearly marked as draft and excluded from published comparisons.

## Validation

```bash
uv run aletheia validate-probes v0.1/contributor-smoke.yaml
uv run aletheia eval --model "$ALETHEIA_MODEL" --suite manifest-smoke
```

