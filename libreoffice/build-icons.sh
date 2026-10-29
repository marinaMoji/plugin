#!/usr/bin/env bash
# Copy plugin/icons/*.svg → marinamoji_kaeriten/icons/ for LibreOffice toolbar.
#
# Addons.xcu points ImageSmallURL / ImageBigURL at the same SVG; LO renders at
# the active toolbar size (sharp on HiDPI, same approach as Colibre).
# Extension Manager still wants a PNG in description.xml.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
ICON_SRC="${ROOT}/../icons"
ICON_DST="${ROOT}/marinamoji_kaeriten/icons"

mkdir -p "${ICON_DST}"

# Drop legacy toolbar PNGs so they are not packed into the .oxt by accident.
rm -f "${ICON_DST}"/*.png

copy_lo_icon() {
  local svg_name="$1"
  local svg="${ICON_SRC}/${svg_name}"
  if [[ ! -f "${svg}" ]]; then
    echo "WARNING: missing ${svg}" >&2
    return 0
  fi
  cp "${svg}" "${ICON_DST}/${svg_name}"
}

copy_lo_icon render_kaeriten.svg
copy_lo_icon unrender_kaeriten.svg
copy_lo_icon export_txt.svg
copy_lo_icon export_xml.svg
copy_lo_icon export_tex.svg
copy_lo_icon toggle_page_writing_mode.svg
copy_lo_icon apply_warichu.svg
copy_lo_icon remove_warichu.svg
copy_lo_icon apply_ruby.svg
copy_lo_icon remove_ruby.svg
copy_lo_icon apply_tatechuyoko.svg
copy_lo_icon remove_tatechuyoko.svg
copy_lo_icon apply_emphasis.svg
copy_lo_icon emphasis_menu.svg
copy_lo_icon remove_emphasis.svg

# Extension Manager icon (recommended 42×42 PNG in description.xml)
IMG_DST="${ROOT}/marinamoji_kaeriten/images"
mkdir -p "${IMG_DST}"
LOGO_CANDIDATES=(
  "${IMG_DST}/logo_square_light.svg"
  "${ROOT}/../onlyoffice/resources/img/logo_square_light.svg"
  "${ROOT}/../onlyoffice/resources/light/logo_square_light.svg"
)
LOGO=""
for candidate in "${LOGO_CANDIDATES[@]}"; do
  if [[ -f "${candidate}" ]]; then
    LOGO="${candidate}"
    break
  fi
done
if [[ -n "${LOGO}" ]]; then
  if ! command -v rsvg-convert >/dev/null 2>&1; then
    echo "WARNING: install rsvg-convert (brew install librsvg) for Extension Manager icon" >&2
  else
    if [[ "$(cd "$(dirname "${LOGO}")" && pwd)/$(basename "${LOGO}")" != \
          "$(cd "${IMG_DST}" && pwd)/logo_square_light.svg" ]]; then
      cp "${LOGO}" "${IMG_DST}/logo_square_light.svg"
    fi
    rsvg-convert -w 42 -h 42 "${LOGO}" -o "${IMG_DST}/extension_icon.png"
    echo "Extension Manager icon → ${IMG_DST}/extension_icon.png (42×42)"
  fi
else
  echo "WARNING: no logo_square_light.svg found for Extension Manager icon" >&2
fi

echo "LibreOffice toolbar icons → ${ICON_DST} (SVG)"
