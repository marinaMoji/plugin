#!/usr/bin/env bash
# Rewrite pages/version.json and pages/MarinaMojiKaeriten.update.xml from host
# version fields + MARINAMOJI_RELEASE_VERSION (bundle label).
#
# LibreOffice update-download URL prefers a versioned GitHub Release asset
# (not /latest/) so the feed stays reproducible. Set MARINAMOJI_RELEASE_TAG
# (e.g. plugins-v0.0.3 or libreoffice-v0.3.10) when publishing.
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "${PACKAGING}/.." && pwd)"
PAGES="${PLUGIN}/pages"
VERSION="${MARINAMOJI_RELEASE_VERSION:-}"
REPO="${MARINAMOJI_GITHUB_REPO:-${GITHUB_REPOSITORY:-marinaMoji/plugin}}"
TAG="${MARINAMOJI_RELEASE_TAG:-}"

if [[ -z "${VERSION}" ]]; then
  if [[ -f "${PACKAGING}/build-release.sh" ]]; then
    # Fall back to the default embedded in build-release.sh
    VERSION="$(sed -n 's/.*MARINAMOJI_RELEASE_VERSION:-\([^}]*\)}.*/\1/p' "${PACKAGING}/build-release.sh" | head -1)"
  fi
fi
VERSION="${VERSION:-0.0.0}"

LO_XML="${PLUGIN}/libreoffice/marinamoji_kaeriten/description.xml"
OO_JSON="${PLUGIN}/onlyoffice/config.json"
WORD_PKG="${PLUGIN}/word/package.json"
WORD_MANIFEST="${PLUGIN}/word/manifest.production.xml"
if [[ ! -f "${WORD_MANIFEST}" ]]; then
  WORD_MANIFEST="${PLUGIN}/word/manifest.xml"
fi

LO_VER="$(sed -n 's/.*<version value="\([^"]*\)".*/\1/p' "${LO_XML}" | head -1)"
OO_VER="$(python3 -c "import json; print(json.load(open('${OO_JSON}'))['version'])")"
WORD_VER="$(python3 -c "import json; print(json.load(open('${WORD_PKG}'))['version'])")"
WORD_MANIFEST_VER="$(sed -n 's/.*<Version>\([^<]*\)<\/Version>.*/\1/p' "${WORD_MANIFEST}" | head -1)"

if [[ -z "${LO_VER}" || -z "${OO_VER}" || -z "${WORD_VER}" || -z "${WORD_MANIFEST_VER}" ]]; then
  echo "ERROR: could not read one or more host versions" >&2
  echo "  libreoffice=${LO_VER:-?} onlyoffice=${OO_VER:-?} word=${WORD_VER:-?} manifest=${WORD_MANIFEST_VER:-?}" >&2
  exit 1
fi

if [[ -n "${MARINAMOJI_OXT_DOWNLOAD_URL:-}" ]]; then
  OXT_URL="${MARINAMOJI_OXT_DOWNLOAD_URL}"
elif [[ -n "${TAG}" ]]; then
  OXT_URL="https://github.com/${REPO}/releases/download/${TAG}/MarinaMojiKaeriten.oxt"
else
  # Default convention for LibreOffice-only releases
  OXT_URL="https://github.com/${REPO}/releases/download/libreoffice-v${LO_VER}/MarinaMojiKaeriten.oxt"
fi

mkdir -p "${PAGES}"
RELEASE_URL="${MARINAMOJI_RELEASE_URL:-https://github.com/${REPO}/releases/latest}"

python3 - "${PAGES}/version.json" <<PY
import json, sys
path = sys.argv[1]
data = {
    "plugins": "${VERSION}",
    "word": "${WORD_VER}",
    "word_manifest": "${WORD_MANIFEST_VER}",
    "libreoffice": "${LO_VER}",
    "onlyoffice": "${OO_VER}",
    "release_url": "${RELEASE_URL}",
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
print(f"Wrote {path}")
for k, v in data.items():
    print(f"  {k}: {v}")
PY

UPDATE_XML="${PAGES}/MarinaMojiKaeriten.update.xml"
cat > "${UPDATE_XML}" <<EOF
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
echo "Wrote ${UPDATE_XML} (libreoffice ${LO_VER})"
echo "  update-download: ${OXT_URL}"
