#!/usr/bin/env bash
# Build release artifacts for GitHub / website (maintainers only).
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "${PACKAGING}/.." && pwd)"
RELEASE="${PACKAGING}/release"
VERSION="${MARINAMOJI_RELEASE_VERSION:-0.3.7}"

rm -rf "${RELEASE}"
mkdir -p "${RELEASE}"

echo "== LibreOffice .oxt"
(cd "${PLUGIN}/libreoffice" && ./build.sh)
cp "${PLUGIN}/libreoffice/dist/MarinaMojiKaeriten.oxt" "${RELEASE}/"

if [[ "${MARINAMOJI_INCLUDE_WORD:-0}" == "1" ]] && [[ -d "${PLUGIN}/word" ]] && [[ -f "${PLUGIN}/word/package.json" ]]; then
  echo "== Word dist zip"
  (cd "${PLUGIN}/word" && npm run build --silent 2>/dev/null || npm run build)
  (cd "${PLUGIN}/word/dist" && zip -r -q "${RELEASE}/word-dist.zip" .)

  if [[ -n "${MARINAMOJI_PLUGIN_BASE:-}" ]] && [[ -f "${PACKAGING}/build-word-manifest.sh" ]]; then
    echo "== Word production manifest"
    "${PACKAGING}/build-word-manifest.sh" "${RELEASE}/marinamoji-kaeriten-word.xml"
  else
    echo "== Skip Word manifest (set MARINAMOJI_PLUGIN_BASE to generate)"
  fi
else
  echo "== Skip Word (parked — set MARINAMOJI_INCLUDE_WORD=1 to build Word assets)"
fi

echo "== ONLYOFFICE zip"
(cd "${PLUGIN}/onlyoffice" && ./build.sh)
(
  cd "${PLUGIN}/onlyoffice"
  zip -r -q "${RELEASE}/marinamoji-kaeriten-onlyoffice.zip" \
    config.json index.html styles.css mapping.json scripts resources
)

if [[ "$(uname -s)" == "Darwin" ]]; then
  echo "== macOS GUI installers"
  chmod +x "${PACKAGING}/mac/"*.sh
  "${PACKAGING}/mac/build-libreoffice-installer-app.sh"
  "${PACKAGING}/mac/build-onlyoffice-installer-app.sh"
  "${PACKAGING}/mac/build-libreoffice-dmg.sh"
  "${PACKAGING}/mac/build-onlyoffice-dmg.sh"

  if [[ "${MARINAMOJI_INCLUDE_WORD:-0}" == "1" ]] && \
     [[ -f "${RELEASE}/marinamoji-kaeriten-word.xml" ]] && \
     [[ -f "${PACKAGING}/mac/build-word-installer-app.sh" ]]; then
    "${PACKAGING}/mac/build-word-installer-app.sh"
    "${PACKAGING}/mac/build-word-dmg.sh"
  fi
fi

WORD_BUILT=0
if [[ -f "${RELEASE}/marinamoji-kaeriten-word.xml" ]]; then
  WORD_BUILT=1
fi

echo "${VERSION}" > "${RELEASE}/VERSION.txt"

WORD_STATUS="not included (run ./build-word-release.sh or set MARINAMOJI_INCLUDE_WORD=1)"
if [[ "${WORD_BUILT}" == "1" ]]; then
  WORD_STATUS="included (pre-release — upload word-dist.zip to ${MARINAMOJI_PLUGIN_BASE:-your hosted URL} first)"
fi

cat > "${RELEASE}/INSTALL.txt" <<EOF
marinaMoji Kaeriten office plugins — release ${VERSION}

Recommended: LibreOffice (alpha, daily driver)
Experimental: ONLYOFFICE (alpha)
Word add-in: ${WORD_STATUS}

--- LibreOffice (all platforms) ---
Download MarinaMojiKaeriten.oxt
1. Quit Writer
2. Extension Manager → Add → accept → restart Writer
3. View → Toolbars → marinaMoji

--- LibreOffice (macOS) ---
Download marinamoji-kaeriten-libreoffice-mac.dmg
1. Right-click installer → Open (if macOS warns)
2. Quit Writer, run "Install marinaMoji Kaeriten (LibreOffice)"
3. Accept extension → restart Writer → enable marinaMoji toolbar

The Mac installer copies Python macros (required on LibreOffice 26.x) and opens the .oxt.

--- ONLYOFFICE (experimental) ---
Download marinamoji-kaeriten-onlyoffice-mac.dmg (Mac) or marinamoji-kaeriten-onlyoffice.zip
Mac: run "Install marinaMoji Kaeriten (ONLYOFFICE)", quit ONLYOFFICE, reopen Writer
Manual: unzip into sdkjs-plugins/{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}/

EOF

if [[ "${WORD_BUILT}" == "1" ]]; then
  cat >> "${RELEASE}/INSTALL.txt" <<EOF
--- Word (pre-release) ---
Download marinamoji-kaeriten-word-mac.dmg (Mac) or marinamoji-kaeriten-word.xml (Windows)
Mac: Right-click installer → Open if macOS warns → run installer → Cmd+Q Word → reopen
     Accueil → Kaeriten → Kaeriten pane
Windows: Insertion → Compléments → Téléverser mon complément → select manifest XML
Requires internet: Word loads the add-in from ${MARINAMOJI_PLUGIN_BASE}

EOF
fi

cat >> "${RELEASE}/INSTALL.txt" <<EOF
Install the marinaMoji IME first (main marinaMoji repo).

Verify: SHA256SUMS.txt
EOF

(
  cd "${RELEASE}"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS.txt' -print0 | sort -z | xargs -0 shasum -a 256 > SHA256SUMS.txt
)

echo ""
echo "Release files in ${RELEASE}/ (version label: ${VERSION})"
ls -la "${RELEASE}"
