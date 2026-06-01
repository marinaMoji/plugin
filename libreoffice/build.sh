#!/usr/bin/env bash
# Build MarinaMojiKaeriten.oxt (menu) and stage macro files for install.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="${ROOT}/marinamoji_kaeriten"
DIST="${ROOT}/dist"
BUILD="${DIST}/build"
OXT="${DIST}/MarinaMojiKaeriten.oxt"

rm -rf "${BUILD}"
mkdir -p "${BUILD}/Scripts/python"
cp "${SRC}/description.xml" "${SRC}/Addons.xcu" "${SRC}/ProtocolHandler.xcu" \
   "${SRC}/MarinaMojiKaeriten.components" "${SRC}/marinamoji_kaeriten_dispatch.py" \
   "${SRC}/README.txt" "${BUILD}/"
cp -R "${SRC}/META-INF" "${BUILD}/"
cp "${SRC}/marinamoji_kaeriten.py" "${SRC}/export_core.py" "${BUILD}/Scripts/python/"
cp "${ROOT}/../mapping.json" "${BUILD}/Scripts/python/marinamoji_mapping.json"

if [[ "$(uname -s)" == "Darwin" ]]; then
  xattr -cr "${BUILD}" 2>/dev/null || true
fi

rm -f "${OXT}"
(cd "${BUILD}" && zip -r -q "${OXT}" .)
echo "Built ${OXT} (toolbar + Python in Scripts/python/)"
echo "Install: LibreOffice → Extension Manager → Add ${OXT} → restart Writer"
echo "Optional: ./install.sh copies macros to user profile (Macro dialog / APSO only)."
