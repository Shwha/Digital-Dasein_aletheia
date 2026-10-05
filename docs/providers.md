# Provider Setup Examples

Aletheia uses LiteLLM model identifiers, so provider setup is mostly a matter
of setting the right environment variables and choosing the model ID available
to your account or local runtime.

The examples in `examples/providers/` are intentionally conservative: they
require you to choose the model ID instead of baking in names that may drift
over time.

## Selecting a Model

Use the exact API model ID and LiteLLM routing syntax supported by your provider.
The project pins `litellm==1.82.6`; compatibility with newly released models must
be checked with a smoke run before a full evaluation. Provider scripts are
setup examples, not evidence that every current model has been tested.

Start with `ALETHEIA_SUITE=manifest-smoke` for hosted models or
`ALETHEIA_SUITE=manifest-smoke-local` for slower local models. Inspect the
report for transport errors before interpreting scores: failed requests can
produce zero scores. `quick` currently executes the full built-in bundle.

See [recorded model coverage](model-status.md) before making claims about tested
models. Keep old report model IDs intact and publish new runs separately.

After copying an environment template below, edit its placeholder key and model
values before sourcing it. Keep provider environment files private and untracked.

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

## xAI/Grok-Compatible Hosted Models

```bash
cp examples/providers/xai.env.example .env.xai
set -a
source .env.xai
set +a
bash examples/providers/run-xai.sh
```

Required variables:

- `XAI_API_KEY`
- `ALETHEIA_MODEL`

Optional variables:

- `XAI_API_BASE`

Use the uppercase `XAI_API_KEY` spelling for shell exports. Aletheia also
normalizes the common dotenv spelling `xAI_API_Key` before handing the key to
LiteLLM, but release scripts and examples use the canonical uppercase name.

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

## macOS Keychain: xAI

Store the credential at a hidden prompt, keeping `-w` last:

```bash
security add-generic-password -a "$USER" -s "aletheia-xai-api-key" -w
```

The dedicated run script reads the credential through a captured subprocess,
without printing it or writing it to `.env`:

```bash
uv run python scripts/run_grok_keychain.py
```

This command makes paid requests: a two-probe smoke evaluation followed by the
full 83-request built-in run if the smoke phase has no transport errors. It
requires the existing `.aletheia/m3-baseline-signing-key.pem` and matching public
key, records provider usage/cost in a sidecar, uses 120-second request timeouts
and zero retries, and preserves provider-default reasoning and output limits.
A smoke score of zero does not by itself stop the run; request errors do.

When supplying a key programmatically to `AletheiaSettings`, pass
`XAI_API_KEY=SecretStr(key)`. Its validation aliases are `XAI_API_KEY` and
`xAI_API_Key`; passing `xai_api_key=` is ignored under the current settings
configuration. Verify the selected value matches the intended credential
without printing either value.

## Recorded Sol 6.1 Run

The local credential is stored in ignored `.env`. The evaluation runner does not
access Keychain:

```bash
uv run python scripts/run_sol_env.py
```

If a signed full report contains transport failures, recover only those failures
while preserving successful results:

```bash
uv run python scripts/recover_sol_transport.py PATH_TO_SIGNED_QUICK_JSON
```

Recovery produces a separate signed composite and usage sidecar; it never replaces
source reports. See [Sol findings](handoffs/sol-6.1-results.md) for the actual
completed run, cost accounting and limitations. Keep `.env` and its backups local.

## Recorded Opus 5.5 Run

Use the Anthropic key in ignored `.env`:

```bash
uv run python scripts/run_opus_env.py
```

The runner uses `anthropic/claude-opus-5-5`, smoke then full quick, 120-second
timeouts, zero retries, no tools, and provider/adapter defaults. The adapter
resolves a 128,000-token output limit. See [Opus findings](handoffs/opus-5.5-results.md)
for the signed results, usage-based cost estimate and cumulative vendor spend.
