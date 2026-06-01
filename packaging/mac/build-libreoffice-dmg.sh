#!/usr/bin/env bash
# Wrap the LibreOffice installer .app in a .dmg for download.
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")/.." && pwd)"
MAC="$(cd "$(dirname "$0")" && pwd)"
APP="${PACKAGING}/release/Install marinaMoji Kaeriten (LibreOffice).app"
OXT="${PACKAGING}/release/MarinaMojiKaeriten.oxt"
DMG="${PACKAGING}/release/marinamoji-kaeriten-libreoffice-mac.dmg"
README="${PACKAGING}/release/Lisez-moi-LibreOffice.txt"

if [[ ! -d "${APP}" ]]; then
  "${PACKAGING}/mac/build-libreoffice-installer-app.sh"
fi
if [[ ! -f "${APP}/Contents/Resources/install-libreoffice-macos.sh" ]]; then
  echo "ERROR: ${APP} is missing install-libreoffice-macos.sh — rebuild installer app first."
  exit 1
fi

cat > "${README}" <<'EOF'
marinaMoji Kaeriten — LibreOffice (Mac)

1. If macOS says the app is damaged or from an unidentified developer:
   use install-libreoffice-macos.command instead (double-click), or
   Right-click the .app installer → Open → Open.

2. Quit LibreOffice Writer (Cmd+Q), then run the installer.

3. Accept the extension in Extension Manager when it opens, then restart Writer.

4. View → Toolbars → marinaMoji.

Alternative: double-click MarinaMojiKaeriten.oxt in this folder, then run the
installer app if toolbar buttons do nothing (macOS LibreOffice 26.x).

Install marinaMoji (IME) first from the main marinaMoji website.
EOF

STAGING="${PACKAGING}/release/dmg-staging-lo"
rm -rf "${STAGING}"
mkdir -p "${STAGING}"
cp -R "${APP}" "${STAGING}/"
cp "${README}" "${STAGING}/"
cp "${MAC}/install-libreoffice-macos.command" "${STAGING}/"
cp "${MAC}/install-libreoffice-macos.sh" "${STAGING}/"
chmod +x "${STAGING}/install-libreoffice-macos.command" "${STAGING}/install-libreoffice-macos.sh"
# Standalone copies so the .command works even if the .app fails to open
cp "${APP}/Contents/Resources/MarinaMojiKaeriten.oxt" \
   "${APP}/Contents/Resources/marinamoji_kaeriten.py" \
   "${APP}/Contents/Resources/export_core.py" \
   "${APP}/Contents/Resources/marinamoji_mapping.json" \
   "${STAGING}/" 2>/dev/null || true
if [[ -f "${OXT}" ]]; then
  cp "${OXT}" "${STAGING}/"
fi

rm -f "${DMG}"
hdiutil create -volname "marinaMoji Kaeriten LO" -srcfolder "${STAGING}" -ov -format UDZO "${DMG}"
rm -rf "${STAGING}"
echo "Built ${DMG}"
