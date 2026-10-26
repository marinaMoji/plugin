#!/usr/bin/env bash
# Sign, notarize and staple the Mac installer .apps and .dmgs in packaging/release/.
#
# No-op (ad-hoc signatures stay) unless APP_IDENTITY is set, so local and fork
# builds keep working. CI sets APP_IDENTITY from the imported Developer ID cert and
# the three notary variables from secrets:
#   APPLE_API_KEY_ID, APPLE_API_ISSUER, APPLE_NOTARY_API_PRIVATE_KEY_P8
set -euo pipefail
MAC="$(cd "$(dirname "$0")" && pwd)"
PACKAGING="$(cd "${MAC}/.." && pwd)"
RELEASE="${PACKAGING}/release"

if [[ -z "${APP_IDENTITY:-}" ]]; then
  echo "APP_IDENTITY not set; leaving installers ad-hoc signed (Gatekeeper will warn)."
  exit 0
fi
: "${APPLE_API_KEY_ID:?}" "${APPLE_API_ISSUER:?}" "${APPLE_NOTARY_API_PRIVATE_KEY_P8:?}"

shopt -s nullglob
apps=("${RELEASE}"/Install\ marinaMoji\ Kaeriten*.app)
dmg_scripts=("${MAC}"/build-*-dmg.sh)

echo "== Developer ID signing (apps)"
for app in "${apps[@]}"; do
  codesign --force --deep --options runtime --timestamp --sign "${APP_IDENTITY}" "${app}"
  codesign --verify --deep --strict "${app}"
done

echo "== Rebuild dmgs around the signed apps"
for s in "${dmg_scripts[@]}"; do "${s}"; done

dmgs=("${RELEASE}"/*.dmg)
KEY="$(mktemp)"
trap 'rm -f "${KEY}"' EXIT
printf '%s\n' "${APPLE_NOTARY_API_PRIVATE_KEY_P8}" > "${KEY}"

for dmg in "${dmgs[@]}"; do
  echo "== ${dmg##*/}"
  codesign --force --timestamp --sign "${APP_IDENTITY}" "${dmg}"
  RESULT="$(xcrun notarytool submit "${dmg}" \
    --key "${KEY}" --key-id "${APPLE_API_KEY_ID}" --issuer "${APPLE_API_ISSUER}" \
    --wait --timeout 1h --output-format json)"
  echo "${RESULT}"
  if [[ "$(echo "${RESULT}" | jq -r .status)" != "Accepted" ]]; then
    xcrun notarytool log "$(echo "${RESULT}" | jq -r .id)" \
      --key "${KEY}" --key-id "${APPLE_API_KEY_ID}" --issuer "${APPLE_API_ISSUER}" || true
    echo "Notarization failed for ${dmg##*/}" >&2
    exit 1
  fi
  xcrun stapler staple "${dmg}"
  xcrun stapler validate "${dmg}"
  spctl --assess -vv --type open --context context:primary-signature "${dmg}"
done
