#!/usr/bin/env bash
# Build release artifacts for GitHub / website (maintainers only).
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "${PACKAGING}/.." && pwd)"
RELEASE="${PACKAGING}/release"
VERSION="${MARINAMOJI_RELEASE_VERSION:-dev}"

rm -rf "${RELEASE}"
mkdir -p "${RELEASE}"

echo "== LibreOffice .oxt"
(cd "${PLUGIN}/libreoffice" && ./build.sh)
cp "${PLUGIN}/libreoffice/dist/MarinaMojiKaeriten.oxt" "${RELEASE}/"

echo "== Word dist zip"
(cd "${PLUGIN}/word" && npm run build --silent 2>/dev/null || npm run build)
(cd "${PLUGIN}/word/dist" && zip -r -q "${RELEASE}/word-dist.zip" .)

if [[ -n "${MARINAMOJI_PLUGIN_BASE:-}" ]]; then
  echo "== Word production manifest"
  "${PACKAGING}/build-word-manifest.sh" "${RELEASE}/marinamoji-kaeriten-word.xml"
else
  echo "== Skip Word manifest (set MARINAMOJI_PLUGIN_BASE to generate)"
fi

echo "== ONLYOFFICE zip"
(cd "${PLUGIN}/onlyoffice" && ./build.sh)
(
  cd "${PLUGIN}/onlyoffice"
  zip -r -q "${RELEASE}/marinamoji-kaeriten-onlyoffice.zip" \
    config.json index.html styles.css mapping.json scripts resources
)

(
  cd "${RELEASE}"
  shasum -a 256 *.oxt *.zip *.xml 2>/dev/null > SHA256SUMS.txt || shasum -a 256 * > SHA256SUMS.txt || true
)

echo ""
echo "Release files in ${RELEASE}/ (version label: ${VERSION})"
ls -la "${RELEASE}"
