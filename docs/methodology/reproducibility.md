# Reproducibility Runbook

This runbook describes the release workflow for rerunning and publishing
Aletheia baseline artifacts.

## 1. Validate Benchmark Assets

```bash
uv run aletheia validate-calibration
uv run aletheia validate-heldout
uv run aletheia validate-probes v0.1/contributor-smoke.yaml
uv run aletheia validate-baselines v0.1/manifest.yaml
```

`validate-calibration` reports the current corpus floor, maturity target,
remaining examples per dimension, probe-linked regression count, and
human-label-only count. Treat probe-linked examples as executable scorer
regressions and human-label-only examples as annotation evidence for future
scoring work.

Report JSON and markdown output include per-rule scores inside scoring details,
so partial-credit behavior can be audited without reverse-engineering the final
probe score.

Some high-value probes also opt into deterministic semantic aliases for common
paraphrases such as provenance, current-session context, verification
boundaries, bodily-care priority, session-memory boundaries, ambiguous-horizon
clarification, self-assessment fallibility, and context provenance. These
aliases are defined in code and reported through the same scoring evidence path;
they are not LLM-judge calls.

`validate-heldout` checks a separate held-out corpus for scorer
generalization. It reports exact label accuracy, a confusion matrix,
per-label precision/recall, clear-polarity accuracy, edge-label accuracy, mean
label distance, and borderline/ambiguous error examples. Treat this as
validation evidence, not calibration evidence: held-out examples should not be
used to tune matcher behavior unless they are explicitly moved into a future
calibration corpus version.

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
