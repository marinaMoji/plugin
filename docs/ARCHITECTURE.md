# Architecture

## Design principle

**IME for input; extension for layout; Unicode source for meaning.**

- marinaMoji commits **Unicode Kanbun** (`說㆒㆑者`) — durable, searchable, interoperable plain text.
- The LibreOffice extension builds **rendered views** (anchored frames) from that source — not the other way around.
- Anchored objects are **not** the source of truth (poor search across marks, copy/paste to other apps loses frames).

## Two layers

```
┌─────────────────────────────────────────────────────────┐
│  Canonical source (ordinary text)                        │
│  說㆒㆑者  — marinaMoji ;1 ;r after 說                  │
│  • grep / git / TEI export / Copy as plain text         │
└─────────────────────────────────────────────────────────┘
                          │
                          │  Render selection / paragraph / document
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Rendering layer (LibreOffice only, v1)                 │
│  說 [frame: 一/レ] 者  — borderless frame as character   │
│  • print-quality kanbun • edit in Writer • PDF export   │
└─────────────────────────────────────────────────────────┘
```

Conceptual interchange (export targets, not necessarily stored inside `.odt`):

```xml
<kanbun char="說" kaeriten="㆒㆑"/>
```

Exporters read **canonical** `㆒㆑`, not frame pixels.

## Pipeline

```
marinaMoji IME  →  Writer body text (Unicode U+319x)
                         ↓
              [Render kaeriten]  (manual v1; not auto-on-keypress)
                         ↓
              Hide/remove visible marks + insert anchored frames
                         ↓
              [Refresh rendering] on source or style changes
```

## What we rejected as primary (LibreOffice)

| Approach | Role |
|----------|------|
| Asian ruby | Rejected — furigana-like placement |
| Subscript / small Unicode only | **Fallback** — simple レ |
| Anchored borderless frame | **Primary renderer** — see [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md) |

## Extension commands (planned)

| Command | Purpose |
|---------|---------|
| **Render kaeriten** | Selection / paragraph / document: source → frames |
| **Refresh rendering** | Rebuild frames from current source marks; fix font-scale drift |
| **Show source** | Edit canonical Unicode; hide or remove frames |
| **Copy as plain text** | Clipboard = `說㆒㆑者` (no frames) |
| **Export TEI** | From canonical text + `mapping.json` |
| **Export LaTeX** | From canonical text (`\kundoku`-style, TBD) |

**Not in v1:** fully automatic render on every keystroke (undo/cursor/IME edge cases).

## Shared components

| Component | Format | Used by |
|-----------|--------|---------|
| [mapping.json](../mapping.json) | Unicode → display glyphs, stack order, fallbacks | Render, export |
| [CONVENTIONS.md](CONVENTIONS.md) | Mark clusters, typing order | User + parser |
| Frame builder | UNO Python in `.oxt` | LibreOffice v1 |
| Subscript fallback | Character styles | Simple marks, no extension |

## LibreOffice extension (first implementation)

- **Delivery:** `.oxt` extension (Python + UNO), not only loose macros.
- **Render algorithm (outline):**
  1. Scan selection for pattern: `(base character)(run of U+3190–U+319F)+`.
  2. For each cluster: map marks to stacked glyphs via `mapping.json`.
  3. Create borderless frame anchored as character after base kanji.
  4. Remove cluster from visible text (or hide with character format — preserves search in “source mode”; TBD).
  5. Register frame ID linked to source offset for refresh.

- **Refresh triggers:** user command; optional on paragraph style change (font size).

Details: [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md).

## Microsoft Word (later)

Same **canonical source**; different **renderer**:

- Subscript / EQ fields (睡人亭 / ふること) — no LO frame parity.
- Word plugin reads the same `mapping.json`; does not read LO frames.

## OpenOffice

Test after LibreOffice extension works; UNO likely similar.

## Interoperability expectations

| Action | Expectation |
|--------|-------------|
| Edit in LibreOffice | Full fidelity |
| PDF from LibreOffice | Full fidelity |
| Copy to gedit / OnlyOffice | **Plain text only** — use **Copy as plain text** or keep canonical marks visible |
| Search `說者` with frames inserted | **Fails** — search `說` or use **Show source** |
| git diff | Canonical `.txt` sidecar or visible `㆒㆑` in ODT |

## Non-goals (v1)

- Automatic 書き下し文
- Linguistic disambiguation when user misplaced marks
- OnlyOffice frame compatibility
- Auto-render on every IME commit

## Testing

1. Compound mark: `說㆒㆑者` → render → visual 一/レ at 說; plain `者` follows.
2. Vertical 縦書き paragraph.
3. Insert/delete before 說 — frame still attached.
4. Refresh after 12 pt → 14 pt paragraph change.
5. Copy as plain text → `說㆒㆑者` on clipboard.
