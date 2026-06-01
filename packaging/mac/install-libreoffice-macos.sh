#!/bin/bash
# Install marinaMoji Kaeriten Python macros for LibreOffice (macOS).
# Usage: install-libreoffice-macos.sh [Resources-folder]
set -euo pipefail

RES="$(cd "$(dirname "$0")" && pwd)"
if [[ $# -ge 1 ]] && [[ -n "${1}" ]]; then
  RES="$(cd "$1" && pwd)"
fi

OXT="${RES}/MarinaMojiKaeriten.oxt"
MACRO="${RES}/marinamoji_kaeriten.py"
EXPORT="${RES}/export_core.py"
MAPPING="${RES}/marinamoji_mapping.json"

if [[ ! -f "${OXT}" ]] || [[ ! -f "${MACRO}" ]]; then
  echo "Missing MarinaMojiKaeriten.oxt or marinamoji_kaeriten.py in ${RES}" >&2
  exit 1
fi

if pgrep -xq soffice || pgrep -xq soffice.bin 2>/dev/null; then
  echo "LibreOffice is still running. Quit Writer (Cmd+Q) and retry." >&2
  exit 2
fi

LO_BASE="${HOME}/Library/Application Support/LibreOffice"
LO_USER=""
if [[ -d "${LO_BASE}/4/user" ]]; then
  LO_USER="${LO_BASE}/4/user"
else
  for d in "${LO_BASE}"/*/user; do
    [[ -d "${d}" ]] && LO_USER="${d}"
  done
  [[ -z "${LO_USER}" ]] && LO_USER="${LO_BASE}/4/user"
fi

DEST="${LO_USER}/Scripts/python"
PACK="${LO_USER}/pack/Scripts/python"
mkdir -p "${DEST}"
cp "${MACRO}" "${EXPORT}" "${DEST}/"
[[ -f "${MAPPING}" ]] && cp "${MAPPING}" "${DEST}/marinamoji_mapping.json"
chmod 644 "${DEST}/marinamoji_kaeriten.py" "${DEST}/export_core.py" 2>/dev/null || true
xattr -c "${DEST}/marinamoji_kaeriten.py" 2>/dev/null || true
rm -f "${PACK}/marinamoji_kaeriten.pack" "${PACK}/marinamoji_mapping.pack" 2>/dev/null || true

open "${OXT}"
