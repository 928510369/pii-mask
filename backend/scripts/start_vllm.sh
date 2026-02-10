#!/bin/bash
# Start vLLM serving AdamLucek/Qwen3-4B-Instruct-2507-PII-RL locally
# Requires: pip install vllm>=0.8.5
# GPU recommended for best performance

echo "Starting vLLM server for AdamLucek/Qwen3-4B-Instruct-2507-PII-RL on port 8001..."
echo "This will download the model on first run (~10GB for 4B model)"
echo ""

vllm serve AdamLucek/Qwen3-4B-Instruct-2507-PII-RL \
  --port 8001 \
  --enable-reasoning \
  --reasoning-parser deepseek_r1 \
  --max-model-len 8192 \
  --dtype auto
