#!/usr/bin/env bash
# Register the production Word manifest (GitHub Pages — no local dev server).
# macOS may refuse the copy into Word's folder; the script then shows you how to drag it in
# (see install-mac-lib.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=install-mac-lib.sh
source "${ROOT}/install-mac-lib.sh"
MANIFEST_URL="${MARINAMOJI_MANIFEST_URL:-https://marinamoji.github.io/plugin/marinamoji-kaeriten-word.xml}"
LOCAL_MANIFEST="${ROOT}/marinamoji-kaeriten-word.xml"
[[ -f "${LOCAL_MANIFEST}" ]] || LOCAL_MANIFEST="${ROOT}/../packaging/release/marinamoji-kaeriten-word.xml"

if [[ -f "${LOCAL_MANIFEST}" ]]; then
  SRC="${LOCAL_MANIFEST}"
  echo "Using the local production manifest: ${SRC}"
else
  SRC="$(mktemp -t marinamoji-word).xml"
  echo "Downloading ${MANIFEST_URL}"
  curl -fsSL "${MANIFEST_URL}" -o "${SRC}"
fi

echo ""
grep -m1 'SourceLocation DefaultValue' "${SRC}" | sed 's/^[[:space:]]*/  /' || true
install_manifest "${SRC}" || true

echo ""
echo "Next:"
echo "  1. Quit Word completely (Cmd+Q)."
echo "  2. Open Word with a document (internet required — no npm run serve)."
echo "  3. Accueil → Kaeriten → Kaeriten pane."
echo "     (or Insertion → Compléments → Mes compléments → Compléments de développeur → marinaMoji)"
