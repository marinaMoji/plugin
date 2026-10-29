#!/usr/bin/env bash
# Register the DEV manifest for Word on macOS (localhost HTTPS — npm run serve required).
# For GitHub Pages / production hosting use: ./install-mac-production.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=install-mac-lib.sh
source "${ROOT}/install-mac-lib.sh"
MANIFEST="${ROOT}/manifest.xml"

echo "DEV manifest (points at https://127.0.0.1:3000; needs npm run serve running)."
install_manifest "${MANIFEST}" || echo "(Finish the drag above, then continue below.)"
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
