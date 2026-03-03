#!/bin/bash
set -e

# Activate virtual environment
source /opt/hfdl/venv/bin/activate

echo "============================================"
echo "  HF Model Downloader CLI"
echo "============================================"
echo ""

# Check HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo "WARNING: HF_TOKEN is not set."
    echo "Set it in .env file or pass via -e HF_TOKEN=xxx"
    echo ""
fi

echo "Models directory: /models"
echo "Type 'hfdl --help' for usage info."
echo ""

# If args are passed, run hfdl directly; otherwise open a shell
if [ $# -gt 0 ]; then
    exec hfdl "$@"
else
    exec /bin/bash
fi
