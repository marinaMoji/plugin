#!/bin/bash
# Install marinaMoji Kaeriten plugin for ONLYOFFICE (macOS).
# Usage: install-onlyoffice-macos.sh /path/to/plugin-source-folder
set -euo pipefail

SRC="${1:?plugin source directory required}"
PLUGIN_GUID="{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}"
DEST_ROOT="${HOME}/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/sdkjs-plugins"
DEST="${DEST_ROOT}/${PLUGIN_GUID}"
OO_SUPPORT="${HOME}/Library/Application Support/asc.onlyoffice.ONLYOFFICE"
WRONG_PLUGIN="${OO_SUPPORT}/plugins/marinamoji-kaeriten"

if [[ ! -f "${SRC}/config.json" ]]; then
  echo "Missing config.json in ${SRC}" >&2
  exit 1
fi

if [[ ! -d "${OO_SUPPORT}" ]] && [[ ! -d "/Applications/ONLYOFFICE.app" ]]; then
  echo "ONLYOFFICE not found. Install Desktop Editors, open Writer once, then retry." >&2
  exit 2
fi

mkdir -p "${DEST_ROOT}"
if [[ -d "${WRONG_PLUGIN}" ]]; then
  rm -rf "${WRONG_PLUGIN}"
fi
rm -rf "${DEST}"
mkdir -p "${DEST}"
cp -R "${SRC}/"* "${DEST}/"
