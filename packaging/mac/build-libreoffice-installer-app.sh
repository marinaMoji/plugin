#!/usr/bin/env bash
# Build "Install marinaMoji Kaeriten (LibreOffice).app" for end users (macOS).
set -euo pipefail
MAC="$(cd "$(dirname "$0")" && pwd)"
PACKAGING="$(cd "${MAC}/.." && pwd)"
PLUGIN="$(cd "${PACKAGING}/.." && pwd)"
LO="${PLUGIN}/libreoffice"
OUT="${PACKAGING}/release/Install marinaMoji Kaeriten (LibreOffice).app"
OXT="${LO}/dist/MarinaMojiKaeriten.oxt"
SRC="${LO}/marinamoji_kaeriten"

if [[ ! -f "${OXT}" ]]; then
  (cd "${LO}" && ./build.sh)
fi

rm -rf "${OUT}"
osacompile -o "${OUT}" "${MAC}/install-libreoffice-extension.applescript"
RES="${OUT}/Contents/Resources"
cp "${OXT}" "${RES}/MarinaMojiKaeriten.oxt"
cp "${SRC}/marinamoji_kaeriten.py" "${SRC}/export_core.py" "${RES}/"
cp "${PLUGIN}/mapping.json" "${RES}/marinamoji_mapping.json"
cp "${MAC}/install-libreoffice-macos.sh" "${RES}/"
chmod +x "${RES}/install-libreoffice-macos.sh"
for f in MarinaMojiKaeriten.oxt marinamoji_kaeriten.py export_core.py install-libreoffice-macos.sh; do
  [[ -f "${RES}/${f}" ]] || { echo "ERROR: missing ${RES}/${f}"; exit 1; }
done
codesign --force --deep --sign - "${OUT}" 2>/dev/null || true
echo "Built ${OUT}"
