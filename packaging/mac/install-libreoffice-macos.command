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

set +e
bash "${SCRIPT}" "${RES}"
code=$?
set -e

if [[ "${code}" -ne 0 ]]; then
  if [[ "${code}" -eq 2 ]]; then
    osascript -e 'display alert "Quit LibreOffice first" message "Quit Writer completely (Cmd+Q), then run this installer again." as warning'
  elif [[ "${code}" -eq 3 ]]; then
    osascript -e 'display alert "LibreOffice not found" message "Install LibreOffice from https://www.libreoffice.org/ (or put LibreOffice.app in Applications), then run this installer again." as critical'
  elif [[ "${code}" -eq 4 ]]; then
    osascript -e 'display alert "Extension install failed" message "Python macros were copied. In LibreOffice use Tools → Extension Manager → Add and choose MarinaMojiKaeriten.oxt from this disk image." as critical'
  else
    osascript -e 'display alert "Install failed" message "Could not finish the LibreOffice install. Quit Writer and try again." as critical'
  fi
  exit "${code}"
fi

osascript <<'EOF'
display dialog "marinaMoji Kaeriten is ready for LibreOffice." & return & return & ¬
  "1. Restart Writer completely (Cmd+Q, then reopen)." & return & ¬
  "2. View → Toolbars → marinaMoji." buttons {"OK"} default button "OK" with title "Install complete"
EOF
