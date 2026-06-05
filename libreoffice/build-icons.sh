#!/usr/bin/env bash
# Rasterize plugin/icons/*.svg → marinamoji_kaeriten/icons/ for LibreOffice toolbar.
#
# Built-in Colibre toolbar art is 24×24 SVG; the *extension* API still loads bitmaps
# and scales them to the active toolbar size (16 / 26 / 32 px via ToolBox settings).
# Source SVGs are 32×32 — we rasterize at 32 (sharp downscale) and 26 (large-buttons mode).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
ICON_SRC="${ROOT}/../icons"
ICON_DST="${ROOT}/marinamoji_kaeriten/icons"

mkdir -p "${ICON_DST}"

if ! command -v rsvg-convert >/dev/null 2>&1; then
  echo "WARNING: install rsvg-convert (brew install librsvg) to rebuild toolbar icons" >&2
  exit 0
fi

render_lo_icon() {
  local svg_name="$1"
  local png_name="$2"
  local svg="${ICON_SRC}/${svg_name}"
  local png="${ICON_DST}/${png_name}"
  if [[ ! -f "${svg}" ]]; then
    echo "WARNING: missing ${svg}" >&2
    return 0
  fi
  cp "${svg}" "${ICON_DST}/${svg_name}"
  # ImageSmallURL — LO scales to current toolbar size (often 24–32 px on modern Writer)
  rsvg-convert -w 32 -h 32 "${svg}" -o "${png}"
  # ImageBigURL — “large toolbar buttons” slot (26×26 in LO; matches Colibre 24+1px margin)
  rsvg-convert -w 26 -h 26 "${svg}" -o "${png%.png}_big.png"
}

render_lo_icon render_kaeriten.svg render_kaeriten.png
render_lo_icon unrender_kaeriten.svg unrender_kaeriten.png
render_lo_icon export_txt.svg copy_plain_text.png
render_lo_icon export_xml.svg export_tei.png
render_lo_icon export_tex.svg export_latex.png
render_lo_icon toggle_page_writing_mode.svg toggle_page_writing_mode.png

echo "LibreOffice toolbar icons → ${ICON_DST} (32px + 26px PNG, SVG sources copied)"
