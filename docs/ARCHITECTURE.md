# Architecture

## Design principle

**IME for input; extension for layout; Unicode source for meaning.**

```text
marinaMoji IME  →  說㆒㆑者     (semantic source — ordinary text)
Office plugin   →  說 [一/レ] 者  (visual view — frame or textbox)
```

- marinaMoji commits **Unicode Kanbun** (`說㆒㆑者`) — durable, searchable, interoperable plain text.
- Office extensions build **rendered views** from that source — not the other way around.
- Anchored objects are **not** the source of truth (copy/paste to other apps loses frames; search across an annotation may fail).

> **The rendered object is not data. The rendered object is a view.**

If font changes, an object is deleted, or the document is re-imported, the plugin **regenerates** the view from source text.

## Two layers

```
┌─────────────────────────────────────────────────────────┐
│  Canonical source (ordinary text)                        │
│  說㆒㆑者  — marinaMoji ;1 ;r after 說                  │
│  • grep / git / Copy plain text                         │
└─────────────────────────────────────────────────────────┘
                          │
                          │  Format kaeriten (manual; v1)
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Rendering layer (host-specific)                         │
│  LibreOffice: borderless frame anchored as character     │
│  Word:        view layer (CC default; inline text box TBD) │
│  • print-quality kanbun • PDF • read-only for users      │
└─────────────────────────────────────────────────────────┘
```

Conceptual interchange for **export** (not necessarily stored inside `.odt` / `.docx`):

```xml
<kanbun char="說" kaeriten="㆒㆑"/>
```

Exporters derive this from **canonical** `㆒㆑` in the text stream + [mapping.json](../mapping.json), not from frame pixels or host-only hidden tags.

## Pipeline (v1 — manual)

Wrong workflow (rejected):

```text
type → create textbox → edit textbox contents
```

Correct workflow:

```text
type:     說㆒㆑者
              ↓
     [Format kaeriten]     ← user command; not automatic on each key
              ↓
     plugin parses clusters
              ↓
     plugin inserts frames/textboxes (view)
              ↓
user edits source (Show source / visible ㆒㆑)
              ↓
     [Refresh rendering]   ← rebuild views from source
```

Annotation objects should be **read-only** from the user’s perspective. Never require clicking inside a frame/textbox to change kaeriten.

## User-facing commands (planned)

| Menu label (preferred) | Also called | Purpose |
|------------------------|-------------|---------|
| **Render kaeriten** | Format + refresh | Selection if highlighted, else document: source → frames; rescale existing frames |
| **Unrender kaeriten** | Show source | Same scope: frames → Unicode marks for editing |
| **Copy plain text** | Copy as plain text | Clipboard = `說㆒㆑者` (marks from rendered views spliced in) |

**Not in v1:**

- Automatic format on every keystroke or IME commit (undo / cursor / IME edge cases).
- Optional later: format on save or idle ([ROADMAP.md](ROADMAP.md) Phase 4).

## Metadata and export

### What is canonical (all hosts)

| Store | Role |
|-------|------|
| Visible Unicode `說㆒㆑者` | **Semantics** — search, git, collaboration, plain export |
| [mapping.json](../mapping.json) | How marks map to stacked glyphs (一, レ, …) |
| [CONVENTIONS.md](CONVENTIONS.md) | Parser rules (clusters after base kanji) |

This is sufficient for v1. Custom document XML, RDF, or proprietary hidden fields are **not** required to encode kaeriten meaning.

### Optional editor-local metadata (per host only)

If the extension **hides** marks after formatting, or needs to find existing objects quickly, it may store **renderer bookkeeping** inside that file format, for example:

- LibreOffice: custom frame name `marinaMoji:kaeriten:<id>`, bookmark, or ODF extension (TBD in code).
- Word: content control name, bookmark, or shape name (TBD).

| Use optional metadata for | Do **not** use it for |
|---------------------------|------------------------|
| Linking a frame/textbox to a text offset for **Refresh** | Primary meaning if Unicode is missing |
| Finding objects to delete before rebuild | Cross-app semantics (read Unicode source instead) |
| Idempotent refresh | Cross-app interchange (Word ↔ LO ↔ OnlyOffice) |

**Do not** replicate one hidden schema across Word, LibreOffice, and OnlyOffice for v1 — each suite has different extension APIs, and paste between apps already drops visual objects.

### Export

```text
說㆒㆑者  →  Copy plain text (clipboard)
```

**v1 ships plain Unicode only.** TEI XML and LaTeX were prototyped (`export_core.py`, `exportCore.js`) but are **not** exposed in the UI: there is no one agreed way to encode kanbun kaeriten in TEI or LaTeX across DH projects (contrast furigana ruby, where conventions exist). Users who need structured export should keep canonical marks in the document and transform downstream with their own project rules.

Export pipelines **never** depend on reading frame/image pixels as the semantic layer.

## What we rejected as primary

| Approach | Role |
|----------|------|
| Asian ruby (LO / Word) | **Rejected** — furigana-like placement |
| Subscript / small Unicode only | **Fallback** — simple レ |
| Anchored frame (LO) | **Primary LO renderer** — [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md) |
| Anchored textbox (Word) | **Target Word renderer** (publication layout) — inline `textWrap` spike; CC is **v0.1 default** — [WORD_FINDINGS.md](WORD_FINDINGS.md) |
| Hidden XML as canonical semantics | **Deferred** — plain Unicode is enough for v1 |
| Auto-format while typing | **Deferred** — manual **Format kaeriten** in v1 |

## LibreOffice extension (first implementation)

- **Delivery:** `.oxt` extension (Python + UNO).
- **Render algorithm (outline):**
  1. Scan selection for `(base character)(run of U+3190–U+319F)+`.
  2. Map marks to stacked glyphs via `mapping.json`.
  3. Create borderless frame anchored as character after base kanji.
  4. Hide or remove visible mark cluster (strategy TBD — see [CONVENTIONS.md](CONVENTIONS.md)).
  5. Optionally register editor-local frame ID for refresh (not for export semantics).

- **Refresh triggers:** **Refresh rendering** command; optional hook on paragraph font-size change.

Details: [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md).

## Microsoft Word (Phase 3)

Same **canonical source**; different **renderer** (swappable without changing the IME):

| Renderer | Role | Status |
|----------|------|--------|
| **Content controls** | In-flow small glyphs + `MARINAMOJI:source=` tag | **Default** in add-in ([mapping.json](../mapping.json)) |
| **Floating text box** | `insertTextBox` + position nudges | Optional; **poor Mac QA** |
| **Inline text box** | `insertTextBox` + `textWrap.type = inline` | **Documented spike** — closest Office.js match to LO “as character” |
| **Subscript / EQ** | Fallback for simple marks | Per [mapping.json](../mapping.json) |

- Word add-in uses the same `mapping.json`; does **not** import LibreOffice frames — re-format from source in Word.
- Users edit `說㆒㆑者`, not view innards. See [WORD_FINDINGS.md](WORD_FINDINGS.md), [WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md).

## OnlyOffice

- **No v1 expectation** of frame/textbox parity with LibreOffice or Word (paste tests: visuals lost).
- **Canonical Unicode** in the file remains portable; collaborators can read marks or use **Copy as plain text**.
- A future OnlyOffice path would be **source + subscript fallback** or a separate renderer — not shared hidden metadata with LO/Word.

## OpenOffice

Test after LibreOffice extension works; UNO likely similar to LO.

## Interoperability expectations

| Action | Expectation |
|--------|-------------|
| Edit in LibreOffice / Word with extension | Full fidelity |
| PDF from host app | Full fidelity |
| Copy to gedit / email | **Plain text** — `說㆒㆑者`; use **Copy as plain text** |
| Copy LO → OnlyOffice | **Visuals lost** — source Unicode may remain |
| Search `說者` with view inserted between 說 and 者 | **Fails** — search `說` or **Show source** |
| git diff | Visible `㆒㆑` in file or `.txt` sidecar |

## Non-goals (v1)

- Automatic 書き下し文
- Linguistic disambiguation when user misplaced marks
- OnlyOffice frame compatibility
- Auto-format on every IME commit or keystroke
- Cross-suite hidden metadata as the semantic layer
- User editing inside annotation frames/textboxes

## Testing

1. Compound mark: `說㆒㆑者` → Format kaeriten → visual 一/レ at 說; plain `者` follows.
2. Vertical 縦書き paragraph.
3. Insert/delete before 說 — view still attached.
4. Refresh after 12 pt → 14 pt paragraph change.
5. Copy as plain text → `說㆒㆑者` on clipboard.
6. (Word, Phase 3) Same tests with textboxes instead of frames.

## Related

- [CONVENTIONS.md](CONVENTIONS.md) — typing and collaboration
- [ROADMAP.md](ROADMAP.md) — phased delivery
- [TARGET_LAYOUT.md](TARGET_LAYOUT.md) — per-host render primitives
