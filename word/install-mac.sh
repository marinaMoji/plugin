#!/usr/bin/env bash
# Register the add-in manifest for Word on macOS (French or English UI).
# Word on Mac does NOT use Insert → Upload like Windows; it reads ~/.../wef/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WEF="${HOME}/Library/Containers/com.microsoft.Word/Data/Documents/wef"
MANIFEST="${ROOT}/manifest.xml"

mkdir -p "${WEF}"
rm -f "${WEF}"/*.xml "${WEF}"/*.manifest.xml 2>/dev/null || true
cp "${MANIFEST}" "${WEF}/marinamoji-kaeriten.xml"
echo "Copied manifest to:"
echo "  ${WEF}/marinamoji-kaeriten.xml"
echo ""
echo "Next:"
echo "  1. Quit Word completely (Cmd+Q)."
echo "  2. In another terminal: cd ${ROOT} && npm run start:server-only"
echo "     (must stay running — fixes « Erreur relative au complément »)"
echo "  3. Open Word again and open a document."
echo "  4. Ribbon: look for tab « marinaMoji », or"
echo "     Accueil → Compléments → marinaMoji Kaeriten"
