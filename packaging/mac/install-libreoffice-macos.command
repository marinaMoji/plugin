#!/bin/bash
# Double-click fallback installer for LibreOffice (macOS). No .app bundle required.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="${DIR}/install-libreoffice-macos.sh"
RES="${DIR}"

if [[ ! -f "${RES}/MarinaMojiKaeriten.oxt" ]] || [[ ! -f "${RES}/marinamoji_kaeriten.py" ]]; then
  RES="${DIR}/Install marinaMoji Kaeriten (LibreOffice).app/Contents/Resources"
fi

if [[ ! -f "${SCRIPT}" ]]; then
  SCRIPT="${RES}/install-libreoffice-macos.sh"
fi

if [[ ! -f "${RES}/MarinaMojiKaeriten.oxt" ]]; then
  osascript -e 'display alert "Files missing" message "Re-download marinamoji-kaeriten-libreoffice-mac.dmg from GitHub Releases." as critical'
  exit 1
fi

if ! bash "${SCRIPT}" "${RES}"; then
  code=$?
  if [[ "${code}" -eq 2 ]]; then
    osascript -e 'display alert "Quit LibreOffice first" message "Quit Writer completely (Cmd+Q), then run this installer again." as warning'
  else
    osascript -e 'display alert "Install failed" message "Could not copy Python macros. Try again after quitting Writer." as critical'
  fi
  exit "${code}"
fi

osascript <<'EOF'
display dialog "marinaMoji Kaeriten is ready for LibreOffice." & return & return & ¬
  "1. In Extension Manager, click Add (if prompted) and accept." & return & ¬
  "2. Restart Writer completely." & return & ¬
  "3. View → Toolbars → marinaMoji." buttons {"OK"} default button "OK" with title "Install complete"
EOF
