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
- `run-ollama.sh`: local Ollama run.
- `run-comparison.sh`: comma-separated multi-model comparison.

Outputs are written under `results/` unless `ALETHEIA_RESULTS_DIR` is set.

