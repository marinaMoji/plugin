# marinaMoji Office plugins (planned)

Companion tools for [marinaMoji](../mozc): turn IME output (Unicode Kanbun marks) into professionally laid-out kaeriten (返り点) in word processors—especially **compound** marks (e.g. 一 + レ).

## Problem

marinaMoji inserts **Unicode Kanbun** (e.g. `;r` → ㆑) for fast input. That text is correct for drafting and interchange, but LibreOffice and Word do not lay out those marks like printed kanbun unless a **renderer** builds proper annotation typography.

Font choice alone does not fix placement; the same U+3191 can look different sizes in gedit vs LibreOffice.

## Solution (validated on LibreOffice)

**Two layers:**

| Layer | Content | Purpose |
|-------|---------|---------|
| **Canonical source** | `說㆒㆑者` (ordinary Unicode text) | marinaMoji input; search; git; TEI/LaTeX export; copy to other apps |
| **Rendered view** | Tiny **anchored frame** (一 / レ stacked) after `說` | Scholarly print layout in Writer; PDF |

Frames are a **view**, not the source of truth. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

LibreOffice prototyping showed:

- **Ruby** — rejected (looks like furigana).
- **Subscript only** — fallback for simple レ; not enough for compound kaeriten.
- **Borderless frame anchored as character** — **primary** renderer; works in vertical text.

Full test notes: [docs/LIBREOFFICE_FRAMES.md](docs/LIBREOFFICE_FRAMES.md).

## Workflow (v1)

1. Type with marinaMoji: `說㆒㆑者`
2. Run **Render kaeriten** (selection / paragraph / document)
3. Edit in Writer; use **Refresh rendering** after mark or style changes
4. **Copy as plain text** when leaving LibreOffice

Auto-render on every keystroke is **deferred** (undo, cursor, IME).

## Scope

| In scope (v1) | Later |
|---------------|-------|
| LO extension: frame render + refresh | Word renderer (EQ / subscript) |
| Canonical Unicode in document | Auto-render on save |
| Render / Show source / Copy plain | TEI, LaTeX export |
| Compound mark clusters | 再読, okurigana |

## Related repo

- IME: `mozc/src/data/preedit/kaeriten.tsv`
- Toolbar: `mozc/src/unix/ibus/mozc_toolbar.cc`

## Documentation

| Doc | Contents |
|-----|----------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Source vs view; commands; interoperability |
| [docs/LIBREOFFICE_FRAMES.md](docs/LIBREOFFICE_FRAMES.md) | LO experiments and frame parameters |
| [docs/TARGET_LAYOUT.md](docs/TARGET_LAYOUT.md) | LO frames vs Word fallbacks |
| [docs/CONVENTIONS.md](docs/CONVENTIONS.md) | Typing order; compound clusters |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Phased build plan |
| [docs/BACKGROUND.md](docs/BACKGROUND.md) | Prior art survey |
| [docs/SOURCES.md](docs/SOURCES.md) | Bibliography |
| [docs/UNICODE_AND_MARINAMOJI.md](docs/UNICODE_AND_MARINAMOJI.md) | `;` shortcuts ↔ code points |

## Shared data

- [mapping.json](mapping.json) — marks, display glyphs, render hints

## Status

**Documentation + LO render prototype validated** — extension (`.oxt`) not shipped yet.
=======
# plugin
Word processor plugin
