# Roadmap

## Phase 0 — Done

- [x] Literature and web source survey
- [x] Align with marinaMoji `kaeriten.tsv`
- [x] Initial architecture docs
- [x] `mapping.json` stub
- [x] LibreOffice prototyping: ruby / subscript / **frames**
- [x] Microsoft Word prototyping: ruby / subscript / **textboxes** ([WORD_FINDINGS.md](WORD_FINDINGS.md))
- [x] Decision: **canonical Unicode source + disposable visual view** ([ARCHITECTURE.md](ARCHITECTURE.md))
- [x] Decision: **manual Format kaeriten** in v1 (no auto-format while typing)
- [x] Decision: **visible Unicode** is semantic layer; hidden metadata optional for refresh only

## Phase 1 — LibreOffice extension (format from source)

- [x] `.oxt` skeleton (Python UNO) — [libreoffice/](../libreoffice/)
- [x] Parse mark clusters after base characters (see [CONVENTIONS.md](CONVENTIONS.md))
- [x] Frame builder: borderless, as-character anchor, compound stack
- [x] Menu: **Format kaeriten** (selection / paragraph / document)
- [x] Remove source marks on format; restore via **Show source** (`Description` stores marks)
- [x] **Refresh rendering** (show source + format)
- [x] Inline **SVG image** renderer; vertical text; compound touching; page-direction toggle
- [ ] **Pre-publish QA:** simple レ, compound ㆒㆑, vertical text, font-size refresh, copy plain

**Success criteria:** User types `說㆒㆑者` with marinaMoji, runs **Render kaeriten**, sees convincing kaeriten at 說 with `者` following, in 縦書き. User does **not** edit inside rendered views.

## Phase 1.5 — Sync and source mode

- [ ] **Refresh rendering** (idempotent rebuild from source marks)
- [ ] **Show source** — edit `說㆒㆑者`; views hidden or removed
- [ ] Find marinaMoji frames by editor-local tags (if metadata used)
- [ ] Paragraph font-size change → user **Refresh** or relative frame sizing
- [x] **Copy as plain text** (canonical clipboard)

## Phase 2 — Export and fallback

- [x] **Copy plain text** to clipboard (canonical Unicode)
- [x] ~~Copy TEI / Copy LaTeX~~ — **removed from v1** (no single kanbun standard in TEI or LaTeX; see [STATUS.md](STATUS.md))
- [ ] Subscript-only fallback macro for simple レ (no extension)

## Phase 3 — Word renderer

- [x] Office.js add-in — [word/](../word/)
- [x] **Inline picture** renderer (Mac default; `word_primary: inline_picture`)
- [x] **Render** + **Refresh** + **Unrender** + **Copy plain** (parity with LO toolbar)
- [x] Alt-text metadata (`MARINAMOJI:kaeriten:id=…;source=…`) for round-trip
- [x] Mac dev tooling: HTTPS server, mkcert, `doctor`, task pane + Accueil ribbon ([WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md))
- [ ] **Pre-publish QA:** Accueil pane connects; render/unrender/refresh; 縦書き; compound; copy plain
- [ ] Self-hosted `dist/` + production manifest ([SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md))

## Phase 4 — Optional

- [ ] Auto-format on save or idle (**not** on every keystroke)
- [ ] 漢文エディタ `[レ]` import
- [ ] 再読 / okurigana (ruby + fields in Word; separate from kaeriten views)
- [ ] OpenOffice QA
- [ ] marinaMoji toolbar hook (speculative)

## OnlyOffice plugin

- [x] Plugin skeleton — [onlyoffice/](../onlyoffice/) (sidebar, copy plain, inline content controls)
- [ ] **Pre-publish QA** on ONLYOFFICE Desktop
- [x] Document: Unicode source; no frame parity with LO on paste

## Deferred / rejected

| Item | Status |
|------|--------|
| Asian ruby as primary kaeriten | **Rejected** |
| Frames/textboxes as source of truth | **Rejected** |
| Hidden metadata as canonical semantics | **Rejected** for v1 |
| TEI / LaTeX export in product UI | **Rejected** for v1 — no single standard |
| Cross-suite hidden schema (LO + Word + OnlyOffice) | **Rejected** for v1 |
| OnlyOffice frame compatibility | **Out of scope** v1 |
| Auto-format on every keystroke / IME commit | **Deferred** |
| User edits inside annotation objects | **Rejected** — edit source only |
