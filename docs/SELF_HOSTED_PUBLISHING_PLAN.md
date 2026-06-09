# Self-hosted publishing — implementation plan (all three plugins)

Step-by-step plan to ship **LibreOffice**, **Word**, and **ONLYOFFICE** kaeriten plugins from **your own website + GitHub Releases**, without Microsoft AppSource, Apple notarization, or asking users to run Terminal.

**Audience:** you (maintainer). **End users:** researchers who download installers or extension files.

**Related:** [DISTRIBUTION.md](DISTRIBUTION.md) (overview), [INSTALL-MAC-GATEKEEPER.md](INSTALL-MAC-GATEKEEPER.md), [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) (dev-only localhost path).

---

## What “self-hosted” means for each plugin

| Plugin | What you host | What users download | Needs public HTTPS? |
|--------|---------------|---------------------|---------------------|
| **LibreOffice** | `.oxt` + Mac `.dmg` on GitHub / website | Extension file or GUI installer | No (files are self-contained) |
| **ONLYOFFICE** | `.zip` + Mac `.dmg` on GitHub / website | Plugin folder or GUI installer | No for Desktop (local plugin folder) |
| **Word** | **Static add-in files** on your website **and** manifest in installer | Mac `.dmg` (manifest) or `manifest.xml` (Windows) | **Yes** — Word loads `taskpane.html` from your URL every session |

Only **Word** requires ongoing web hosting. LO and OO are “download once, install locally” like the LibreOffice `.oxt`.

```text
your-domain.example
├── /releases/          ← GitHub Release assets (or direct links)
└── /word/              ← Word only: plugin/word/dist/ uploaded here
    ├── taskpane.html
    ├── taskpane.js
    ├── commands.html
    ├── mapping.json
    ├── office.js
    └── assets/icon-*.png
```

---

## Current readiness (June 2026)

| Plugin | Code | Packaging scripts | In default release? | Blocker before public ship |
|--------|------|-------------------|---------------------|----------------------------|
| **LibreOffice** | ✅ feature-complete | ✅ `.oxt`, Mac `.dmg` | ✅ yes | **Pre-publish QA** on target LO version |
| **ONLYOFFICE** | ✅ feature-complete | ✅ `.zip`, Mac `.dmg` | ✅ yes | **Pre-publish QA** on ONLYOFFICE Desktop |
| **Word** | ✅ feature-complete | ✅ `word-dist.zip`, manifest, Mac `.dmg` | 🟡 opt-in (`MARINAMOJI_INCLUDE_WORD=1`) | **Pre-publish QA** + upload `dist/` to HTTPS |

See [STATUS.md](STATUS.md) for the current gate: implementation is done; **testing** blocks publish.

---

## Phase 0 — One-time setup (maintainer)

### 0.1 Prerequisites on your Mac

```bash
# Build tools (already used in dev)
brew install mkcert librsvg gh   # gh = GitHub CLI for releases
cd plugin/word && npm install    # Word build only
```

### 0.2 Choose URLs

Pick stable paths before your first public release. Example:

| Purpose | Example URL |
|---------|-------------|
| Website install index | `https://marinamoji.example.org/install/` |
| Word add-in static files | `https://marinamoji.example.org/word/` |
| GitHub Releases (all binaries) | `https://github.com/marinaMoji/plugin/releases` |

Set this once and reuse in manifests and website copy:

```bash
export MARINAMOJI_PLUGIN_BASE="https://marinamoji.example.org/word"
```

### 0.3 Website pages to create

| Page | Content |
|------|---------|
| `/install/` | Pick LibreOffice / Word / ONLYOFFICE |
| `/install/libreoffice/` | Download links, 3 screenshots, toolbar step |
| `/install/word/` | Mac `.dmg`, Windows manifest upload steps |
| `/install/onlyoffice/` | Mac `.dmg` + manual zip path |
| `/install/mac-gatekeeper/` | Right-click → Open (link [INSTALL-MAC-GATEKEEPER.md](INSTALL-MAC-GATEKEEPER.md)) |

Every page should say: **Install marinaMoji IME first**, then the office plugin.

### 0.4 Hosting options for Word `dist/`

Any static host with valid TLS:

- **GitHub Pages** — [docs/GITHUB_PAGES.md](GITHUB_PAGES.md) (`https://marinaMoji.github.io/plugin/word/` for this repo)
- University web space + Let’s Encrypt
- Cloudflare Pages / Netlify
- S3 + CloudFront

**Not acceptable for end users:** `https://127.0.0.1:3000`, mkcert, or self-signed certs.

---

## Phase 1 — LibreOffice (ship first)

LibreOffice is the **recommended daily driver**. Self-hosted publishing is the simplest of the three.

### 1.1 Build release artifacts

```bash
cd plugin/packaging
export MARINAMOJI_RELEASE_VERSION="0.4.0"
./build-release.sh
```

Produces in `packaging/release/`:

- `MarinaMojiKaeriten.oxt` — all platforms
- `marinamoji-kaeriten-libreoffice-mac.dmg` — Mac GUI installer (macOS only)
- `Install marinaMoji Kaeriten (LibreOffice).app`

### 1.2 Upload

| Where | Files |
|-------|-------|
| GitHub Release | `.oxt`, `.dmg`, `INSTALL.txt`, `SHA256SUMS.txt` |
| Website | Same download links (can mirror GitHub Release URLs) |

No separate “plugin server” for LibreOffice.

### 1.3 QA gate (before linking from website)

- [ ] Fresh Mac: `.dmg` installer → Extension Manager → restart Writer
- [ ] Toolbar **Render / Unrender / Refresh** work
- [ ] **Copy plain text** to clipboard
- [ ] Vertical page + compound kaeriten (image renderer)
- [ ] Linux or Windows: `.oxt` only path tested once

### 1.4 User install (document on website)

**Mac:** download `.dmg` → Right-click → Open installer → quit Writer → run installer → restart → **View → Toolbars → marinaMoji**.

**Linux / Windows:** download `.oxt` → Extension Manager → Add → restart.

Details: [libreoffice/README.md](../libreoffice/README.md).

---

## Phase 2 — ONLYOFFICE (experimental, ship second)

ONLYOFFICE plugins are **copied into a local folder** — no HTTPS server required for Desktop users.

### 2.1 Build (included in `build-release.sh`)

Produces:

- `marinamoji-kaeriten-onlyoffice.zip`
- `marinamoji-kaeriten-onlyoffice-mac.dmg` (macOS)

Plugin GUID (install path must match):

```text
{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}
```

Desktop path:

```text
~/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/sdkjs-plugins/{GUID}/
```

### 2.2 Upload

Same as LibreOffice: GitHub Release + website download links. No live hosting.

### 2.3 QA gate

- [ ] Mac installer copies into correct `sdkjs-plugins/{GUID}/` folder
- [ ] **Plugins → marinaMoji** appears after restart
- [ ] Render / Unrender on `說㆒㆑者`
- [ ] Document limitation: paste from LO **does not** keep frames (Unicode source only)

### 2.4 Document Server (optional, later)

If colleagues use **browser ONLYOFFICE** via Docker, IT must deploy the plugin folder on the **server** plugin path — a separate checklist from Desktop. See [ONLYOFFICE.md](ONLYOFFICE.md).

---

## Phase 3 — Word (ship when Mac QA passes)

Word is the only plugin that needs **you to keep a website folder updated** on every release.

### 3.1 Finish development QA first

Do **not** publish until these pass from **Accueil → Kaeriten pane** (not Compléments preview):

- [ ] Task pane shows **Ready**
- [ ] Render / Unrender / Refresh on simple + compound marks
- [ ] Copy plain text
- [ ] Save document, quit Word, reopen — marks still round-trip
- [ ] Test once on Windows (upload manifest) if you support Windows users

Checklist: [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) section B.

### 3.2 Build Word assets

```bash
cd plugin/word
./build.sh                    # → dist/ (gitignored; rebuild every release)
npm run validate              # manifest schema check (dev manifest)

cd ../packaging
export MARINAMOJI_INCLUDE_WORD=1
export MARINAMOJI_PLUGIN_BASE="https://marinamoji.example.org/word"
export MARINAMOJI_RELEASE_VERSION="0.4.0"
./build-release.sh
```

Produces:

| File | Purpose |
|------|---------|
| `word-dist.zip` | Upload and extract to `https://…/word/` on your server |
| `marinamoji-kaeriten-word.xml` | Production manifest (URLs already substituted) |
| `marinamoji-kaeriten-word-mac.dmg` | Mac installer (embeds manifest) |

Template: [word/manifest.production.xml](../word/manifest.production.xml).  
Generator: [packaging/build-word-manifest.sh](../packaging/build-word-manifest.sh).

### 3.3 Deploy static files (every Word release)

1. Unzip `word-dist.zip` contents to your web root under `/word/`.
2. Verify in a browser (no cert warnings):
   - `https://marinamoji.example.org/word/taskpane.html`
   - `https://marinamoji.example.org/word/assets/icon-32.png`
3. Upload **before** or **at the same time** as the new manifest/installer — old manifests pointing at missing files break users.

### 3.4 Ship installers

| Platform | Ship | User steps |
|----------|------|------------|
| **Mac** | `marinamoji-kaeriten-word-mac.dmg` | Run installer → Cmd+Q Word → reopen → Accueil → Kaeriten |
| **Windows** | `marinamoji-kaeriten-word.xml` | Insertion → Compléments → Téléverser → select manifest |

Mac installer script: [packaging/mac/install-word-addin.applescript](../packaging/mac/install-word-addin.applescript).

### 3.5 Un-park Word in release pipeline

When ready for public Word distribution, update these (maintainer one-time edits):

1. **`packaging/build-release.sh`** — set `MARINAMOJI_INCLUDE_WORD=1` by default, or document the env var prominently.
2. **`packaging/publish-github-release.sh`** — add `word-dist.zip`, Word `.dmg`, and manifest to uploaded assets.
3. **`packaging/release/INSTALL.txt`** — add Word section (generated text in `build-release.sh`).
4. **`officeReady.js` error strings** — replace “npm run serve” with “check your internet connection / support page” for production users.

### 3.6 Word-specific ongoing maintenance

On **every** Word plugin release:

```text
1. ./build.sh
2. Upload dist/ → https://…/word/
3. Regenerate manifest (MARINAMOJI_PLUGIN_BASE=…)
4. Rebuild Mac .dmg if manifest URLs changed
5. Bump <Version> in manifest if Office caches old add-in
```

---

## Phase 4 — GitHub Release (all three)

### 4.1 Full maintainer command sequence

```bash
cd plugin/packaging

export MARINAMOJI_RELEASE_VERSION="0.4.0"
export MARINAMOJI_RELEASE_TAG="plugins-v0.4.0"
export MARINAMOJI_GITHUB_REPO="marinaMoji/plugin"   # adjust to your repo

# LibreOffice + ONLYOFFICE always; Word when ready:
export MARINAMOJI_INCLUDE_WORD=1
export MARINAMOJI_PLUGIN_BASE="https://marinamoji.example.org/word"

./build-release.sh

# Upload dist/ to website (Word) — manual or CI
# unzip -o packaging/release/word-dist.zip -d /path/to/webroot/word/

./publish-github-release.sh
```

### 4.2 Release asset checklist

| Asset | LibreOffice | ONLYOFFICE | Word |
|-------|:-----------:|:----------:|:----:|
| `MarinaMojiKaeriten.oxt` | ✅ | — | — |
| `marinamoji-kaeriten-libreoffice-mac.dmg` | ✅ | — | — |
| `marinamoji-kaeriten-onlyoffice.zip` | — | ✅ | — |
| `marinamoji-kaeriten-onlyoffice-mac.dmg` | — | ✅ | — |
| `word-dist.zip` | — | — | ✅ |
| `marinamoji-kaeriten-word.xml` | — | — | ✅ |
| `marinamoji-kaeriten-word-mac.dmg` | — | — | ✅ |
| `INSTALL.txt` | ✅ | ✅ | ✅ |
| `SHA256SUMS.txt` | ✅ | ✅ | ✅ |

---

## Phase 5 — Website copy (minimum viable)

### Install index (`/install/`)

```text
1. Install marinaMoji IME (link to main repo / download page)
2. Pick your word processor:
   - LibreOffice (recommended)
   - Microsoft Word (beta — requires internet)
   - ONLYOFFICE (experimental)
3. macOS blocked the app? → Gatekeeper help page
```

### Per-plugin one-liner

| Plugin | Label on website |
|--------|------------------|
| LibreOffice | **Recommended** — full kaeriten rendering, vertical text, export |
| Word | **Beta** — requires hosted add-in; Mac/Windows sideload |
| ONLYOFFICE | **Experimental** — inline controls; paste from LO loses frames |

---

## Recommended rollout order

```text
Week 1 — LibreOffice public
  ├── build-release.sh
  ├── GitHub Release + website /install/libreoffice/
  └── QA on LO 26.x Mac + one Linux/Windows .oxt test

Week 2 — ONLYOFFICE (experimental label)
  ├── same release tag or plugins-v0.4.1
  └── QA on ONLYOFFICE Desktop Mac

Week 3+ — Word (when QA green)
  ├── set up /word/ hosting
  ├── MARINAMOJI_INCLUDE_WORD=1
  ├── unpark publish-github-release.sh
  └── /install/word/ + Windows manifest instructions
```

You can ship LO and OO **now** without waiting for Word.

---

## What we are still not doing

| Channel | Status |
|---------|--------|
| Microsoft AppSource / Partner Center | Deferred — see [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md) |
| Apple notarization ($99/yr) | Optional; document Gatekeeper instead |
| Auto-update inside plugins | Manual re-download from Releases |
| Centralized M365 deployment | Optional for university IT later |

---

## Quick reference — maintainer files

| File | Role |
|------|------|
| [packaging/build-release.sh](../packaging/build-release.sh) | Build all release binaries |
| [packaging/publish-github-release.sh](../packaging/publish-github-release.sh) | Upload to GitHub Releases |
| [packaging/build-word-manifest.sh](../packaging/build-word-manifest.sh) | Production Word manifest |
| [packaging/mac/README.md](../packaging/mac/README.md) | Build Mac `.app` / `.dmg` installers |
| [word/manifest.production.xml](../word/manifest.production.xml) | Word manifest template |
| [libreoffice/build.sh](../libreoffice/build.sh) | LibreOffice `.oxt` only |
| [onlyoffice/build.sh](../onlyoffice/build.sh) | ONLYOFFICE plugin folder |

---

## Related docs

- [DISTRIBUTION.md](DISTRIBUTION.md) — strategy overview
- [INSTALLERS_AND_UPDATES.md](INSTALLERS_AND_UPDATES.md) — installers, publication, user updates
- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) — localhost dev (not for end users)
- [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md) — AppSource vs self-host
- [ONLYOFFICE.md](ONLYOFFICE.md) — Desktop vs Document Server
- [INSTALL-MAC-GATEKEEPER.md](INSTALL-MAC-GATEKEEPER.md) — unsigned Mac installers
