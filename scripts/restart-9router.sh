#!/usr/bin/env bash
# Restart 9Router service
# Usage: ./restart-9router.sh

set -euo pipefail

echo "Restarting 9Router..."
echo "  If 9Router is running ..."
if launchctl list | grep -q "ai.hermes.9router"; then
    launchctl kickstart -k gui/$(id -u)/ai.hermes.9router
    echo "  Done."
else
    echo "  9Router not running. Use launchctl load ~/Library/LaunchAgents/ai.hermes.9router.plist"
fi

echo ""
echo "Verify:"
echo "  curl http://127.0.0.1:20128/v1/models | head -20"
