#!/usr/bin/env bash
# Register the DEV manifest for Word on macOS (localhost HTTPS — npm run serve required).
# For GitHub Pages / production hosting use: ./install-mac-production.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WEF="${HOME}/Library/Containers/com.microsoft.Word/Data/Documents/wef"
MANIFEST="${ROOT}/manifest.xml"

mkdir -p "${WEF}"
rm -f "${WEF}"/*.xml "${WEF}"/*.manifest.xml 2>/dev/null || true
cp "${MANIFEST}" "${WEF}/marinamoji-kaeriten.xml"
echo "Copied DEV manifest (127.0.0.1:3000) to:"
echo "  ${WEF}/marinamoji-kaeriten.xml"
echo ""
echo "Production (GitHub Pages, no local server):"
echo "  ./install-mac-production.sh"
echo ""
echo "Next (dev):"
echo "  1. Quit Word completely (Cmd+Q)."
echo "  2. In another terminal: cd ${ROOT} && npm run serve"
echo "     (must stay running — fixes « Erreur relative au complément »)"
echo "  3. Open Word again and open a document."
echo "  4. Accueil → Kaeriten → Kaeriten pane"
