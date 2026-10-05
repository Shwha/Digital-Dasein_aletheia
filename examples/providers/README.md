# Provider Examples

These examples show reproducible local workflows for hosted and local model
providers. They intentionally do not commit real secrets or provider-specific
model defaults.

## Pattern

1. Copy the relevant `.env.example` file.
2. Set your provider key or local endpoint.
3. Set `ALETHEIA_MODEL` to a LiteLLM model ID available to you.
4. Run the matching shell script with `bash`.

## Scripts

- `run-openai.sh`: hosted OpenAI-compatible run.
- `run-anthropic.sh`: hosted Anthropic-compatible run.
- `run-xai.sh`: hosted xAI/Grok-compatible run.
- `run-ollama.sh`: local Ollama run.
- `run-comparison.sh`: comma-separated multi-model comparison.

Outputs are written under `results/` unless `ALETHEIA_RESULTS_DIR` is set.

## Model Freshness

Choose an exact API model ID supported by the pinned LiteLLM version. Start
with `ALETHEIA_SUITE=manifest-smoke` (hosted) or `manifest-smoke-local` (local),
then inspect errors before running the built-in suite. `quick` and `standard`
currently execute the same built-in probes.

See [provider setup](../../docs/providers.md) and
[recorded model coverage](../../docs/model-status.md). These scripts do not
constitute test results for newly released models.
