# Word add-in — development and pre-publish QA (June 2026)

Handoff notes for **marinaMoji Kaeriten** in Microsoft Word (`plugin/word/`). For render experiments, see [WORD_FINDINGS.md](WORD_FINDINGS.md). For publishing, see [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md).

**Project status:** [STATUS.md](STATUS.md) — all three plugins are **feature-complete**; **testing** is the gate before publish.

---

## Current status

| Area | Status |
|------|--------|
| **Implementation** | ✅ Render / Unrender / Refresh / Copy plain; inline picture renderer (`word_primary: inline_picture`) |
| **Mac dev workflow** | ✅ HTTPS + mkcert + sideload + task pane |
| **Pre-publish QA** | ⏳ Required before GitHub/website release |
| **End-user hosting** | ⏳ Upload `dist/` to public HTTPS; ship production manifest |

The add-in loads HTML from a **local HTTPS server** (`https://127.0.0.1:3000`) during development. End users load from **your website** — never localhost.

**Compléments navigator preview** does not connect to Word — expected. Use **Accueil → Kaeriten pane** with a document open.

---

## Dev quick start

Run in **Terminal.app** from the Word add-in folder:

```bash
cd /Users/daniel/Code/marinaMoji/plugin/word

# One-time: trust mkcert CA (Mac password)
brew install mkcert    # if needed
mkcert -install

npm run setup:certs
npm run build
./install-mac.sh

npm run serve:stop
npm run serve
# Expect: "HTTPS trusted — OK for Word"

# Second terminal
npm run doctor
# Expect: "All checks passed."
```

**Word:** quit (Cmd+Q), reopen **with a document open**, then **Accueil → Kaeriten → Kaeriten pane**.

---

## Pre-publish QA checklist (section B)

Run these on **your target Word version** (Mac first; Windows separately).

1. **Connect:** task pane shows **Ready**.
2. **Simple mark, selection scope:** type `說` + レ with marinaMoji → select → **Render** → **Unrender** restores `說㆒`.
3. **Whole-document render:** type at least two clusters in different paragraphs, leave only the caret active (no selection), click **Render** → both clusters render.
4. **Compound:** `說㆒㆑者` → render → marks appear as inline picture beside 說.
5. **Refresh:** change paragraph font size → **Refresh** rescales pictures; run **Refresh** again without changing style and confirm nothing visibly changes.
6. **Copy plain:** with rendered views still showing, **Copy plain** → clipboard = `說㆒㆑者`. Reads alt-text metadata; does not unrender.
7. **縦書き:** vertical paragraph — compound stack and placement acceptable.
8. **Save / reopen:** rendered views survive save and reload.
9. **Production manifest:** build with `MARINAMOJI_PLUGIN_BASE=https://your-domain/word ./build-word-manifest.sh`; sideload production manifest; confirm pane loads from hosted URL (not localhost).

When all pass, enable Word in release build (`MARINAMOJI_INCLUDE_WORD=1`) and follow [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md) Phase 3.

**Export note:** v1 ships **Copy plain Unicode only**. TEI and LaTeX buttons were removed — no single standard for kanbun in those formats.

---

## Where to open the add-in (French Word UI)

| Goal | French menu path |
|------|------------------|
| **Register / list add-in** | **Compléments** → marinaMoji Kaeriten |
| **Real task pane (use this)** | **Accueil** → **Kaeriten** → **Kaeriten pane** |
| **Ribbon commands** | **Accueil** → group **Kaeriten** |

Mac sideload folder: `~/Library/Containers/com.microsoft.Word/Data/Documents/wef/`

Install script: `plugin/word/install-mac.sh`

---

## Troubleshooting

Run **`npm run diagnose`** first.

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| `unknown option '-install'` from mkcert | npm’s fake `mkcert` on PATH | `brew install mkcert`; `npm run setup:certs` |
| Blank pane | HTTPS cert not trusted | `mkcert -install`; `npm run serve` |
| « Erreur relative au complément » | Server not running | `npm run serve` (HTTPS); keep terminal open |
| **Word did not connect** in Compléments | Preview only | Open document → **Accueil → Kaeriten pane** |
| **Word did not connect** from ribbon | Server down or stale manifest | `npm run doctor`; Cmd+Q Word; `npm run reset-word` |

Safari check: `https://127.0.0.1:3000/taskpane.html` should load without “not secure” after `mkcert -install`.

---

## npm scripts (reference)

| Script | Purpose |
|--------|---------|
| `npm run build` | Webpack → `dist/` |
| `npm run serve` | HTTPS on 127.0.0.1:3000 |
| `npm run doctor` | Pre-flight checks |
| `npm run setup:certs` | mkcert leaf cert in `certs/` |
| `npm run reset-word` | Refresh sideload manifest |
| `npm test` | Export logic (no Word needed) |

---

## Related files

- [word/README.md](../word/README.md) — build and install
- [WORD_FINDINGS.md](WORD_FINDINGS.md) — renderer history
- [WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md) — Renderer chronicle
- [ROADMAP.md](ROADMAP.md) — Phase 3 checklist
- [ARCHITECTURE.md](ARCHITECTURE.md) — source vs view
