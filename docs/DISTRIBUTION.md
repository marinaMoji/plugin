# Distribution — GitHub, website, and easy installers

How we ship marinaMoji **office plugins** without Microsoft Marketplace, Apple Developer Program, or asking users to run Terminal.

**Audience:** researchers and students (newbies). **Channels:** GitHub Releases + your website. **Mac:** unsigned installers with clear **Gatekeeper** instructions.

**Current state:** implementation complete; **pre-publish QA** blocks release. See **[STATUS.md](STATUS.md)**.

**Maintainers:** step-by-step publishing plan for all three plugins (LO, Word, ONLYOFFICE) → **[SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md)**.  
**Installers + updates:** **[INSTALLERS_AND_UPDATES.md](INSTALLERS_AND_UPDATES.md)**.  
**ONLYOFFICE Plugin Marketplace:** **[ONLYOFFICE_MARKETPLACE.md](ONLYOFFICE_MARKETPLACE.md)** (separate from GitHub Releases).  
**LibreOffice Extensions website:** **[LIBREOFFICE_MARKETPLACE.md](LIBREOFFICE_MARKETPLACE.md)** (listing ≠ native update feed).

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
| **LibreOffice** | Download Mac `.dmg` → run installer (or `.oxt` on Linux/Windows) | May warn on unsigned `.app` / `.dmg` |
| **Word** | Download Mac `.dmg` (manifest) or Windows `marinamoji-kaeriten-word-setup.exe` | May warn on unsigned `.dmg`; the Windows `.exe` is signed (SmartScreen may still warn at first) |
| **ONLYOFFICE** | Download Mac `.dmg` → run installer (or manual zip) | May warn on unsigned `.app` / `.dmg` |

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

We publish `plugin/word/dist/` to `https://marinamoji.github.io/plugin/word/` (GitHub Pages for this repo) or your own domain on each release. See [GITHUB_PAGES.md](GITHUB_PAGES.md).

---

## GitHub Releases layout

Each release tag (e.g. `plugins-v0.3.7`) attaches:

| Asset | Contents |
|-------|----------|
| `MarinaMojiKaeriten.oxt` | LibreOffice extension (all platforms) |
| `marinamoji-kaeriten-libreoffice-mac.dmg` | Mac GUI installer + `.oxt` + readme |
| `marinamoji-kaeriten.plugin` | ONLYOFFICE Plugin Manager install (7.4+) |
| `marinamoji-kaeriten-onlyoffice.zip` | ONLYOFFICE plugin folder (manual install) |
| `marinamoji-kaeriten-onlyoffice-mac.dmg` | Mac GUI installer + zip + readme |
| `INSTALL.txt` | Plain-language install summary |
| `SHA256SUMS.txt` | Checksums |

Word assets (`word-dist.zip`, Word `.dmg`) are now included in default release builds (`MARINAMOJI_INCLUDE_WORD=1` is the default in `build-release.sh` as of 2026-08-26, after Mac pre-publish QA passed). Set `MARINAMOJI_INCLUDE_WORD=0` to exclude them.

Build locally: `plugin/packaging/build-release.sh` (maintainers only).

---

## Website pages (suggested)

| Page | Purpose |
|------|---------|
| **/install/** | Index: pick LibreOffice / Word / ONLYOFFICE |
| **/install/libreoffice/** | Download `.oxt`, 3 screenshots (Extension Manager FR/EN) |
| **/install/word/** | Download Mac `.dmg` or Windows `marinamoji-kaeriten-word-setup.exe` |
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

## LibreOffice — Mac installer + `.oxt`

**macOS (recommended — no Terminal):**

1. Download `marinamoji-kaeriten-libreoffice-mac.dmg` from the website or GitHub.
2. **Right-click → Open** the installer app if macOS warns ([Gatekeeper](#gatekeeper-macos)).
3. **Quit Writer** (Cmd+Q), then run **Install marinaMoji Kaeriten (LibreOffice)**.
4. Restart Writer completely (Cmd+Q, then reopen).
5. **View → Toolbars → marinaMoji**.

The Mac installer copies Python macros into your LibreOffice profile (required on **LibreOffice 26.x**) and registers `MarinaMojiKaeriten.oxt` with LibreOffice’s `unopkg` (not bare `open`, which often fails on macOS when Launch Services has no `.oxt` handler).

**Linux / Windows / power users:**

1. Download `MarinaMojiKaeriten.oxt`.
2. Double-click (or **Tools → Extension Manager → Add**) → accept → restart Writer.
3. **View → Toolbars → marinaMoji**.

**Maintainer:** `cd plugin/libreoffice && ./build.sh` → upload `dist/MarinaMojiKaeriten.oxt` and the Mac `.dmg` from `packaging/build-release.sh`.

Optional **`install.sh`** (Terminal) — same macro copy as the Mac installer; for APSO / Macro dialog only.

---

## Word — hosted add-in + double-click installer

### Hosting (required before release)

For **this repo**, GitHub Pages already hosts the Word add-in — see [GITHUB_PAGES.md](GITHUB_PAGES.md). On your own domain:

1. Build: `cd plugin/word && ./build.sh` (or `npm run build`).
2. Upload contents of `plugin/word/dist/` to  
   `https://<your-domain>/word/`  
   (all of `taskpane.html`, `*.js`, `mapping.json`, `assets/`, etc.).
3. Generate production manifest:  
   `MARINAMOJI_PLUGIN_BASE=https://<your-domain>/word ./packaging/build-word-manifest.sh`
4. Ship `manifest.production.xml` (or embedded in the Mac installer).

**Testers (this repo):** `./word/install-mac-production.sh` (it falls back to a Finder drag when macOS blocks the copy) — no upload step needed; workflow deploys on push to `main`.

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

### Windows installer

We ship **`marinamoji-kaeriten-word-setup.exe`** (Inno Setup, built by CI on every `plugins-v*` release from `packaging/windows/marinamoji-kaeriten-word.iss`).

**User steps:**

1. Download `marinamoji-kaeriten-word-setup.exe` from the GitHub Release. The installer is Authenticode-signed, but SmartScreen can still warn until the certificate has built up reputation (**More info → Run anyway**).
2. Run it. It is per-user: no administrator rights, nothing outside your profile. English, French and Japanese.
3. It copies the production manifest to `%LOCALAPPDATA%\marinaMoji\Kaeriten\` and registers it under `HKCU\Software\Microsoft\Office\16.0\WEF\Developer`.
4. Close Word completely, reopen it with a document (internet required, the add-in is hosted on GitHub Pages).
5. **Home → Kaeriten**, or **Insert → Add-ins → My Add-ins → Developer Add-ins**.

Uninstall from **Settings → Apps** (removes the registry value and the folder).

The add-in itself updates automatically (Word loads it from GitHub Pages); the installer only needs re-running if the manifest changes.

**Status:** the installer is built by CI but has not yet been verified on a real Windows Word, nor has the composer's direct insert on Windows ([marinaMoji/plugin#12](https://github.com/marinaMoji/plugin/issues/12)). Direct insert from the composer needs marinaMoji 0.0.19 or later.

**Manual (testers, Word on the web):** **Insertion → Compléments → Mes compléments → Téléverser mon complément** → choose `marinamoji-kaeriten-word.xml` from the release.

---

## ONLYOFFICE — Mac installer + zip (experimental)

**macOS (no Terminal):**

1. Download `marinamoji-kaeriten-onlyoffice-mac.dmg`.
2. **Right-click → Open** the installer if macOS warns.
3. **Quit ONLYOFFICE** (Cmd+Q), run **Install marinaMoji Kaeriten (ONLYOFFICE)**.
4. Reopen a **Document** → ribbon **Plugins** → **marinaMoji**.

**Manual (all platforms):**

1. Prefer `marinamoji-kaeriten.plugin` → Plugins → Plugin Manager → *Install plugin manually* (Desktop 7.4+; plugin needs **9.3+** to run).
2. Or download `marinamoji-kaeriten-onlyoffice.zip` and unzip into `sdkjs-plugins/{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}/` (see [onlyoffice/README.md](../onlyoffice/README.md)).
3. Quit ONLYOFFICE fully, reopen a Document, look on the **Plugins** tab (not Home).

Build: `plugin/packaging/build-release.sh` (zips `plugin/onlyoffice/` and builds Mac `.app` / `.dmg`).

---

## Maintainer workflow (Terminal — not for end users)

```bash
cd plugin/packaging
export MARINAMOJI_RELEASE_VERSION="0.3.7"
./build-release.sh
# Upload packaging/release/* to GitHub Release + website
```

On macOS, `build-release.sh` also builds LibreOffice and ONLYOFFICE `.app` installers and `.dmg` wrappers.

---

## IME (marinaMoji) is separate

The **input method** (typing `;r` → ㆑) is installed from [github.com/marinaMoji/marinaMoji](https://github.com/marinaMoji/marinaMoji) (`.pkg` / Linux install instructions there). This **plugin** repo only **formats** text already typed.

Website should say: **Install marinaMoji first**, then install the Writer/Word extension you use.

---

## Checklist before publishing a release

See the full phased checklist in **[SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md)**. Minimum:

- [ ] `MarinaMojiKaeriten.oxt` opens in LO Extension Manager
- [ ] Mac LO installer tested (toolbar buttons work after restart)
- [ ] Mac ONLYOFFICE installer lands in `sdkjs-plugins/{GUID}/`
- [ ] Word: `dist/` uploaded to `https://<domain>/word/` and manifest URLs verified (when shipping Word)
- [ ] GitHub Release assets + `SHA256SUMS.txt` + `INSTALL.txt`
- [ ] Website install pages linked from README

---

## Related docs

- **[SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md)** — implementation plan (all three plugins)
- [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md) — why we skip AppSource for now
- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) — **developers** still use localhost + mkcert
- [ONLYOFFICE.md](ONLYOFFICE.md)
- [packaging/mac/README.md](../packaging/mac/README.md) — build installer apps
