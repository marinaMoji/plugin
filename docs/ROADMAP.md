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
- [ ] Manual QA: simple レ, compound 一二レ, vertical text, font-size refresh

**Success criteria:** User types `說㆒㆑者` with marinaMoji, runs **Format kaeriten** on paragraph, sees convincing 一/レ at 說 with `者` following, in 縦書き. User does **not** edit inside the frame.

## Phase 1.5 — Sync and source mode

- [ ] **Refresh rendering** (idempotent rebuild from source marks)
- [ ] **Show source** — edit `說㆒㆑者`; views hidden or removed
- [ ] Find marinaMoji frames by editor-local tags (if metadata used)
- [ ] Paragraph font-size change → user **Refresh** or relative frame sizing
- [ ] **Copy as plain text** (canonical clipboard)

## Phase 2 — Export and fallback

- [ ] **Export TEI** from canonical visible text + `mapping.json` (not from frame objects)
- [ ] **Export LaTeX** (experimental, `\kundoku`-style)
- [ ] Subscript-only fallback macro for simple レ (no extension)

## Phase 3 — Word renderer

- [ ] Add-in or VBA: same canonical source, **textbox** renderer (see [WORD_FINDINGS.md](WORD_FINDINGS.md))
- [ ] **Format kaeriten** + **Refresh rendering** + **Show source** (parity with LO commands)
- [ ] Optional Word-local shape/bookmark IDs for refresh only
- [ ] No import of LO frames — format from source in Word

## Phase 4 — Optional

- [ ] Auto-format on save or idle (**not** on every keystroke)
- [ ] 漢文エディタ `[レ]` import
- [ ] 再読 / okurigana (ruby + fields in Word; separate from kaeriten views)
- [ ] OpenOffice QA
- [ ] marinaMoji toolbar hook (speculative)

## OnlyOffice (no dedicated phase in v1)

- [ ] Document: Unicode source + subscript fallback; no frame parity with LO
- [ ] Do not plan shared hidden metadata across LO / Word / OnlyOffice

## Deferred / rejected

| Item | Status |
|------|--------|
| Asian ruby as primary kaeriten | **Rejected** |
| Frames/textboxes as source of truth | **Rejected** |
| Hidden metadata as canonical semantics | **Rejected** for v1 |
| Cross-suite hidden schema (LO + Word + OnlyOffice) | **Rejected** for v1 |
| OnlyOffice frame compatibility | **Out of scope** v1 |
| Auto-format on every keystroke / IME commit | **Deferred** |
| User edits inside annotation objects | **Rejected** — edit source only |
