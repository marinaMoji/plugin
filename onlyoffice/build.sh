#!/usr/bin/env bash
# Sync mapping.json and regenerate ONLYOFFICE plugin icons from marinaMoji logos.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MOZC="${ROOT}/../../../marinaMoji/src/unix/ibus/toolbar_icons"
LIGHT_SVG="${ROOT}/resources/light/logo_square_light.svg"
DARK_SVG="${ROOT}/resources/dark/logo_square_dark.svg"
IMG="${ROOT}/resources/img"

cp "${ROOT}/../mapping.json" "${ROOT}/mapping.json"

mkdir -p "${ROOT}/resources/light" "${ROOT}/resources/dark" "${IMG}"

if [[ ! -f "${LIGHT_SVG}" ]] && [[ -f "${MOZC}/logo_square_light.svg" ]]; then
  cp "${MOZC}/logo_square_light.svg" "${LIGHT_SVG}"
fi
if [[ ! -f "${DARK_SVG}" ]] && [[ -f "${MOZC}/logo_square_dark.svg" ]]; then
  cp "${MOZC}/logo_square_dark.svg" "${DARK_SVG}"
fi

if ! command -v rsvg-convert >/dev/null 2>&1; then
  echo "WARNING: install rsvg-convert (brew install librsvg) to rebuild icons"
  exit 0
fi

render_icon_set() {
  local svg="$1"
  local outdir="$2"
  [[ -f "${svg}" ]] || return 0
  rsvg-convert -w 32 -h 32 "${svg}" -o "${outdir}/icon.png"
  rsvg-convert -w 40 -h 40 "${svg}" -o "${outdir}/icon@1.25x.png"
  rsvg-convert -w 48 -h 48 "${svg}" -o "${outdir}/icon@1.5x.png"
  rsvg-convert -w 56 -h 56 "${svg}" -o "${outdir}/icon@1.75x.png"
  rsvg-convert -w 64 -h 64 "${svg}" -o "${outdir}/icon@2x.png"
  rsvg-convert -w 128 -h 128 "${svg}" -o "${outdir}/icon-sidebar.png"
  cp "${outdir}/icon.png" "${IMG}/icon.png"
  cp "${outdir}/icon@2x.png" "${IMG}/icon@2x.png"
  cp "${outdir}/icon-sidebar.png" "${IMG}/icon-sidebar.png"
}

render_icon_set "${LIGHT_SVG}" "${ROOT}/resources/light"
render_icon_set "${DARK_SVG}" "${ROOT}/resources/dark"

echo "Updated ONLYOFFICE plugin icons (light + dark, multi-scale)"
echo "Updated onlyoffice/mapping.json"
