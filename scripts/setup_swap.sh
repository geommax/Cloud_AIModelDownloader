#!/usr/bin/env bash
set -euo pipefail

# Setup swap space on a cloud instance to prevent OOM kills
# during large model downloads.

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root (sudo)."
  exit 1
fi

SWAP_SIZE="${1:-8G}"
SWAP_FILE="/swapfile"

if swapon --show | grep -q "$SWAP_FILE"; then
  echo "Swap is already active at $SWAP_FILE"
  swapon --show
  exit 0
fi

echo "Creating ${SWAP_SIZE} swap file at ${SWAP_FILE} ..."
fallocate -l "$SWAP_SIZE" "$SWAP_FILE"
chmod 600 "$SWAP_FILE"
mkswap "$SWAP_FILE"
swapon "$SWAP_FILE"

# Persist across reboots
if ! grep -q "$SWAP_FILE" /etc/fstab; then
  echo "$SWAP_FILE none swap sw 0 0" >> /etc/fstab
fi

echo "Swap enabled:"
swapon --show
free -h
