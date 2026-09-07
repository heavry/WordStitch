#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR="${WORDSTITCH_MODEL_DIR:-./models/wordstitch}"
PORT="${WORDSTITCH_PORT:-8080}"
mkdir -p "$MODEL_DIR"

curl -fL --retry 5 --retry-delay 2 \
  -o "$MODEL_DIR/WordStitch-4B-Q4_K_M.gguf" \
  "https://huggingface.co/heavry/WordStitch-4B/resolve/main/WordStitch-4B-Q4_K_M.gguf"

exec llama-server \
  -m "$MODEL_DIR/WordStitch-4B-Q4_K_M.gguf" \
  --host 127.0.0.1 \
  --port "$PORT" \
  -c 2048 \
  -ngl 99 \
  --jinja \
  --chat-template-kwargs '{"enable_thinking":false}' \
  --reasoning-budget 0

