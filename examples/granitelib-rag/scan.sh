#!/usr/bin/env bash
set -euo pipefail

REPO="ibm-granite/granitelib-rag-r1.0"
REVISION="2f0b2c79c6731068625aca8045c2eb2e8912b353"
ADAPTER_PATH="${1:-answerability/granite-4.0-micro/lora}"
CACHE_ROOT="${ADAPTERBILL_EXAMPLE_CACHE:-.cache/granitelib-rag-r1.0}"

uvx --from huggingface_hub hf download "$REPO" \
  --revision "$REVISION" \
  --include "$ADAPTER_PATH/*" \
  --local-dir "$CACHE_ROOT"

uv run adapterbill scan "$CACHE_ROOT/$ADAPTER_PATH" "${@:2}"
