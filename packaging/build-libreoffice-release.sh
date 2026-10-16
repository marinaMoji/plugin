#!/usr/bin/env bash
# Build LibreOffice-only release artifacts (no Word / ONLYOFFICE rebuild).
# Writes a reviewable update-feed XML under packaging/release-libreoffice/.
# Does NOT modify live GitHub Pages (pages/ on main) unless you copy/commit it later.
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "${PACKAGING}/.." && pwd)"
RELEASE="${PACKAGING}/release-libreoffice"
LO="${PLUGIN}/libreoffice"
LO_XML="${LO}/marinamoji_kaeriten/description.xml"
LO_VER="$(sed -n 's/.*<version value="\([^"]*\)".*/\1/p' "${LO_XML}" | head -1)"
TAG="${MARINAMOJI_RELEASE_TAG:-libreoffice-v${LO_VER}}"
REPO="${MARINAMOJI_GITHUB_REPO:-${GITHUB_REPOSITORY:-marinaMoji/plugin}}"
OXT_URL="https://github.com/${REPO}/releases/download/${TAG}/MarinaMojiKaeriten.oxt"

rm -rf "${RELEASE}"
mkdir -p "${RELEASE}"

echo "== LibreOffice version ${LO_VER} (tag ${TAG})"
chmod +x "${LO}/build.sh" "${LO}/validate-extension.sh" 2>/dev/null || true

echo "== Unit tests"
python3 "${LO}/tests/test_parser.py"
python3 "${LO}/tests/test_export.py"

echo "== Build .oxt"
(cd "${LO}" && ./build.sh)
cp "${LO}/dist/MarinaMojiKaeriten.oxt" "${RELEASE}/"

echo "== Validate package"
(cd "${LO}" && ./validate-extension.sh "${RELEASE}/MarinaMojiKaeriten.oxt")

echo "== Generate reviewable update feed (not deployed)"
cat > "${RELEASE}/MarinaMojiKaeriten.update.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<description xmlns="http://openoffice.org/extensions/update/2006"
             xmlns:xlink="http://www.w3.org/1999/xlink"
             xmlns:lo="http://libreoffice.org/extensions/description/2011"
             xmlns:d="http://openoffice.org/extensions/description/2006">
  <identifier value="org.marinaMoji.kaeriten"/>
  <version value="${LO_VER}"/>
  <update-download>
    <src xlink:href="${OXT_URL}"/>
  </update-download>
  <publisher>
    <name xlink:href="https://github.com/${REPO}" lang="en">marinaMoji</name>
  </publisher>
  <dependencies>
    <lo:LibreOffice-minimal-version value="6.4" d:name="LibreOffice 6.4"/>
  </dependencies>
</description>
EOF

python3 - "${RELEASE}/MarinaMojiKaeriten.update.xml" "${LO_VER}" "${OXT_URL}" <<'PY'
import sys
import xml.etree.ElementTree as ET

path, lo_ver, expect = sys.argv[1:4]
NS = {"u": "http://openoffice.org/extensions/update/2006"}
root = ET.parse(path).getroot()
ver = root.find("u:version", NS).get("value")
href = root.find("u:update-download/u:src", NS).get("{http://www.w3.org/1999/xlink}href")
assert ver == lo_ver, f"feed version {ver} != {lo_ver}"
assert href == expect, f"feed URL got {href!r} expected {expect!r}"
assert "/latest/" not in href, "refusing /latest/ download URL"
print(f"OK: update feed version={ver}")
print(f"OK: update-download={href}")
PY

# Optional companion channel snippet for maintainers (does not write pages/)
cat > "${RELEASE}/version-snippet.json" <<EOF
{
  "libreoffice": "${LO_VER}",
  "release_tag": "${TAG}",
  "oxt_url": "${OXT_URL}",
  "update_feed_url": "https://marinamoji.github.io/plugin/MarinaMojiKaeriten.update.xml"
}
EOF

if [[ "$(uname -s)" == "Darwin" ]] && [[ "${MARINAMOJI_BUILD_LO_DMG:-1}" == "1" ]]; then
  echo "== macOS LibreOffice DMG (optional)"
  chmod +x "${PACKAGING}/mac/"*.sh 2>/dev/null || true
  mkdir -p "${PACKAGING}/release"
  cp "${RELEASE}/MarinaMojiKaeriten.oxt" "${PACKAGING}/release/"
  if [[ -x "${PACKAGING}/mac/build-libreoffice-installer-app.sh" ]]; then
    "${PACKAGING}/mac/build-libreoffice-installer-app.sh" || echo "WARNING: LO installer app build failed"
  fi
  if [[ -x "${PACKAGING}/mac/build-libreoffice-dmg.sh" ]]; then
    "${PACKAGING}/mac/build-libreoffice-dmg.sh" || echo "WARNING: LO DMG build failed"
  fi
  if [[ -f "${PACKAGING}/release/marinamoji-kaeriten-libreoffice-mac.dmg" ]]; then
    cp "${PACKAGING}/release/marinamoji-kaeriten-libreoffice-mac.dmg" "${RELEASE}/"
  fi
fi

echo "${LO_VER}" > "${RELEASE}/VERSION.txt"
cat > "${RELEASE}/INSTALL.txt" <<EOF
marinaMoji Kaeriten — LibreOffice extension ${LO_VER}

1. Quit Writer
2. Tools → Extension Manager → Add → MarinaMojiKaeriten.oxt
3. Accept the GPL-3.0 license → restart Writer
4. View → Toolbars → marinaMoji

macOS LibreOffice 26.x: if toolbar buttons do nothing, use the Mac .dmg installer
(copies Python macros into your LibreOffice profile).

Updates: Extension Manager → Check for Updates (feed on GitHub Pages after publish).
EOF

(
  cd "${RELEASE}"
  FILES=(MarinaMojiKaeriten.oxt MarinaMojiKaeriten.update.xml VERSION.txt INSTALL.txt)
  [[ -f marinamoji-kaeriten-libreoffice-mac.dmg ]] && FILES+=(marinamoji-kaeriten-libreoffice-mac.dmg)
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "${FILES[@]}" > SHA256SUMS.txt
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "${FILES[@]}" > SHA256SUMS.txt
  fi
)

echo "LibreOffice release artifacts → ${RELEASE}/"
ls -la "${RELEASE}"
echo
echo "Review ${RELEASE}/MarinaMojiKaeriten.update.xml before authorizing Pages deploy."
echo "Publish Release first, then copy the XML into pages/ and push main (or use the workflow input)."
