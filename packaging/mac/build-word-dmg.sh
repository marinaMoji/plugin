#!/usr/bin/env bash
# Wrap the Word installer .app in a .dmg for download.
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")/.." && pwd)"
APP="${PACKAGING}/release/Install marinaMoji Kaeriten.app"
DMG="${PACKAGING}/release/marinamoji-kaeriten-word-mac.dmg"
README="${PACKAGING}/release/Lisez-moi-Word.txt"

if [[ ! -d "${APP}" ]]; then
  "${PACKAGING}/mac/build-word-installer-app.sh"
fi

cat > "${README}" <<'EOF'
marinaMoji Kaeriten — Word (Mac)

1. If macOS says the app is from an unidentified developer:
   Right-click "Install marinaMoji Kaeriten" → Open → Open.

2. Run the installer, then quit Word (Cmd+Q) and reopen.

3. In Word: Accueil → Kaeriten → Kaeriten pane.

Install marinaMoji (IME) first from the main marinaMoji website.

More help: see INSTALL-MAC-GATEKEEPER on the marinaMoji site.
EOF

STAGING="${PACKAGING}/release/dmg-staging"
rm -rf "${STAGING}"
mkdir -p "${STAGING}"
cp -R "${APP}" "${STAGING}/"
cp "${README}" "${STAGING}/"

rm -f "${DMG}"
hdiutil create -volname "marinaMoji Kaeriten Word" -srcfolder "${STAGING}" -ov -format UDZO "${DMG}"
rm -rf "${STAGING}"
echo "Built ${DMG}"
