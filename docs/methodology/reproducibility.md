# Reproducibility Runbook

This runbook describes the release workflow for rerunning and publishing
Aletheia baseline artifacts.

## 1. Validate Benchmark Assets

```bash
uv run aletheia validate-calibration
uv run aletheia validate-probes v0.1/contributor-smoke.yaml
uv run aletheia validate-baselines v0.1/manifest.yaml
```

`validate-calibration` reports the current corpus floor, maturity target,
remaining examples per dimension, probe-linked regression count, and
human-label-only count. Treat probe-linked examples as executable scorer
regressions and human-label-only examples as annotation evidence for future
scoring work.

## 2. Prepare Signing

```bash
uv run aletheia keygen --private-key .aletheia/signing-key.pem
export ALETHEIA_SIGNING_KEY_PATH=.aletheia/signing-key.pem
```

Keep private keys out of commits and published bundles.

## 3. Generate Baseline Commands

```bash
uv run aletheia baseline-plan v0.1/manifest.yaml
```

Run the commands for the models available in your environment. For planned
hosted slots, replace placeholder model IDs with exact LiteLLM model IDs before
publication.

Some local Ollama baselines require longer per-probe timeouts than the default
suite setting. Use the exact command emitted by `baseline-plan`; those runtime
overrides are recorded in signed reports.

## 4. Verify Reports

```bash
uv run aletheia verify results/baselines/<run-id>.json \
  --public-key .aletheia/signing-key.pem.pub
```

## 5. Generate Bundle Manifest

```bash
uv run aletheia bundle-benchmark --output dist/benchmark-bundle-manifest.json
```

The bundle manifest records the files that define the benchmark release and
their SHA-256 hashes.
