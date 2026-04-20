#!/usr/bin/env bash
set -euo pipefail

: "${ALETHEIA_MODELS:?Set ALETHEIA_MODELS to comma-separated LiteLLM model IDs.}"

SUITE="${ALETHEIA_SUITE:-quick}"
OUT_DIR="${ALETHEIA_RESULTS_DIR:-results/provider-comparison}"

mkdir -p "$OUT_DIR"
uv run aletheia compare \
  --models "$ALETHEIA_MODELS" \
  --suite "$SUITE" \
  --output "$OUT_DIR" \
  --markdown "$OUT_DIR/comparison.md"

