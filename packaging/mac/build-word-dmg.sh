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

1. Installez d'abord marinaMoji (IME) depuis le site principal.
   Quittez Word (Cmd+Q).

2. Double-cliquez sur "Install marinaMoji Kaeriten".
   - Cette version est signée et notarisée par Apple : elle s'ouvre directement.
   - Si macOS affiche « Apple n'a pas pu confirmer… » (ancienne version non signée) :
     fermez la fenêtre, ouvrez Réglages Système → Confidentialité et sécurité,
     faites défiler jusqu'au message sur l'installeur, cliquez sur « Ouvrir quand même »,
     puis confirmez. (Le clic droit → Ouvrir ne fonctionne plus depuis macOS 15.)

3. macOS protège le dossier des compléments de Word. Si l'installation automatique est
   bloquée, l'installeur affiche le fichier marinamoji-kaeriten.xml (sur le Bureau) et le
   dossier de Word : faites glisser le fichier dans ce dossier. (Ou accordez l'« Accès
   complet au disque » à l'installeur et relancez-le.)

4. Rouvrez Word avec un document (connexion internet requise : le complément
   est chargé depuis marinamoji.github.io).

5. Dans Word : Accueil → Kaeriten → volet Kaeriten.
   S'il n'apparaît pas : Insertion → Compléments → Mes compléments → section
   « Compléments de développeur ».

---

marinaMoji Kaeriten — Word (Mac)

1. Install marinaMoji (IME) first, then quit Word (Cmd+Q).
2. Double-click "Install marinaMoji Kaeriten". It is signed and notarized, so it opens
   directly. On an older unsigned build: System Settings → Privacy & Security → Open
   Anyway (right-click → Open no longer works on macOS 15+).
3. If macOS blocks the automatic install, drag marinamoji-kaeriten.xml (shown on your Desktop)
   into the Word add-in folder the installer opens, or grant the installer Full Disk Access.
4. Reopen Word with a document (internet required).
5. Home → Kaeriten → Kaeriten pane, or Insert → Add-ins → My Add-ins → Developer Add-ins.
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
