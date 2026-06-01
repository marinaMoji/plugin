# Word add-in — development status (Mac, May 2026)

Handoff notes for **marinaMoji Kaeriten** in Microsoft Word (`plugin/word/`). For manual experiments (textboxes, ruby), see [WORD_FINDINGS.md](WORD_FINDINGS.md). For planning research (certs, macros, parity), see [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md).

## Current status

| Area | Status |
|------|--------|
| **LibreOffice extension** | Working — primary tool for daily use |
| **Word add-in code** | Built (v0.1.2): render / unrender / refresh, clipboard export, ribbon + task pane |
| **Word on Mac (your machine)** | **Not yet verified end-to-end** — dev HTTPS + Office.js connection still being stabilized |
| **Compléments navigator preview** | **Does not connect** to Word — expected; use ribbon task pane instead |

The add-in loads HTML from a **local HTTPS server** (`https://127.0.0.1:3000`). Word on Mac is stricter than Safari: if the certificate is not trusted, the pane stays **blank**. If Office.js never binds to a document, you see **“Word did not connect”**.

## What we fixed this session

- **HTTPS dev server** with mkcert (`certs/`) or Microsoft dev certs fallback
- **`npm run doctor`** — checks certs, `dist/`, sideload manifest, server
- **`npm run serve`** — must print **HTTPS trusted — OK for Word** (not FATAL)
- Manifest URLs use **`127.0.0.1`** (not `localhost`)
- Ribbon on **Accueil → Kaeriten** (Mac often hides custom tabs)
- Task pane UI with buttons; local + CDN fallback for `office.js`
- Clearer message when opened from **Compléments** preview vs real document pane

## Resume next session (checklist)

Run these in **Terminal.app**. You **must** be in the Word add-in folder (npm looks for `package.json` there):

```bash
cd /Users/daniel/Code/marinaMoji/plugin/word
```

If you see `ENOENT ... /Users/daniel/package.json`, you are in your **home folder** — run `cd` as above, or use `./mm` from that folder (works from anywhere: `.../plugin/word/mm run serve`).

Then:

```bash
# 1. One-time: trust mkcert CA (Mac password)
brew install mkcert    # if needed
mkcert -install

# 2. Certs + build
npm run setup:certs
npm run build
./install-mac.sh

# 3. Server (leave running)
npm run serve:stop
npm run serve
# Expect: "HTTPS trusted — OK for Word"

# 4. Verify (second terminal)
npm run doctor
# Expect: "All checks passed."

# 5. Word
npm run reset-word    # optional, if manifest changed
# Quit Word (Cmd+Q), reopen WITH A DOCUMENT OPEN
# Accueil → Kaeriten → Kaeriten pane   (NOT Compléments preview only)
```

**Success criteria for next session:**

1. Task pane shows **Ready — select text and click Render.**
2. Type `說㆒㆑者` with marinaMoji, select, click **Render** — content controls appear.
3. **Unrender** / **Refresh** / **Copy plain** work on the same selection.

If step 1 fails, use the troubleshooting table below before changing code.

## Where to open the add-in (French Word UI)

| Goal | French menu path |
|------|------------------|
| **Register / list add-in** | **Compléments** → marinaMoji Kaeriten |
| **Real task pane (use this)** | **Accueil** → **Kaeriten** → **Kaeriten pane** |
| **Ribbon commands** | **Accueil** → group **Kaeriten** |

Mac sideload folder (no “Upload my add-in” in the desktop app):

`~/Library/Containers/com.microsoft.Word/Data/Documents/wef/`

Install script: `plugin/word/install-mac.sh`

## Troubleshooting

Run **`npm run diagnose`** first — it prints certificate mode, whether Homebrew mkcert is used, and an HTTPS probe.

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| `unknown option '-install'` from mkcert | npm’s fake `mkcert` package on PATH, not Homebrew | `brew install mkcert`; use `/opt/homebrew/bin/mkcert -install`; `npm run setup:certs` |
| Blank pane | HTTPS cert not trusted | `mkcert -install` in Terminal.app; `npm run setup:certs`; `npm run serve` |
| Serve says probe failed | CA not in system keychain | `mkcert -install` (not “session” keychain only) |
| Port 3000 in use, probe fails | Old/wrong server on 3000 | `npm run serve:stop` then `npm run serve` |
| « Erreur relative au complément » | Server not running or wrong protocol | `npm run serve` (HTTPS); keep terminal open |
| **Word did not connect** in Compléments browser | Preview only | Open document → **Accueil → Kaeriten pane** |
| **Word did not connect** from ribbon too | Server down, stale manifest, or Office.js blocked | `npm run doctor`; Cmd+Q Word; `npm run reset-word` |
| Port 3000 in use | Old server | `npm run serve:stop` then `npm run serve` |
| Safari loads page, Word blank | Word does not allow “proceed anyway” | Trust CA properly (`mkcert -install`) |

Safari check: `https://127.0.0.1:3000/taskpane.html` should load **without** “not secure” after `mkcert -install`.

Minimal Word check: `https://127.0.0.1:3000/hello.html` — if this shows green heading in the pane, HTTPS is OK and the problem is Office.js only.

## npm scripts (reference)

| Script | Purpose |
|--------|---------|
| `npm run build` | Webpack → `dist/` |
| `npm run serve` | HTTPS on 127.0.0.1:3000 |
| `npm run doctor` | Pre-flight checks |
| `npm run diagnose` | HTTPS / mkcert detailed report |
| `npm run setup:certs` | mkcert leaf cert in `certs/` |
| `npm run reset-word` | Refresh sideload manifest |
| `npm run trust` / `trust:fix` | Microsoft dev certs (alternative to mkcert) |
| `npm test` | Export logic (no Word needed) |

## Planned next steps (priority order)

### A. Unblock Mac Word (environment)

1. Confirm `npm run doctor` → all OK with Word quit.
2. Confirm task pane **Ready** from **Accueil → Kaeriten pane** (document open).
3. If still failing: enable Word Web Inspector (`defaults write com.microsoft.Word OfficeWebAddinDeveloperExtras -bool true`; Word from office.com, not Mac App Store) and inspect console errors on the task pane.

### B. Functional QA (once connected)

1. Simple mark: `說` + レ → render → unrender.
2. Compound: `說㆒㆑者`.
3. Change paragraph font size → **Refresh**.
4. **Copy TEI** / **Copy LaTeX** into a text editor.
5. Optional: 縦書き paragraph.

### C. Code / product (after QA)

1. Decide: keep **content controls** v0.1 or invest in **textboxes** (`insertTextBox`) for closer match to [WORD_FINDINGS.md](WORD_FINDINGS.md) layout.
2. Align README trust docs (mkcert-first vs `npm run trust`).
3. Windows sideload path (Upload My Add-in) — separate test.
4. Update [ROADMAP.md](ROADMAP.md) Phase 3 when Mac QA passes.

### D. Practical workflow until Word is stable

Use **LibreOffice** for real editing; treat Word add-in as preview development only.

## Related files

- [word/README.md](../word/README.md) — build and install
- [WORD_FINDINGS.md](WORD_FINDINGS.md) — textbox vs ruby experiments
- [ROADMAP.md](ROADMAP.md) — Phase 3 checklist
- [ARCHITECTURE.md](ARCHITECTURE.md) — source vs view
