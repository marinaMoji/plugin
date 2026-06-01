#!/usr/bin/env bash
# Wrap the ONLYOFFICE installer .app in a .dmg for download.
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")/.." && pwd)"
MAC="$(cd "$(dirname "$0")" && pwd)"
APP="${PACKAGING}/release/Install marinaMoji Kaeriten (ONLYOFFICE).app"
ZIP="${PACKAGING}/release/marinamoji-kaeriten-onlyoffice.zip"
DMG="${PACKAGING}/release/marinamoji-kaeriten-onlyoffice-mac.dmg"
README="${PACKAGING}/release/Lisez-moi-ONLYOFFICE.txt"

if [[ ! -d "${APP}" ]]; then
  "${PACKAGING}/mac/build-onlyoffice-installer-app.sh"
fi

cat > "${README}" <<'EOF'
marinaMoji Kaeriten — ONLYOFFICE (Mac, experimental)

1. If macOS says the app is damaged or from an unidentified developer:
   use install-onlyoffice-macos.command instead (double-click), or
   Right-click the .app installer → Open → Open.

2. Quit ONLYOFFICE (Cmd+Q), then run the installer.

3. Reopen Writer → Plugins → marinaMoji.

Alternative: unzip marinamoji-kaeriten-onlyoffice.zip into
~/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/sdkjs-plugins/{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}/

Install marinaMoji (IME) first from the main marinaMoji website.
EOF

STAGING="${PACKAGING}/release/dmg-staging-oo"
rm -rf "${STAGING}"
mkdir -p "${STAGING}"
cp -R "${APP}" "${STAGING}/"
cp "${README}" "${STAGING}/"
cp "${MAC}/install-onlyoffice-macos.command" "${STAGING}/"
cp "${MAC}/install-onlyoffice-macos.sh" "${STAGING}/"
chmod +x "${STAGING}/install-onlyoffice-macos.command" "${STAGING}/install-onlyoffice-macos.sh"
mkdir -p "${STAGING}/marinamoji-kaeriten-onlyoffice"
rsync -a "${APP}/Contents/Resources/marinamoji-kaeriten-onlyoffice/" "${STAGING}/marinamoji-kaeriten-onlyoffice/"
if [[ -f "${ZIP}" ]]; then
  cp "${ZIP}" "${STAGING}/"
fi

rm -f "${DMG}"
hdiutil create -volname "marinaMoji Kaeriten OO" -srcfolder "${STAGING}" -ov -format UDZO "${DMG}"
rm -rf "${STAGING}"
echo "Built ${DMG}"
