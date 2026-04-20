# Baseline Manifests

Baseline manifests define the model runs that make up a benchmark release.
They are not only a list of scores. They are a rerun contract: model ID, suite,
provider class, expected artifact path, signature policy, benchmark card, and
methodology link.

## Validate The Baseline Manifest

```bash
uv run aletheia validate-baselines v0.1/manifest.yaml
```

## Print Reproducible Run Commands

```bash
uv run aletheia baseline-plan v0.1/manifest.yaml
```

Small local models may use `manifest-smoke-local`, which runs the same external
probe manifest as `manifest-smoke` with a longer timeout appropriate for Ollama.
Full local quick-suite baselines may also declare per-run timeout and retry
overrides in the manifest; `baseline-plan` renders those flags explicitly.

For Ed25519-signed publication runs, create or select a signing key first:

```bash
uv run aletheia keygen --private-key .aletheia/signing-key.pem
export ALETHEIA_SIGNING_KEY_PATH=.aletheia/signing-key.pem
uv run aletheia baseline-plan v0.1/manifest.yaml
```

## Status Labels

- `planned`: the run belongs in the release plan but has not been published.
- `historical`: an earlier report exists, but it may use legacy provenance.
- `published`: the report is release-grade and must satisfy its signature policy.
- `deprecated`: kept for context, not used for current comparisons.

## Signature Policies

- `ed25519`: required for new public baseline reports.
- `legacy_sha256`: accepted only for historical reports whose integrity marker still verifies.
- `none`: allowed only for planned, historical, or explicitly non-comparable artifacts.
