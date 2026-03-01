#!/usr/bin/env bash
# Raspberry Pi first-time setup script
# Run this manually once on a fresh Pi before the first deployment.
# After this runs, subsequent deploys happen automatically via GitHub Actions.
#
# Usage (from your Mac, over SSH):
#   ssh pi@<pi-ip> 'bash -s' < pi_setup.sh
#
# Or copy and run directly on the Pi:
#   bash pi_setup.sh
set -euo pipefail

echo "=== Manga Tracker — Raspberry Pi Setup ==="
echo ""

# 1. Confirm architecture
ARCH=$(uname -m)
echo "Architecture: $ARCH"
if [ "$ARCH" != "aarch64" ]; then
  echo "WARNING: Expected aarch64 (Pi 4), got $ARCH"
fi

MODEL=$(cat /proc/device-tree/model 2>/dev/null || echo "unknown")
echo "Model: $MODEL"
echo ""

# 2. Update package list
echo "--- Updating packages ---"
sudo apt-get update -qq

# 3. Install Docker
if command -v docker &> /dev/null; then
  echo "✓ Docker already installed: $(docker --version)"
else
  echo "--- Installing Docker ---"
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER"
  echo "✓ Docker installed"
  echo "  NOTE: You need to log out and back in (or run 'newgrp docker') for group to take effect"
fi

# 4. Install Docker Compose plugin
if docker compose version &> /dev/null 2>&1; then
  echo "✓ Docker Compose already installed"
else
  echo "--- Installing Docker Compose plugin ---"
  sudo apt-get install -y -qq docker-compose-plugin
  echo "✓ Docker Compose installed"
fi

# 5. Install 1Password CLI
if command -v op &> /dev/null; then
  echo "✓ 1Password CLI already installed: $(op --version)"
else
  echo "--- Installing 1Password CLI ---"
  curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
    sudo gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg

  echo "deb [arch=arm64 signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] \
    https://downloads.1password.com/linux/debian/arm64 stable main" | \
    sudo tee /etc/apt/sources.list.d/1password.list > /dev/null

  sudo apt-get update -qq
  sudo apt-get install -y -qq 1password-cli
  echo "✓ 1Password CLI installed"
fi

# 6. Install curl (for health checks)
if ! command -v curl &> /dev/null; then
  sudo apt-get install -y -qq curl
fi

# 7. Create app directory
mkdir -p ~/manga-tracker/data
echo "✓ Created ~/manga-tracker/data"

# 8. Prompt for OP_SERVICE_ACCOUNT_TOKEN
echo ""
echo "=== 1Password Service Account Token ==="
echo "Create a service account at: https://developer.1password.com/docs/service-accounts/"
echo "Then add the token to your shell profile:"
echo ""
echo '  echo '"'"'export OP_SERVICE_ACCOUNT_TOKEN="ops_your_token_here"'"'"' >> ~/.bashrc'
echo "  source ~/.bashrc"
echo ""

if [ -z "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]; then
  echo "WARNING: OP_SERVICE_ACCOUNT_TOKEN is not set in this session."
  echo "Set it before running docker compose or the app won't start."
else
  echo "✓ OP_SERVICE_ACCOUNT_TOKEN is set in this session"
fi

# 9. Get Pi IP
PI_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "=== Setup Complete ==="
echo "Pi IP address: $PI_IP"
echo "After your first push to main, access the app at: http://$PI_IP:5000"
echo ""
echo "Next steps:"
echo "  1. Set OP_SERVICE_ACCOUNT_TOKEN in ~/.bashrc (see above)"
echo "  2. Add OP_SERVICE_ACCOUNT_TOKEN as a GitHub Actions secret"
echo "  3. Push to main — GitHub Actions will build and deploy automatically"
