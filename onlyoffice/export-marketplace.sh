#!/usr/bin/env bash
# Build (optional) and export a folder ready to copy into
# ONLYOFFICE/onlyoffice.github.io → sdkjs-plugins/content/marinamoji/
#
# Does NOT fork, push, or open a pull request.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "${ROOT}/.." && pwd)"
OUT_ROOT="${MARINAMOJI_MARKETPLACE_OUT:-${PLUGIN}/packaging/release}"
STAGE="${OUT_ROOT}/marketplace/marinamoji"
ZIP="${OUT_ROOT}/marinamoji-onlyoffice-marketplace.zip"
SKIP_BUILD="${MARINAMOJI_MARKETPLACE_SKIP_BUILD:-0}"
FOLDER_NAME="marinamoji"

mkdir -p "${OUT_ROOT}"

if [[ "${SKIP_BUILD}" != "1" ]]; then
  echo "== Build ONLYOFFICE plugin"
  chmod +x "${ROOT}/build.sh" "${ROOT}/validate-marketplace.sh"
  "${ROOT}/build.sh"
else
  echo "== Skip build (MARINAMOJI_MARKETPLACE_SKIP_BUILD=1)"
  chmod +x "${ROOT}/validate-marketplace.sh"
  "${ROOT}/validate-marketplace.sh"
fi

VERSION="$(python3 -c "import json; print(json.load(open('${ROOT}/config.json'))['version'])")"

echo "== Stage marketplace tree → ${STAGE}"
rm -rf "${STAGE}"
mkdir -p "${STAGE}"

# Same payload as the .plugin zip, plus CHANGELOG (required by marketplace README).
for item in config.json index.html styles.css mapping.json CHANGELOG.md scripts resources; do
  if [[ -e "${ROOT}/${item}" ]]; then
    cp -R "${ROOT}/${item}" "${STAGE}/"
  else
    echo "ERROR: missing ${item}" >&2
    exit 1
  fi
done

# Drop build-only / source-only assets that are not needed in the store copy.
find "${STAGE}" -name '.DS_Store' -delete 2>/dev/null || true
find "${STAGE}/resources" -name 'logo_square_*.svg' -delete 2>/dev/null || true
find "${STAGE}/resources/store/screenshots" \( -name '*.svg' -o -name 'logo_long_*.png' -o -name 'icon.svg' \) -delete 2>/dev/null || true

STORE_SNIPPET="${OUT_ROOT}/marketplace/store-config-snippet.json"
cat > "${STORE_SNIPPET}" <<EOF
{ "name": "${FOLDER_NAME}", "discussion": "" }
EOF

SUBMIT="${OUT_ROOT}/marketplace/SUBMIT.txt"
cat > "${SUBMIT}" <<EOF
marinaMoji ONLYOFFICE marketplace export
version: ${VERSION}
folder name: ${FOLDER_NAME}
staged: marketplace/${FOLDER_NAME}/
zip: marinamoji-onlyoffice-marketplace.zip

This export does NOT open a pull request. Do that only with explicit authorization.

Initial listing
--------------
1. Fork https://github.com/ONLYOFFICE/onlyoffice.github.io (once).
2. Sync your fork with upstream master.
3. Copy marketplace/${FOLDER_NAME}/ to:
     sdkjs-plugins/content/${FOLDER_NAME}/
4. Append this object to the marketplace root store/config.json array:
     $(cat "${STORE_SNIPPET}")
5. Commit, push to your fork's master (or a branch), open a PR upstream.
6. PR title suggestion: Add marinamoji plugin (v${VERSION})

Update (already listed)
-----------------------
1. Sync fork with upstream.
2. Replace sdkjs-plugins/content/${FOLDER_NAME}/ with this export (same GUID, new version).
3. Do NOT change the GUID in config.json.
4. PR title suggestion: Update marinamoji to v${VERSION}

Docs: plugin/docs/ONLYOFFICE_MARKETPLACE.md
EOF

echo "== Zip ${ZIP}"
rm -f "${ZIP}"
(
  cd "${OUT_ROOT}/marketplace"
  zip -r -q "${ZIP}" "${FOLDER_NAME}" SUBMIT.txt store-config-snippet.json
)

echo ""
echo "Marketplace export ready (v${VERSION}):"
echo "  ${STAGE}"
echo "  ${ZIP}"
echo "  ${SUBMIT}"
