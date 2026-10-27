#!/bin/bash
# Install marinaMoji Kaeriten Python macros + .oxt for LibreOffice (macOS).
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
EXT_ID="org.marinaMoji.kaeriten"

if [[ ! -f "${OXT}" ]] || [[ ! -f "${MACRO}" ]]; then
  echo "Missing MarinaMojiKaeriten.oxt or marinamoji_kaeriten.py in ${RES}" >&2
  exit 1
fi

if pgrep -xq soffice || pgrep -xq soffice.bin 2>/dev/null; then
  echo "LibreOffice is still running. Quit Writer (Cmd+Q) and retry." >&2
  exit 2
fi

find_libreoffice_app() {
  local candidate
  for candidate in \
    "/Applications/LibreOffice.app" \
    "/Applications/LibreOffice Fresh.app" \
    "/Applications/LibreOffice Still.app" \
    "${HOME}/Applications/LibreOffice.app"
  do
    if [[ -x "${candidate}/Contents/MacOS/soffice" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done
  # Spotlight (works when the app lives outside /Applications)
  candidate="$(mdfind "kMDItemCFBundleIdentifier == 'org.libreoffice.script'" 2>/dev/null | head -1 || true)"
  if [[ -n "${candidate}" ]] && [[ -x "${candidate}/Contents/MacOS/soffice" ]]; then
    printf '%s\n' "${candidate}"
    return 0
  fi
  return 1
}

LO_APP=""
if ! LO_APP="$(find_libreoffice_app)"; then
  echo "LibreOffice was not found. Install LibreOffice from https://www.libreoffice.org/ then run this installer again." >&2
  exit 3
fi

UNOPKG="${LO_APP}/Contents/MacOS/unopkg"
if [[ ! -x "${UNOPKG}" ]]; then
  echo "LibreOffice is missing unopkg at ${UNOPKG}" >&2
  exit 3
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

echo "Copied Python macros to ${DEST}"
echo "Installing extension with ${LO_APP}…"

# Prefer unopkg: does not depend on Launch Services claiming .oxt
# (bare `open file.oxt` fails with kLSApplicationNotFoundErr when no handler is registered).
if ! "${UNOPKG}" add --force --suppress-license "${OXT}"; then
  echo "unopkg failed; trying open -a LibreOffice…" >&2
  if ! open -a "${LO_APP}" "${OXT}"; then
    echo "Could not install the .oxt extension (${EXT_ID})." >&2
    echo "Python macros were copied. Add the extension by hand:" >&2
    echo "  Tools → Extension Manager → Add → ${OXT}" >&2
    exit 4
  fi
fi

echo "Installed ${EXT_ID} from ${OXT}"
