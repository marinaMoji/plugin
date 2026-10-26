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

3. macOS protège le dossier des compléments de Word. Si l'installeur ne peut pas copier le
   fichier, il vous le montre : faites glisser marinamoji-kaeriten.xml (sélectionné, sur le
   Bureau) dans le dossier de Word qui s'ouvre à côté, et choisissez Remplacer si demandé.

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
3. If the installer cannot copy the file itself (macOS protects Word's folder), it shows it to
   you: drag marinamoji-kaeriten.xml (selected on your Desktop) into the Word folder that opens
   beside it, choosing Replace if asked.
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
