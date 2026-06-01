#!/usr/bin/env bash
# Install marinaMoji Kaeriten into ONLYOFFICE Desktop Editors (macOS).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

# From config.json "guid": "asc.{…}" → folder name is {…} only (ONLYOFFICE docs).
PLUGIN_GUID="{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}"
SDK_PLUGINS="${HOME}/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/sdkjs-plugins"
DEST="${SDK_PLUGINS}/${PLUGIN_GUID}"

if pgrep -xq "ONLYOFFICE" 2>/dev/null || pgrep -xq "DesktopEditors" 2>/dev/null; then
  echo "WARNING: ONLYOFFICE appears to be running. Quit it (Cmd+Q), then run this script again."
  echo ""
fi

if [[ ! -d "${SDK_PLUGINS}" ]]; then
  echo "ONLYOFFICE plugins folder not found:"
  echo "  ${SDK_PLUGINS}"
  echo "Install ONLYOFFICE Desktop Editors first, open Writer once, then retry."
  exit 1
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
echo "Next: quit ONLYOFFICE (Cmd+Q), reopen Writer, open Plugins tab."
echo "Look for marinaMoji → marinaMoji Kaeriten (under Plugin Manager or Plugins list)."
echo ""
echo "Wrong path (does NOT work): .../plugins/marinamoji-kaeriten/"
echo "Correct path:             .../data/sdkjs-plugins/${PLUGIN_GUID}/"
