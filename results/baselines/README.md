# Baseline Results

This directory contains signed or historical baseline reports referenced by
`benchmarks/baselines/v0.1/manifest.yaml`.

Milestone 3 distinguishes three artifact classes:

- Signed publication artifacts: Ed25519-signed JSON reports that satisfy the
  baseline manifest policy. The Gemma local quick-suite reports are the first
  full local publication artifacts.
- Signed smoke artifacts: small manifest-backed runs that prove the publication
  workflow end to end, but should not be interpreted as full model rankings.
  The xAI/Grok smoke report also proves the hosted-provider path.
- Historical artifacts: older reports retained for continuity and clearly
  labeled in the baseline manifest.

Validate referenced artifacts with:

```bash
uv run aletheia validate-baselines v0.1/manifest.yaml
```
