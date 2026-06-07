#!/usr/bin/env bash
# Build Word add-in release artifacts (dist zip, manifest, Mac .dmg installer).
# LibreOffice / ONLYOFFICE artifacts in packaging/release/ are left untouched.
#
# Usage:
#   cp packaging/word-release.env.example packaging/word-release.env
#   # edit MARINAMOJI_PLUGIN_BASE to your https://…/word URL
#   ./packaging/build-word-release.sh
#
# Or inline:
#   MARINAMOJI_PLUGIN_BASE=https://your-site/word ./packaging/build-word-release.sh
set -euo pipefail

PACKAGING="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "${PACKAGING}/.." && pwd)"
RELEASE="${PACKAGING}/release"
ENV_FILE="${PACKAGING}/word-release.env"

# Explicit opt-in: Word is never built unless you run this script (or set the flag yourself).
export MARINAMOJI_INCLUDE_WORD=1

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck source=/dev/null
  source "${ENV_FILE}"
fi

BASE="${MARINAMOJI_PLUGIN_BASE:-}"
if [[ -z "${BASE}" ]]; then
  echo "Set MARINAMOJI_PLUGIN_BASE (HTTPS URL where word/dist/ will be hosted, no trailing slash)."
  echo ""
  echo "  cp packaging/word-release.env.example packaging/word-release.env"
  echo "  # edit MARINAMOJI_PLUGIN_BASE, then:"
  echo "  ./packaging/build-word-release.sh"
  exit 1
fi
export MARINAMOJI_PLUGIN_BASE="${BASE%/}"

if [[ ! -d "${PLUGIN}/word" ]] || [[ ! -f "${PLUGIN}/word/package.json" ]]; then
  echo "Word add-in sources not found under ${PLUGIN}/word"
  exit 1
fi

mkdir -p "${RELEASE}"

echo "== Word dist (MARINAMOJI_PLUGIN_BASE=${MARINAMOJI_PLUGIN_BASE})"
(cd "${PLUGIN}/word" && npm run build --silent 2>/dev/null || npm run build)
(cd "${PLUGIN}/word/dist" && zip -r -q "${RELEASE}/word-dist.zip" .)

echo "== Word production manifest"
"${PACKAGING}/build-word-manifest.sh" "${RELEASE}/marinamoji-kaeriten-word.xml"

if [[ "$(uname -s)" == "Darwin" ]]; then
  echo "== macOS Word installer"
  chmod +x "${PACKAGING}/mac/"*.sh
  "${PACKAGING}/mac/build-word-installer-app.sh"
  "${PACKAGING}/mac/build-word-dmg.sh"
else
  echo "== Skip Mac .dmg (build on macOS for GUI installer)"
fi

(
  cd "${RELEASE}"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS.txt' -print0 | sort -z | xargs -0 shasum -a 256
) > "${RELEASE}/SHA256SUMS.txt"

echo ""
echo "Word release files in ${RELEASE}/"
ls -la "${RELEASE}"/word-dist.zip "${RELEASE}"/marinamoji-kaeriten-word.xml 2>/dev/null || true
ls -la "${RELEASE}"/marinamoji-kaeriten-word-mac.dmg 2>/dev/null || true
