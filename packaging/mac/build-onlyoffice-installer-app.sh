#!/usr/bin/env bash
# Build "Install marinaMoji Kaeriten (ONLYOFFICE).app" for end users (macOS).
set -euo pipefail
MAC="$(cd "$(dirname "$0")" && pwd)"
PACKAGING="$(cd "${MAC}/.." && pwd)"
PLUGIN="$(cd "${PACKAGING}/.." && pwd)"
OO="${PLUGIN}/onlyoffice"
OUT="${PACKAGING}/release/Install marinaMoji Kaeriten (ONLYOFFICE).app"
BUNDLE="${OUT}/Contents/Resources/marinamoji-kaeriten-onlyoffice"

(cd "${OO}" && ./build.sh)

rm -rf "${OUT}"
osacompile -o "${OUT}" "${MAC}/install-onlyoffice-plugin.applescript"
mkdir -p "${BUNDLE}"
rsync -a --delete \
  --exclude 'install-mac.sh' \
  --exclude 'README.md' \
  --exclude '.DS_Store' \
  "${OO}/" "${BUNDLE}/"
cp "${MAC}/install-onlyoffice-macos.sh" "${OUT}/Contents/Resources/"
chmod +x "${OUT}/Contents/Resources/install-onlyoffice-macos.sh"

if [[ ! -f "${BUNDLE}/resources/light/icon.png" ]]; then
  echo "ERROR: ${BUNDLE}/resources/light/icon.png missing — run onlyoffice/build.sh first." >&2
  exit 1
fi
if ! grep -q '"name": "marinaMoji"' "${BUNDLE}/config.json"; then
  echo "ERROR: ${BUNDLE}/config.json has unexpected name — rebuild onlyoffice/ first." >&2
  exit 1
fi
PLUGIN_VERSION="$(python3 -c "import json; print(json.load(open('${BUNDLE}/config.json'))['version'])")"
echo "Bundled ONLYOFFICE plugin version: ${PLUGIN_VERSION}"

codesign --force --deep --sign - "${OUT}" 2>/dev/null || true
echo "Built ${OUT}"
