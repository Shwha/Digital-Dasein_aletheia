# Provider Setup Examples

Aletheia uses LiteLLM model identifiers, so provider setup is mostly a matter
of setting the right environment variables and choosing the model ID available
to your account or local runtime.

The examples in `examples/providers/` are intentionally conservative: they
require you to choose the model ID instead of baking in names that may drift
over time.

## OpenAI-Compatible Hosted Models

```bash
cp examples/providers/openai.env.example .env.openai
set -a
source .env.openai
set +a
bash examples/providers/run-openai.sh
```

Required variables:

- `OPENAI_API_KEY`
- `ALETHEIA_MODEL`

## Anthropic-Compatible Hosted Models

```bash
cp examples/providers/anthropic.env.example .env.anthropic
set -a
source .env.anthropic
set +a
bash examples/providers/run-anthropic.sh
```

Required variables:

- `ANTHROPIC_API_KEY`
- `ALETHEIA_MODEL`

## Ollama Local Models

Start Ollama separately, pull the model you want to evaluate, then run:

```bash
cp examples/providers/ollama.env.example .env.ollama
set -a
source .env.ollama
set +a
bash examples/providers/run-ollama.sh
```

Required variables:

- `OLLAMA_API_BASE`
- `ALETHEIA_MODEL`

## Example Comparison Run

Use a comma-separated model list. The suite defaults to `quick`.

```bash
ALETHEIA_MODELS="model-a,model-b" \
ALETHEIA_SUITE=quick \
bash examples/providers/run-comparison.sh
```

Comparison outputs are written under `results/provider-comparison/` by default.

