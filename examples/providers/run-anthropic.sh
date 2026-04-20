#!/usr/bin/env bash
set -euo pipefail

: "${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY before running this example.}"
: "${ALETHEIA_MODEL:?Set ALETHEIA_MODEL to an Anthropic LiteLLM model ID.}"

SUITE="${ALETHEIA_SUITE:-quick}"
OUT_DIR="${ALETHEIA_RESULTS_DIR:-results/provider-anthropic}"
SAFE_MODEL="${ALETHEIA_MODEL//\//_}"

mkdir -p "$OUT_DIR"
uv run aletheia eval \
  --model "$ALETHEIA_MODEL" \
  --suite "$SUITE" \
  --output "$OUT_DIR/${SAFE_MODEL}-${SUITE}.json" \
  --markdown "$OUT_DIR/${SAFE_MODEL}-${SUITE}.md"

