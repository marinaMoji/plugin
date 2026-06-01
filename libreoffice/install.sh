#!/usr/bin/env bash
# Install marinaMoji Kaeriten Python macros into the LibreOffice user profile.
# Required on macOS LO 26.x: bundled Python in .oxt often fails to register (enable error).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="${ROOT}/marinamoji_kaeriten"

_find_lo_profile() {
  if [[ "$(uname -s)" == "Darwin" ]]; then
    local base="${HOME}/Library/Application Support/LibreOffice"
    if [[ -d "${base}/4/user" ]]; then
      echo "${base}/4/user"
      return
    fi
    local latest=""
    for d in "${base}"/*/user; do
      [[ -d "${d}" ]] || continue
      latest="${d}"
    done
    if [[ -n "${latest}" ]]; then
      echo "${latest}"
      return
    fi
    echo "${base}/4/user"
  else
    echo "${HOME}/.config/libreoffice/4/user"
  fi
}

LO_PROFILE="$(_find_lo_profile)"
LO_USER="${LO_PROFILE}/Scripts/python"
LO_PACK="${LO_PROFILE}/pack/Scripts/python"

if pgrep -xq soffice || pgrep -xq "soffice.bin" 2>/dev/null; then
  echo "WARNING: LibreOffice is running. Quit Writer completely, then run install.sh again."
  echo "         (Otherwise script cache .pack files may stay stale and macros fail to load.)"
  echo ""
fi

if [[ ! -f "${SRC}/marinamoji_kaeriten.py" ]]; then
  echo "ERROR: Source macro missing: ${SRC}/marinamoji_kaeriten.py"
  echo "       Run this script from the marinaMoji plugin: plugin/libreoffice/install.sh"
  exit 1
fi

mkdir -p "${LO_USER}"
cp "${SRC}/marinamoji_kaeriten.py" "${SRC}/export_core.py" "${LO_USER}/"
cp "${ROOT}/../mapping.json" "${LO_USER}/marinamoji_mapping.json"

if [[ ! -f "${LO_USER}/marinamoji_kaeriten.py" ]]; then
  echo "ERROR: Copy failed — expected:"
  echo "  ${LO_USER}/marinamoji_kaeriten.py"
  exit 1
fi

chmod 644 "${LO_USER}/marinamoji_kaeriten.py" "${LO_USER}/marinamoji_mapping.json"
if [[ "$(uname -s)" == "Darwin" ]]; then
  xattr -c "${LO_USER}/marinamoji_kaeriten.py" 2>/dev/null || true
  xattr -c "${LO_USER}/marinamoji_mapping.json" 2>/dev/null || true
fi

# Drop LO's compiled script cache so it reloads the .py (stale .pack → file open errors).
rm -f "${LO_PACK}/marinamoji_kaeriten.pack" "${LO_PACK}/marinamoji_mapping.pack" 2>/dev/null || true

echo "Installed macros to:"
echo "  ${LO_USER}/marinamoji_kaeriten.py"
echo "  ${LO_USER}/marinamoji_mapping.json"
ls -la "${LO_USER}/"
echo ""
echo "In Finder: Go → Go to Folder… (⌘⇧G), paste:"
echo "  ${LO_USER}"
echo ""
echo "Optional: macros are also in MarinaMojiKaeriten.oxt (toolbar uses ProtocolHandler)."
echo "Next: ./build.sh → Extension Manager → Add dist/MarinaMojiKaeriten.oxt → restart Writer."
