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
osacompile -o "${OUT}" "${MAC}/install-word-addin.applescript"
cp "${MANIFEST}" "${OUT}/Contents/Resources/manifest.production.xml"
codesign --force --deep --sign - "${OUT}" 2>/dev/null || true
echo "Built ${OUT}"
