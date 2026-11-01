#!/usr/bin/env bash
# Build MarinaMojiKaeriten.oxt (toolbar) and stage macro files for install.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="${ROOT}/marinamoji_kaeriten"
DIST="${ROOT}/dist"
BUILD="${DIST}/build"
MODE="${1:-light}"
if [[ "${MODE}" != "light" && "${MODE}" != "dark" ]]; then
  echo "Usage: $0 [light|dark]" >&2
  exit 1
fi
OXT="${DIST}/MarinaMojiKaeriten.oxt"
if [[ "${MODE}" == "dark" ]]; then
  OXT="${DIST}/MarinaMojiKaeriten-dark.oxt"
fi
PLUGIN="$(cd "${ROOT}/.." && pwd)"

chmod +x "${ROOT}/build-icons.sh"
"${ROOT}/build-icons.sh"

rm -rf "${BUILD}"
mkdir -p "${BUILD}/Scripts/python" "${BUILD}/registration" "${BUILD}/description" "${BUILD}/images"
cp "${SRC}/description.xml" "${SRC}/Addons.xcu" "${SRC}/ProtocolHandler.xcu" "${SRC}/Jobs.xcu" \
   "${SRC}/MarinaMojiKaeriten.components" "${SRC}/marinamoji_kaeriten_dispatch.py" \
   "${SRC}/README.txt" "${BUILD}/"
cp -R "${SRC}/META-INF" "${BUILD}/"
if [[ -f "${SRC}/Office/UI/WriterWindowState.xcu" ]]; then
  mkdir -p "${BUILD}/Office/UI"
  cp "${SRC}/Office/UI/WriterWindowState.xcu" "${BUILD}/Office/UI/"
fi
cp "${SRC}/marinamoji_kaeriten.py" "${SRC}/export_core.py" "${SRC}/composer_handoff.py" \
   "${SRC}/warichu.py" "${SRC}/ruby.py" "${SRC}/emphasis.py" "${SRC}/typography_prefs.py" \
   "${SRC}/tatechuyoko.py" "${SRC}/typography_analysis.py" "${SRC}/typography_inspector.py" \
   "${SRC}/jidori.py" "${SRC}/jidori_math.py" "${SRC}/about.py" \
   "${BUILD}/Scripts/python/"
cp "${PLUGIN}/mapping.json" "${BUILD}/Scripts/python/marinamoji_mapping.json"
# Offline About guide (HTML + specimens + logo)
if [[ -d "${SRC}/help" ]]; then
  cp -R "${SRC}/help" "${BUILD}/"
fi

# License: keep registration/license_en.txt in sync with repo LICENSE
if [[ -f "${PLUGIN}/LICENSE" ]]; then
  cp "${PLUGIN}/LICENSE" "${BUILD}/registration/license_en.txt"
  cp "${PLUGIN}/LICENSE" "${SRC}/registration/license_en.txt"
elif [[ -f "${SRC}/registration/license_en.txt" ]]; then
  cp "${SRC}/registration/license_en.txt" "${BUILD}/registration/"
else
  echo "ERROR: missing GPL license text (plugin/LICENSE)" >&2
  exit 1
fi

cp "${SRC}/description/"*.txt "${BUILD}/description/"
if [[ -d "${SRC}/icons" ]] && compgen -G "${SRC}/icons/*" >/dev/null; then
  cp -R "${SRC}/icons" "${BUILD}/"
fi
if [[ "${MODE}" == "dark" ]]; then
  # LibreOffice add-on image URLs do not switch with the UI theme. Prepare
  # a separate package with light foregrounds on transparent backgrounds.
  python3 - "${BUILD}/icons" <<'PYCODE'
from pathlib import Path
import sys

for path in Path(sys.argv[1]).glob("*.svg"):
    text = path.read_text(encoding="utf-8")
    for old, new in (("#48484a", "#f2f2f7"), ("#005fef", "#75adff"),
                     ("#005ced", "#75adff"), ("#203758", "#f2f2f7")):
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
PYCODE
fi
if [[ -f "${SRC}/images/extension_icon.png" ]]; then
  cp "${SRC}/images/extension_icon.png" "${BUILD}/images/"
else
  echo "ERROR: missing images/extension_icon.png (run build-icons.sh)" >&2
  exit 1
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
  xattr -cr "${BUILD}" 2>/dev/null || true
fi

rm -f "${OXT}"
(cd "${BUILD}" && zip -r -q "${OXT}" .)
echo "Built ${OXT} (toolbar + Python in Scripts/python/)"
echo "Install: LibreOffice → Extension Manager → Add ${OXT} → restart Writer"
echo "Optional: ./install.sh copies macros to user profile (Macro dialog / APSO only)."
