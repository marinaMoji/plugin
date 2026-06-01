# Roadmap

## Phase 0 — Done

- [x] Literature and web source survey
- [x] Align with marinaMoji `kaeriten.tsv`
- [x] Initial architecture docs
- [x] `mapping.json` stub
- [x] LibreOffice prototyping: ruby / subscript / **frames**
- [x] Decision: **canonical Unicode source + frame render view** ([LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md))

## Phase 1 — LibreOffice extension (render from source)

- [ ] `.oxt` skeleton (Python UNO)
- [ ] Parse mark clusters after base characters (see [CONVENTIONS.md](CONVENTIONS.md))
- [ ] Frame builder: borderless, as-character anchor, compound stack
- [ ] Commands: **Render selection**, **Render paragraph**, **Render document**
- [ ] Remove or hide source marks after render (strategy TBD)
- [ ] Manual tests: simple レ, compound 一二レ, vertical text

**Success criteria:** User types `說㆒㆑者` with marinaMoji, runs Render on paragraph, sees convincing 一/レ at 說 with `者` following, in 縦書き.

## Phase 1.5 — Sync and source mode

- [ ] **Refresh rendering** (idempotent rebuild frames from marks)
- [ ] **Show source** / hide frames for editing Unicode
- [ ] Frame registry (find marinaMoji frames for refresh)
- [ ] Paragraph font-size change → refresh or relative frame sizing
- [ ] **Copy as plain text** (canonical clipboard)

## Phase 2 — Export and fallback

- [ ] **Export TEI** from canonical text + `mapping.json`
- [ ] **Export LaTeX** (experimental, `\kundoku`-style)
- [ ] Subscript-only fallback macro for simple レ (no extension)

## Phase 3 — Word renderer

- [ ] VBA or add-in: same canonical source, Word-native layout (subscript / EQ)
- [ ] No expectation of importing LO frames into Word

## Phase 4 — Optional

- [ ] Auto-render on save or idle (not on every keystroke in v1)
- [ ] 漢文エディタ `[レ]` import
- [ ] 再読 / okurigana (ruby + fields in Word; separate from kaeriten frames)
- [ ] OpenOffice QA
- [ ] marinaMoji toolbar hook (speculative)

## Deferred / rejected

- Asian ruby as primary kaeriten — **rejected**
- Anchored frames as source of truth — **rejected**
- OnlyOffice frame compatibility — **out of scope**
- Full automatic render while typing — **deferred** (undo/IME complexity)
