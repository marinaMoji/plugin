# marinaMoji Kaeriten — Microsoft Word add-in

Office.js add-in for **Word on Mac or Windows**. Same model as the LibreOffice extension:

- **Source:** visible Unicode from marinaMoji (`說㆒㆑者`)
- **View:** inline PNG pictures (canvas-drawn glyphs; default `word_primary: inline_picture`)
- **Commands:** Render, Unrender, Refresh, Copy plain text

**Status (June 2026):** Implementation complete for v1. **Pre-publish QA** and HTTPS hosting required before distribution. Dev setup: [../docs/WORD_ADDIN_DEV.md](../docs/WORD_ADDIN_DEV.md). Project status: [../docs/STATUS.md](../docs/STATUS.md).

**End-user distribution (no Terminal):** Host `dist/` on your website; ship the Mac installer from [../packaging/](../packaging/). See [../docs/SELF_HOSTED_PUBLISHING_PLAN.md](../docs/SELF_HOSTED_PUBLISHING_PLAN.md) (Phase 3) and [../docs/DISTRIBUTION.md](../docs/DISTRIBUTION.md).

See also [../docs/WORD_FINDINGS.md](../docs/WORD_FINDINGS.md), [../docs/WORD_ADDIN_ATTEMPTS.md](../docs/WORD_ADDIN_ATTEMPTS.md), and [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## Prerequisites

- [Node.js](https://nodejs.org/) 18+ and `npm`
- **Microsoft Word** (desktop; Mac or Windows)
- marinaMoji IME for typing Kanbun marks
- **Mac only:** [mkcert](https://github.com/FiloSottile/mkcert) recommended for HTTPS trust in Word

## Build

```bash
cd /Users/daniel/Code/marinaMoji/plugin/word
./build.sh
```

**npm must run inside this folder.** If Terminal says it cannot find `/Users/daniel/package.json`, you are in the wrong directory. Shortcut: `./mm run serve` (see below).

This installs npm dependencies (first time), bundles JavaScript into `dist/`, copies `mapping.json`, and runs export unit tests.

## Sideload for development (Mac)

Word on Mac (French or English) **does not** have LibreOffice-style “Extension Manager”, and **there is usually no “Upload my add-in” menu** in the desktop app. Manifests go in Word’s `wef` folder via `install-mac.sh`.

### Quick start (recommended)

```bash
cd plugin/word

# Once per Mac — installs mkcert’s CA (password prompt)
brew install mkcert
mkcert -install

npm run setup:certs
./build.sh
./install-mac.sh

npm run serve          # leave this terminal open
# Second terminal:
npm run doctor         # expect: All checks passed.
```

Then **quit Word (Cmd+Q)**, reopen with a **document open**, and open the pane from **Accueil → Kaeriten → Kaeriten pane** (not only the Compléments preview).

Full troubleshooting: [../docs/WORD_ADDIN_DEV.md](../docs/WORD_ADDIN_DEV.md).

### Certificate trust (Mac)

Word requires **HTTPS** on port **3000**. Unlike Safari, Word will **not** show a “continue anyway” button — the certificate must be trusted in the system keychain.

**Trap:** `npm run setup:certs` must use **Homebrew’s** [mkcert](https://github.com/FiloSottile/mkcert), not the unrelated npm package also named `mkcert` (pulled in by Office dev tools). If you see `unknown option '-install'`, run:

```bash
brew install mkcert
/opt/homebrew/bin/mkcert -install
npm run setup:certs
```

| Method | Commands |
|--------|----------|
| **mkcert (recommended)** | `brew install mkcert`; `/opt/homebrew/bin/mkcert -install`; `npm run setup:certs` |
| **Microsoft dev certs** | `npm run trust` or `npm run trust:fix` |
| **Check everything** | `npm run diagnose` |

**Shortcut (any directory):** `.../plugin/word/mm run serve` — wrapper that `cd`s to the right place first.

Manifest and server use **`https://127.0.0.1:3000`** (not `localhost`).

After trust is set up, `npm run serve` should print **HTTPS trusted — OK for Word**. If you see **FATAL**, run `mkcert -install` in **Terminal.app** (not only adding a cert to the “session” keychain).

### Server and checks

```bash
npm run serve          # HTTPS server — keep running
npm run serve:stop     # free port 3000
npm run doctor         # certs, dist/, manifest, server
npm run reset-word     # refresh sideload manifest after changes
```

**Safari check:** `https://127.0.0.1:3000/taskpane.html` should load without “not secure”.

**Minimal Word check:** `https://127.0.0.1:3000/hello.html` — confirms HTTPS only (no Office.js).

### Where to click in Word (French UI)

| Where | French UI | Notes |
|--------|-----------|--------|
| **Task pane (main UI)** | **Accueil** → **Kaeriten** → **Kaeriten pane** | Use this after a document is open |
| **Ribbon shortcuts** | **Accueil** → group **Kaeriten** | Render, Unrender, … |
| **Compléments list** | **Compléments** → marinaMoji Kaeriten | Registers add-in; **preview often does not connect** |

**Important:** The **Compléments** add-in browser (*navigateur*) shows a preview. Office.js often **never connects** there → *“Word did not connect”*. That is normal. Open a document, keep `npm run serve` running, then use **Accueil → Kaeriten pane**.

After changing `manifest.xml`, run `./install-mac.sh`, quit Word (Cmd+Q), restart.

### Alternative: Microsoft trust only

```bash
npm run trust
./build.sh && ./install-mac.sh
npm run start:server-only
```

### Windows / Word on the web

**Insert** → **Add-ins** → **My Add-ins** → **Upload My Add-in** → `plugin/word/manifest.xml`  
(French: **Insertion** → **Compléments** → **Mes compléments** → **Téléverser mon complément**.)

To stop debugging: `npm stop`.

## Usage

1. Type with marinaMoji, e.g. `說㆒㆑者`.
2. Select text (or leave nothing selected to use the whole document).
3. Click **Render** — marks become small stacked views after the base character.
4. Edit the **Unicode source** (run **Unrender** first, or edit before rendering).
5. After changing paragraph font size, click **Refresh**.
6. **Copy plain** puts canonical Unicode on the clipboard.

Operations are silent (no dialog boxes). Check the result in the document or by pasting elsewhere.

## Project layout

| Path | Role |
|------|------|
| `src/exportCore.js` | Parser + plain export (port of LO `export_core.py`) |
| `src/render.js` | Render / unrender / refresh in Word |
| `src/officeReady.js` | Wait for Office.js / Word host |
| `src/taskpane/` | Task pane HTML + UI |
| `src/commands/commands.js` | Ribbon `ExecuteFunction` handlers |
| `scripts/` | `serve-https.mjs`, `doctor.mjs`, `setup-mkcert.sh`, … |
| `manifest.xml` | Add-in registration and ribbon |
| `dist/` | Built files served at `https://127.0.0.1:3000/` |
| `certs/` | mkcert leaf cert (gitignored; created by `setup:certs`) |

## Notes

- v0.1 uses **content controls** (default via Office.js). Optional **floating** text boxes (`word_primary: textbox`) exist but failed Mac placement QA.
- **Next documented path** for LO-like layout: `insertTextBox` + `textWrap.type = inline` (Renderer C) — see [WORD_ADDIN_ATTEMPTS.md](../docs/WORD_ADDIN_ATTEMPTS.md) and [WORD_FINDINGS.md](../docs/WORD_FINDINGS.md). Microsoft documents `insertTextBox` as **floating** by default; inline wrap is a separate property.
- Export reads canonical Unicode from tagged views without changing the document; use the copy box + ⌘C if automatic clipboard fails on Mac.
- Word does not read LibreOffice frames — format from source in each app.

## Tests

```bash
npm test
```

No Word installation required.
