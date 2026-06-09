#!/usr/bin/env bash
# Register the production Word manifest (GitHub Pages — no local dev server).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WEF="${HOME}/Library/Containers/com.microsoft.Word/Data/Documents/wef"
MANIFEST_URL="${MARINAMOJI_MANIFEST_URL:-https://marinamoji.github.io/plugin/marinamoji-kaeriten-word.xml}"
LOCAL_MANIFEST="${ROOT}/../packaging/release/marinamoji-kaeriten-word.xml"
DEST="${WEF}/marinamoji-kaeriten.xml"

mkdir -p "${WEF}"
rm -f "${WEF}"/*.xml "${WEF}"/*.manifest.xml 2>/dev/null || true

if [[ -f "${LOCAL_MANIFEST}" ]]; then
  cp "${LOCAL_MANIFEST}" "${DEST}"
  echo "Installed local production manifest:"
  echo "  ${LOCAL_MANIFEST}"
else
  echo "Downloading ${MANIFEST_URL}"
  curl -fsSL "${MANIFEST_URL}" -o "${DEST}"
  echo "Installed production manifest from GitHub Pages."
fi

echo "  → ${DEST}"
echo ""
grep -m1 'SourceLocation DefaultValue' "${DEST}" | sed 's/^[[:space:]]*/  /' || true
echo ""
echo "Next:"
echo "  1. Quit Word completely (Cmd+Q)."
echo "  2. Open Word with a document (internet required — no npm run serve)."
echo "  3. Accueil → Kaeriten → Kaeriten pane."
