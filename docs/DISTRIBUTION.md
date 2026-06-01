# Distribution — GitHub, website, and easy installers

How we ship marinaMoji **office plugins** without Microsoft Marketplace, Apple Developer Program, or asking users to run Terminal.

**Audience:** researchers and students (newbies). **Channels:** GitHub Releases + your website. **Mac:** unsigned installers with clear **Gatekeeper** instructions.

---

## What we are *not* doing (for now)

| Program | Why skip |
|---------|----------|
| **Microsoft Partner Center / AppSource** | Public store review; needs hosted add-in + legal entity |
| **Apple Developer Program ($99/yr)** | **Notarization** for frictionless Gatekeeper — optional later |
| **mkcert / `npm run serve` for end users** | Developer-only; confuses non-technical users |

We **do** use normal **HTTPS** on our own domain (e.g. Let’s Encrypt via GitHub Pages, Cloudflare, or university hosting) so Word can load the add-in **without** a local dev server.

---

## Three products, three install experiences

| Product | End-user install (goal) | Gatekeeper |
|---------|-------------------------|------------|
| **LibreOffice** | Download `.oxt` → double-click → Extension Manager | Usually none (LO opens the extension) |
| **Word** | Download `.dmg` → run **Install marinaMoji Kaeriten** → open Word | May warn on unsigned `.app` / `.dmg` — [see below](#gatekeeper-macos) |
| **ONLYOFFICE** | Download `.zip` → run **Install…** app or drag folder | Same as Word if using `.app` |

**Recommended order for new users:** LibreOffice first (simplest), then Word or ONLYOFFICE if they need that host.

---

## Architecture: dev vs release (Word)

```text
DEVELOPERS (you)                    END USERS (website / GitHub)
─────────────────                   ─────────────────────────────
manifest.xml                        manifest.production.xml
https://127.0.0.1:3000/      →      https://plugins.example.org/word/
npm run serve (local)               (static files on your server)
mkcert                              (normal public TLS — no user setup)
```

End users **never** install mkcert or Node. They only:

1. Install the marinaMoji **IME** (separate installer — see main repo).
2. Run our **Word installer** once (copies manifest).
3. Open Word → **Accueil → Kaeriten**.

We publish `plugin/word/dist/` to `https://<your-domain>/word/` on each release.

---

## GitHub Releases layout

Each release tag (e.g. `plugins-v0.3.7`) attaches:

| Asset | Contents |
|-------|----------|
| `MarinaMojiKaeriten.oxt` | LibreOffice extension |
| `marinamoji-kaeriten-word-mac.dmg` | Word manifest installer + readme |
| `word-dist.zip` | Static add-in files (for self-hosting mirrors) |
| `marinamoji-kaeriten-onlyoffice.zip` | ONLYOFFICE plugin folder |
| `SHA256SUMS.txt` | Checksums |

Build locally: `plugin/packaging/build-release.sh` (maintainers only).

---

## Website pages (suggested)

| Page | Purpose |
|------|---------|
| **/install/** | Index: pick LibreOffice / Word / ONLYOFFICE |
| **/install/libreoffice/** | Download `.oxt`, 3 screenshots (Extension Manager FR/EN) |
| **/install/word/** | Download Mac `.dmg`, Windows “upload manifest” later |
| **/install/onlyoffice/** | Download zip + Install app |
| **/install/mac-gatekeeper/** | One page: “macOS blocked the app” — Right-click → Open |

Link to GitHub Releases as “all versions / checksums”.

---

## Gatekeeper (macOS)

Downloaded `.dmg`, `.app`, and `.pkg` files from the internet get a **quarantine** flag. macOS may say the app is from an unidentified developer.

**We do not notarize** (that needs Apple Developer). We document safe install:

### If the user sees “cannot be opened because the developer cannot be verified”

1. **Do not** disable Gatekeeper globally.
2. **Right-click** (or Control-click) the app → **Open** → **Open** again in the dialog.  
   (French: **Clic droit → Ouvrir → Ouvrir**.)
3. Or: **Réglages Système → Confidentialité et sécurité → Ouvrir quand même** (button appears right after the block).

### If the download still fails

Remove quarantine for that file only (optional support step — can be a one-line in advanced troubleshooting, not the main path):

```bash
xattr -cr "/Applications/Install marinaMoji Kaeriten.app"
```

Prefer **Right-click → Open** in docs for newbies.

### What we sign (optional, free)

Maintainers can ad-hoc sign to reduce scariness (still not notarized):

```bash
codesign --force --deep --sign - "Install marinaMoji Kaeriten.app"
```

Users may still need Right-click → Open the first time.

---

## LibreOffice — easiest path

**User steps (no Terminal):**

1. Download `MarinaMojiKaeriten.oxt` from the website or GitHub.
2. Double-click the file (or **Fichier → Ouvrir** in LibreOffice).
3. LibreOffice **Extension Manager** opens → **Add** → accept → **restart Writer**.
4. **Affichage → Barres d’outils → marinaMoji**.

**Maintainer:** `cd plugin/libreoffice && ./build.sh` → upload `dist/MarinaMojiKaeriten.oxt`.

Optional: put the `.oxt` inside a `.dmg` with a short `Lisez-moi.txt` — same Gatekeeper rules if the `.dmg` is unsigned.

`install.sh` (macros to user profile) stays **optional** for power users; the `.oxt` alone is enough for the toolbar.

---

## Word — hosted add-in + double-click installer

### Hosting (required before release)

1. Build: `cd plugin/word && ./build.sh` (or `npm run build`).
2. Upload contents of `plugin/word/dist/` to  
   `https://<your-domain>/word/`  
   (all of `taskpane.html`, `*.js`, `mapping.json`, `assets/`, etc.).
3. Generate production manifest:  
   `MARINAMOJI_PLUGIN_BASE=https://<your-domain>/word ./packaging/build-word-manifest.sh`
4. Ship `manifest.production.xml` (or embedded in the Mac installer).

TLS must be valid (Let’s Encrypt is fine). **No** self-signed certs for end users.

### Mac installer (no Terminal)

We ship **`Install marinaMoji Kaeriten.app`** (AppleScript), built from:

`plugin/packaging/mac/install-word-addin.applescript`

**User steps:**

1. Download `marinamoji-kaeriten-word-mac.dmg`.
2. Open the DMG, drag the installer app to **Applications** (optional).
3. **Right-click → Open** the installer if macOS warns.
4. Installer copies the manifest into Word’s sideload folder.
5. Quit Word (Cmd+Q), reopen, open a document → **Accueil → Kaeriten**.

See [packaging/mac/README.md](../packaging/mac/README.md) for building the `.app` / `.dmg`.

### Windows (later)

**Insertion → Compléments → Mes compléments → Téléverser mon complément** → choose `manifest.production.xml`.  
No local server if manifest URLs point to your website.

---

## ONLYOFFICE — zip + installer app

**User steps:**

1. Download `marinamoji-kaeriten-onlyoffice.zip`.
2. Run **Install marinaMoji Kaeriten (ONLYOFFICE).app** (copies folder into plugins directory), **or** follow drag-and-drop steps in the readme inside the zip.
3. Restart ONLYOFFICE Writer → **Plugins → marinaMoji Kaeriten**.

Build: `plugin/packaging/build-release.sh` zips `plugin/onlyoffice/` (after `./build.sh`).

---

## Maintainer workflow (Terminal — not for end users)

```bash
cd plugin/packaging
export MARINAMOJI_PLUGIN_BASE="https://plugins.yourdomain.org/word"
./build-release.sh
# Upload dist/release/* to GitHub Release + static host
./mac/build-word-dmg.sh   # optional: DMG with installer .app
```

---

## IME (marinaMoji) is separate

The **input method** (typing `;r` → ㆑) is installed from the main **marinaMozc** repo (`.pkg` / instructions there). Office plugins only **format** text already typed.

Website should say: **Install marinaMoji first**, then install the Writer/Word extension you use.

---

## Checklist before publishing a release

- [ ] `MarinaMojiKaeriten.oxt` opens in LO Extension Manager
- [ ] `https://<domain>/word/taskpane.html` loads in Safari (no certificate warning)
- [ ] Production manifest URLs all use `<domain>`, not `127.0.0.1`
- [ ] Mac Word installer tested on a clean Mac account (Right-click → Open path documented)
- [ ] GitHub Release assets + `SHA256SUMS.txt`
- [ ] Website install pages linked from README

---

## Related docs

- [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md) — why we skip AppSource for now
- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) — **developers** still use localhost + mkcert
- [ONLYOFFICE.md](ONLYOFFICE.md)
- [packaging/mac/README.md](../packaging/mac/README.md) — build installer apps
