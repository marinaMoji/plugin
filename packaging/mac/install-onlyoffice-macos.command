#!/bin/bash
# Double-click fallback installer for ONLYOFFICE (macOS). No .app bundle required.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="${DIR}/install-onlyoffice-macos.sh"
SRC="${DIR}/marinamoji-kaeriten-onlyoffice"

if [[ ! -f "${SRC}/config.json" ]]; then
  SRC="${DIR}/Install marinaMoji Kaeriten (ONLYOFFICE).app/Contents/Resources/marinamoji-kaeriten-onlyoffice"
fi
if [[ ! -f "${SCRIPT}" ]]; then
  SCRIPT="${DIR}/Install marinaMoji Kaeriten (ONLYOFFICE).app/Contents/Resources/install-onlyoffice-macos.sh"
fi
if [[ ! -f "${SRC}/config.json" ]]; then
  ZIP="${DIR}/marinamoji-kaeriten-onlyoffice.zip"
  if [[ -f "${ZIP}" ]]; then
    TMP="$(mktemp -d)"
    unzip -q "${ZIP}" -d "${TMP}"
    SRC="${TMP}"
  else
    osascript -e 'display alert "Files missing" message "Re-download marinamoji-kaeriten-onlyoffice-mac.dmg from GitHub Releases." as critical'
    exit 1
  fi
fi

if ! bash "${SCRIPT}" "${SRC}"; then
  code=$?
  if [[ "${code}" -eq 2 ]]; then
    osascript -e 'display alert "ONLYOFFICE not found" message "Install ONLYOFFICE Desktop Editors, open Writer once, then run this installer again." as critical'
  else
    osascript -e 'display alert "Install failed" message "Could not copy plugin files." as critical'
  fi
  exit "${code}"
fi

osascript <<'EOF'
display dialog "marinaMoji Kaeriten was installed for ONLYOFFICE." & return & return & ¬
  "1. Quit ONLYOFFICE completely (Cmd+Q)." & return & ¬
  "2. Reopen Writer." & return & ¬
  "3. Plugins → marinaMoji." buttons {"OK"} default button "OK" with title "Install complete"
EOF
