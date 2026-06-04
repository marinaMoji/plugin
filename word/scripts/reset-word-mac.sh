#!/usr/bin/env bash
# Clear sideloaded manifests so Word reloads the latest manifest + URLs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEF="${HOME}/Library/Containers/com.microsoft.Word/Data/Documents/wef"

echo "Removing old Word sideload manifests from:"
echo "  ${WEF}"
rm -f "${WEF}"/*.xml "${WEF}"/*.manifest.xml 2>/dev/null || true

"${ROOT}/install-mac.sh"

echo ""
echo "Done. Quit Word completely (Cmd+Q), then:"
echo "  npm run serve"
echo "  Open Word → Compléments → marinaMoji Kaeriten"
