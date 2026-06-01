#!/usr/bin/env bash
# Build "Install marinaMoji Kaeriten.app" for Word (maintainers).
set -euo pipefail
MAC="$(cd "$(dirname "$0")" && pwd)"
PACKAGING="$(cd "${MAC}/.." && pwd)"
PLUGIN="$(cd "${PACKAGING}/.." && pwd)"
OUT="${PACKAGING}/release/Install marinaMoji Kaeriten.app"
MANIFEST="${PACKAGING}/release/marinamoji-kaeriten-word.xml"

if [[ ! -f "${MANIFEST}" ]]; then
  echo "Run with MARINAMOJI_PLUGIN_BASE set:"
  echo "  MARINAMOJI_PLUGIN_BASE=https://your-domain/word ${PACKAGING}/build-release.sh"
  exit 1
fi

rm -rf "${OUT}"
mkdir -p "${OUT}/Contents/Resources" "${OUT}/Contents/MacOS"
cp "${MANIFEST}" "${OUT}/Contents/Resources/manifest.production.xml"
osacompile -o "${OUT}/Contents/MacOS/applet" "${MAC}/install-word-addin.applescript"
/usr/bin/sed -i '' 's/applet/Install marinaMoji Kaeriten/' "${OUT}/Contents/Info.plist" 2>/dev/null || true
# Ad-hoc sign (optional; users may still Right-click → Open)
codesign --force --deep --sign - "${OUT}" 2>/dev/null || true
echo "Built ${OUT}"
