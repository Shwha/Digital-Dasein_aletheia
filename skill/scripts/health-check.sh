#!/usr/bin/env bash
# Check if the OpenClawSkills pipeline server is running.
# Exit 0 if healthy, exit 1 if not.

set -euo pipefail

PORT="${OPENCLAW_SKILLS_PORT:-8901}"
URL="http://127.0.0.1:${PORT}/health"

response=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null || echo "000")

if [ "$response" = "200" ]; then
    echo "OpenClawSkills server is running on port $PORT"
    curl -s "$URL" | python3 -m json.tool 2>/dev/null || curl -s "$URL"
    exit 0
else
    echo "OpenClawSkills server is NOT running on port $PORT (HTTP $response)"
    echo "Start it with: openclaw-skills serve"
    exit 1
fi
