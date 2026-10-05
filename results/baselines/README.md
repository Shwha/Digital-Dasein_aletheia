# Baseline Results

This directory contains signed or historical baseline reports referenced by
`benchmarks/baselines/v0.1/manifest.yaml`.

Milestone 3 distinguishes three artifact classes:

- Signed publication artifacts: Ed25519-signed JSON reports that satisfy the
  baseline manifest policy. The Gemma local quick-suite reports are the first
  full local publication artifacts; the Grok quick-suite reports are the first
  full hosted publication artifacts.
- Signed smoke artifacts: small manifest-backed runs that prove the publication
  workflow end to end, but should not be interpreted as full model rankings.
  The xAI/Grok smoke report also proves the hosted-provider path.
- Historical artifacts: older reports retained for continuity and clearly
  labeled in the baseline manifest.

Validate referenced artifacts with:

```bash
uv run aletheia validate-baselines v0.1/manifest.yaml
```

## Model Coverage and Freshness

The earlier checked-in runs are March–April 2026 snapshots. A signed
Grok 4.7 run from October 4, 2026 is now included. `published` denotes
artifact policy compliance, not that a model is current. OpenAI coverage now
includes Sol 6.1; Anthropic is still planned. Keep existing reports and manifest entries intact;
add new runs with exact model IDs, separate output paths, and matching runtime
settings. See [model coverage and refresh workflow](../../docs/model-status.md).

## Grok 4.7 Run

See [Grok 4.7 findings](../../docs/handoffs/grok-4.7-results-2026-10-04.md)
for the new signed smoke/full reports and exact provider billing. The
`20261004T191152Z` smoke files preserve a failed credential-injection attempt;
they are excluded from the baseline manifest and must not be interpreted as
model scores. The successful run uses the `20261004T191227Z` prefix.

## Sol 6.1 Run

[Sol findings](../../docs/handoffs/sol-6.1-results.md) describe the signed
`20261005T013727Z-recovered-quick` composite and the successful
`20261005T012235Z-smoke` report. Earlier failed/partial attempts and the first
recovery remain diagnostics, excluded from the manifest. The composite preserves
successful original results and reruns transport failures; its 0.7211 index
is based on 83 successful responses. Costs are usage-based estimates.
