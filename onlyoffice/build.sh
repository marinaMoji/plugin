#!/usr/bin/env bash
# Sync mapping.json, regenerate icons, and package ONLYOFFICE .plugin for Plugin Manager.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DIST="${ROOT}/dist"
PLUGIN="${DIST}/marinamoji-kaeriten.plugin"
MOZC="${ROOT}/../../../marinaMoji/src/unix/ibus/toolbar_icons"
if [[ ! -d "${MOZC}" ]]; then
  MOZC="${ROOT}/../../../marinaMozc/src/unix/ibus/toolbar_icons"
fi
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
  echo "WARNING: install rsvg-convert (e.g. apt install librsvg2-bin) to rebuild icons"
else
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
  # Plugin Manager tile art: master icon.svg / icon.png at 240×120 (@2x).
  # ONLYOFFICE paints store.background behind a centered 120×60 logo overlay.
  # Strip the #203758 backdrop from tile icons so the header fills edge-to-edge.
  STORE_TILE_BG="#203758"
  store_icon_svg_no_bg() {
    local src="$1"
    local dest="$2"
    python3 - "${src}" "${dest}" <<'PY'
import re, sys
svg = open(sys.argv[1], encoding="utf-8").read()
svg = re.sub(r"<rect\b[^>]*\bid=\"rect1\"[^>]*/>", "", svg, count=1, flags=re.S)
open(sys.argv[2], "w", encoding="utf-8").write(svg)
PY
  }
  png_no_bg() {
    local src="$1"
    local dest="$2"
    python3 - "${src}" "${dest}" "${STORE_TILE_BG}" <<'PY'
import sys
from PIL import Image

src, dest, bg = sys.argv[1:4]
bg = tuple(int(bg[i:i+2], 16) for i in (1, 3, 5))
im = Image.open(src).convert("RGBA")
px = im.load()
w, h = im.size
for y in range(h):
    for x in range(w):
        r, g, b, a = px[x, y]
        if (r, g, b) == bg:
            px[x, y] = (r, g, b, 0)
im.save(dest)
PY
  }
  render_store_icon_set_from_svg() {
    local svg="$1"
    local outdir="$2"
    [[ -f "${svg}" ]] || return 0
    local tmp_svg="${outdir}/.tile_no_bg.svg"
    store_icon_svg_no_bg "${svg}" "${tmp_svg}"
    rsvg-convert -w 120 -h 60 "${tmp_svg}" -o "${outdir}/icon.png"
    rsvg-convert -w 150 -h 75 "${tmp_svg}" -o "${outdir}/icon@1.25x.png"
    rsvg-convert -w 180 -h 90 "${tmp_svg}" -o "${outdir}/icon@1.5x.png"
    rsvg-convert -w 210 -h 105 "${tmp_svg}" -o "${outdir}/icon@1.75x.png"
    rsvg-convert -w 240 -h 120 "${tmp_svg}" -o "${outdir}/icon@2x.png"
    cp "${tmp_svg}" "${outdir}/icon.svg"
    rm -f "${tmp_svg}"
  }
  render_store_icon_set_from_png() {
    local png="$1"
    local outdir="$2"
    [[ -f "${png}" ]] || return 0
    local tmp_png="${outdir}/.tile_no_bg.png"
    png_no_bg "${png}" "${tmp_png}"
    sips -z 60 120 "${tmp_png}" --out "${outdir}/icon.png" >/dev/null
    sips -z 75 150 "${tmp_png}" --out "${outdir}/icon@1.25x.png" >/dev/null
    sips -z 90 180 "${tmp_png}" --out "${outdir}/icon@1.5x.png" >/dev/null
    sips -z 105 210 "${tmp_png}" --out "${outdir}/icon@1.75x.png" >/dev/null
    cp "${tmp_png}" "${outdir}/icon@2x.png"
    rm -f "${tmp_png}"
  }
  mkdir -p "${ROOT}/resources/store/icons" "${ROOT}/resources/store/screenshots"
  if [[ -f "${ROOT}/icon.svg" ]]; then
    render_store_icon_set_from_svg "${ROOT}/icon.svg" "${ROOT}/resources/store/icons"
  elif [[ -f "${ROOT}/icon.png" ]]; then
    render_store_icon_set_from_png "${ROOT}/icon.png" "${ROOT}/resources/store/icons"
  else
    render_store_icon_set_from_svg "${MOZC}/logo_long_light.svg" "${ROOT}/resources/store/icons"
  fi
  rsvg-convert -w 1020 -h 228 \
    "${MOZC}/logo_long_light.svg" \
    -o "${ROOT}/resources/store/screenshots/logo_long_light.png"
  rsvg-convert -w 1020 -h 228 \
    "${MOZC}/logo_long_dark.svg" \
    -o "${ROOT}/resources/store/screenshots/logo_long_dark.png"
  if [[ -f "${ROOT}/icon.png" ]]; then
    cp "${ROOT}/icon.png" "${ROOT}/resources/store/screenshots/install.png"
    cp "${ROOT}/icon.png" "${ROOT}/resources/store/screenshots/uninstall.png"
  elif [[ -f "${ROOT}/icon.svg" ]]; then
    rsvg-convert -w 240 -h 120 \
      "${ROOT}/icon.svg" \
      -o "${ROOT}/resources/store/screenshots/install.png"
    cp "${ROOT}/resources/store/screenshots/install.png" \
      "${ROOT}/resources/store/screenshots/uninstall.png"
  else
    rsvg-convert -w 1280 -h 720 \
      "${ROOT}/resources/store/screenshots/install.svg" \
      -o "${ROOT}/resources/store/screenshots/install.png"
    rsvg-convert -w 1280 -h 720 \
      "${ROOT}/resources/store/screenshots/uninstall.svg" \
      -o "${ROOT}/resources/store/screenshots/uninstall.png"
  fi
  echo "Updated ONLYOFFICE plugin icons (light + dark, multi-scale)"
fi

echo "Updated onlyoffice/mapping.json"

mkdir -p "${DIST}"
rm -f "${PLUGIN}"
(
  cd "${ROOT}"
  zip -r -q "${PLUGIN}" \
    config.json index.html styles.css mapping.json scripts resources
)

echo "Built ${PLUGIN}"
echo "Install: ONLYOFFICE Writer → Plugins → Plugin Manager → My plugins → Install plugin manually"
