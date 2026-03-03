#!/usr/bin/env bash
set -euo pipefail

# Install Docker Engine on Debian 11 (bullseye)
# Reference: https://docs.docker.com/engine/install/debian/

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root (sudo)."
  exit 1
fi

apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

ARCH=$(dpkg --print-architecture)
CODENAME=$(lsb_release -cs)

cat >/etc/apt/sources.list.d/docker.list <<EOF
deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian ${CODENAME} stable
EOF

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now docker

echo "Docker installed successfully."

echo "If you want to run docker without sudo, run:"
if [[ -n "${SUDO_USER:-}" ]]; then
  echo "  sudo usermod -aG docker ${SUDO_USER}"
else
  echo "  sudo usermod -aG docker <your-username>"
fi
