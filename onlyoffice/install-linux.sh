#!/usr/bin/env bash
# Install marinaMoji Kaeriten into ONLYOFFICE Desktop Editors (Linux).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

# From config.json "guid": "asc.{…}" → folder name is {…} only (ONLYOFFICE docs).
PLUGIN_GUID="{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}"
XDG_DATA_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}"

# Prefer the layout that already has Desktop Editors user data.
# Deb/RPM: ~/.local/share/onlyoffice/...
# Flatpak: ~/.var/app/org.onlyoffice.desktopeditors/... (path gained an extra
# "data/" segment in newer Desktop builds).
pick_sdk_plugins() {
  local candidates=(
    "${XDG_DATA_HOME}/onlyoffice/desktopeditors/sdkjs-plugins"
    "${HOME}/.var/app/org.onlyoffice.desktopeditors/data/onlyoffice/desktopeditors/data/sdkjs-plugins"
    "${HOME}/.var/app/org.onlyoffice.desktopeditors/data/onlyoffice/desktopeditors/sdkjs-plugins"
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ -d "$(dirname "${c}")" ]]; then
      echo "${c}"
      return 0
    fi
  done
  # Default for a fresh .deb install after the user has opened Desktop once.
  echo "${candidates[0]}"
}

SDK_PLUGINS="$(pick_sdk_plugins)"
DEST="${SDK_PLUGINS}/${PLUGIN_GUID}"

if pgrep -x "DesktopEditors" >/dev/null 2>&1 || \
   pgrep -f "onlyoffice-desktopeditors" >/dev/null 2>&1; then
  echo "WARNING: ONLYOFFICE appears to be running. Quit it, then run this script again."
  echo ""
fi

if [[ ! -d "${XDG_DATA_HOME}/onlyoffice" ]] && \
   [[ ! -d "${HOME}/.var/app/org.onlyoffice.desktopeditors" ]] && \
   [[ ! -x "$(command -v onlyoffice-desktopeditors || true)" ]] && \
   ! snap list onlyoffice-desktopeditors >/dev/null 2>&1 && \
   ! flatpak info org.onlyoffice.desktopeditors >/dev/null 2>&1; then
  echo "ONLYOFFICE not found. Install ONLYOFFICE Desktop Editors first, open a Document once, then retry."
  exit 1
fi

if [[ "${SDK_PLUGINS}" == *"/snap/"* ]] || snap list onlyoffice-desktopeditors >/dev/null 2>&1; then
  if [[ ! -d "$(dirname "${SDK_PLUGINS}")" ]]; then
    echo "Snap ONLYOFFICE detected. Install the plugin via Plugin Manager (.plugin file),"
    echo "or use the .deb / Flatpak build so this script can copy into a writable sdkjs-plugins folder."
    exit 1
  fi
fi

mkdir -p "${SDK_PLUGINS}"
"${ROOT}/build.sh"

mkdir -p "${DEST}"
# Only the files Desktop loads — not build/marketplace helper scripts.
# Protect composer_result.js (written by the IME, not in source) from --delete.
rsync -a --delete --delete-excluded \
  --filter 'P composer_result.js' \
  --exclude 'install-mac.sh' \
  --exclude 'install-linux.sh' \
  --exclude 'README.md' \
  --exclude 'CHANGELOG.md' \
  --exclude 'dist' \
  --exclude '.git' \
  --exclude 'build.sh' \
  --exclude 'validate-marketplace.sh' \
  --exclude 'export-marketplace.sh' \
  --exclude 'apply-marketplace-export.sh' \
  --exclude 'icon.png' \
  --exclude 'icon.svg' \
  "${ROOT}/" "${DEST}/"

echo ""
echo "Installed to:"
echo "  ${DEST}"
echo ""
echo "Plugin version: $(python3 -c "import json; print(json.load(open('${DEST}/config.json'))['version'])" 2>/dev/null || echo unknown)"
echo "Next: quit ONLYOFFICE, open a Document (not spreadsheet)."
echo "Ribbon → Plugins tab → marinaMoji (sidebar). Keep the panel open when inserting a composed character."
echo "Needs Desktop 9.3+, and a marinaMoji build that writes composer_result.js on Linux"
echo "(including Flatpak paths when Desktop Editors is installed that way)."
