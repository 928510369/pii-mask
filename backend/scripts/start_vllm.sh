#!/bin/bash
# Start vLLM serving Qwen3-0.6B locally
# Requires: pip install vllm>=0.8.5
# GPU recommended for best performance

echo "Starting vLLM server for Qwen3-0.6B on port 8001..."
echo "This will download the model on first run (~1.2GB)"
echo ""

vllm serve Qwen/Qwen3-0.6B \
  --port 8001 \
  --enable-reasoning \
  --reasoning-parser deepseek_r1 \
  --max-model-len 8192 \
  --dtype auto
