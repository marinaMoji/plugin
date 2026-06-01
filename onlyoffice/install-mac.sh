#!/usr/bin/env bash
# Install marinaMoji Kaeriten into ONLYOFFICE Desktop Editors (macOS).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

# From config.json "guid": "asc.{…}" → folder name is {…} only (ONLYOFFICE docs).
PLUGIN_GUID="{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}"
SDK_PLUGINS="${HOME}/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/sdkjs-plugins"
DEST="${SDK_PLUGINS}/${PLUGIN_GUID}"
OO_SUPPORT="${HOME}/Library/Application Support/asc.onlyoffice.ONLYOFFICE"
# Old installers copied here — ONLYOFFICE may load this stale copy instead of the GUID folder.
WRONG_PLUGIN="${OO_SUPPORT}/plugins/marinamoji-kaeriten"

if pgrep -xq "ONLYOFFICE" 2>/dev/null || pgrep -xq "DesktopEditors" 2>/dev/null; then
  echo "WARNING: ONLYOFFICE appears to be running. Quit it (Cmd+Q), then run this script again."
  echo ""
fi

if [[ ! -d "${OO_SUPPORT}" ]] && [[ ! -d "/Applications/ONLYOFFICE.app" ]]; then
  echo "ONLYOFFICE not found. Install ONLYOFFICE Desktop Editors first, open Writer once, then retry."
  exit 1
fi

mkdir -p "${SDK_PLUGINS}"

if [[ -d "${WRONG_PLUGIN}" ]]; then
  echo "Removing old plugin copy at wrong path:"
  echo "  ${WRONG_PLUGIN}"
  rm -rf "${WRONG_PLUGIN}"
fi

"${ROOT}/build.sh"

mkdir -p "${DEST}"
rsync -a --delete \
  --exclude 'install-mac.sh' \
  --exclude 'README.md' \
  "${ROOT}/" "${DEST}/"

echo ""
echo "Installed to:"
echo "  ${DEST}"
echo ""
echo "Plugin version: $(python3 -c "import json; print(json.load(open('${DEST}/config.json'))['version'])" 2>/dev/null || echo unknown)"
echo "Next: quit ONLYOFFICE (Cmd+Q), reopen Writer, open Plugins tab."
echo "Look for marinaMoji in the Plugins tab (Plugin Manager → My plugins)."
echo ""
echo "Wrong path (does NOT work): .../plugins/marinamoji-kaeriten/"
echo "Correct path:             .../data/sdkjs-plugins/${PLUGIN_GUID}/"
