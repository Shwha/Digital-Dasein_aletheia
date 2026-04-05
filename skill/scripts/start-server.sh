#!/usr/bin/env bash
# Start the OpenClawSkills pipeline server.
# Usage: ./start-server.sh [config]
# Default config: configs/default.yaml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Find the OpenClawSkills installation
INSTALL_DIR="${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/workspace/OpenClawSkills}"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "ERROR: OpenClawSkills not found at $INSTALL_DIR"
    echo "Set OPENCLAW_SKILLS_DIR or install to ~/.openclaw/workspace/OpenClawSkills"
    exit 1
fi

cd "$INSTALL_DIR"

# Activate venv if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

CONFIG="${1:-configs/default.yaml}"

echo "Starting OpenClawSkills pipeline server..."
echo "Config: $CONFIG"
echo "Install dir: $INSTALL_DIR"

exec openclaw-skills serve --config "$CONFIG"
