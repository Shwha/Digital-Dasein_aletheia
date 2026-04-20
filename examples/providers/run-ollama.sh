#!/usr/bin/env bash
set -euo pipefail

: "${ALETHEIA_MODEL:?Set ALETHEIA_MODEL to an Ollama LiteLLM model ID.}"

export OLLAMA_API_BASE="${OLLAMA_API_BASE:-http://localhost:11434}"

SUITE="${ALETHEIA_SUITE:-quick}"
OUT_DIR="${ALETHEIA_RESULTS_DIR:-results/provider-ollama}"
SAFE_MODEL="${ALETHEIA_MODEL//\//_}"

mkdir -p "$OUT_DIR"
uv run aletheia eval \
  --model "$ALETHEIA_MODEL" \
  --suite "$SUITE" \
  --output "$OUT_DIR/${SAFE_MODEL}-${SUITE}.json" \
  --markdown "$OUT_DIR/${SAFE_MODEL}-${SUITE}.md"

