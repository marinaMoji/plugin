# marinaMoji Office plugins (planned)

Companion tools for [marinaMoji](https://github.com/marinaMoji/marinaMozc): turn IME output (Unicode Kanbun marks) into professionally laid-out kaeriten (返り点) in word processors—especially **compound** marks (e.g. 一 + レ).

## Problem

marinaMoji inserts **Unicode Kanbun** (e.g. `;r` → ㆑) for fast input. That text is correct for drafting and interchange, but LibreOffice and Word do not lay out those marks like printed kanbun unless a **renderer** builds proper annotation typography.

Font choice alone does not fix placement; the same U+3191 can look different sizes in gedit vs LibreOffice.

## Solution (validated on LibreOffice and Word)

**Two layers:**

| Layer | Content | Purpose |
|-------|---------|---------|
| **Canonical source** | `說㆒㆑者` (ordinary Unicode text) | marinaMoji input; search; git; TEI/LaTeX export; copy to other apps |
| **Rendered view** | Anchored **frame** (LO) or **textbox** (Word) with stacked glyphs | Scholarly print layout; PDF; **not** the archival format |

Frames and textboxes are a **view**, not the source of truth. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

**LibreOffice (2026):** ruby rejected; subscript fallback only; **borderless frame** primary — [docs/LIBREOFFICE_FRAMES.md](docs/LIBREOFFICE_FRAMES.md).

**Microsoft Word (2026):** same conclusions — ruby rejected; **anchored textbox** primary; users must edit source, not boxes — [docs/WORD_FINDINGS.md](docs/WORD_FINDINGS.md).

## Workflow (v1) — manual formatting only

1. Type with marinaMoji: `說㆒㆑者`
2. Run **Format kaeriten** (menu; same as *Render kaeriten* in docs) on selection / paragraph / document
3. Edit **source text** (`說㆒㆑者`), not the annotation objects
4. Run **Refresh rendering** after mark or paragraph style changes
5. **Copy as plain text** when leaving LibreOffice or Word

**Not in v1:** automatic format on every keystroke or IME commit (undo, cursor, and IME edge cases).

## Metadata and export

- **Meaning** lives in visible Unicode (`㆒㆑`), not in hidden Word/LO/OnlyOffice XML for v1.
- **Optional** editor-local IDs may link a frame/textbox to a position for refresh only.
- **TEI / LaTeX** export reads canonical text + [mapping.json](mapping.json).

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#metadata-and-export).

## Scope

| In scope (v1) | Later |
|---------------|-------|
| LO extension: frame render + refresh | Auto-format on save (optional) |
| Word add-in: content controls (dev; Mac QA pending) | Word textbox renderer (closer to manual experiments) |
| **Format kaeriten** + **Refresh** commands | 再読, okurigana |
| Canonical Unicode in document | |
| Show source / Copy plain / TEI / LaTeX (LO + Word) | |

| Out of scope (v1) | |
|-------------------|---|
| OnlyOffice frame parity (paste from LO) | |
| OnlyOffice plugin (inline controls, dev) | |
| Hidden metadata as canonical semantics | |
| Auto-format while typing | |

## Related repo

- IME: `marinaMozc/src/data/preedit/kaeriten.tsv`
- Toolbar: `marinaMozc/src/unix/ibus/mozc_toolbar.cc`, `marinaMozc/src/mac/mozc_toolbar.mm`

## Documentation

| Doc | Contents |
|-----|----------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Source vs view; metadata; commands; interoperability |
| [libreoffice/README.md](libreoffice/README.md) | LO extension build and install |
| [word/README.md](word/README.md) | Word add-in build and sideload |
| [docs/WORD_ADDIN_DEV.md](docs/WORD_ADDIN_DEV.md) | Word Mac dev status, resume checklist, troubleshooting |
| [docs/WORD_PLUGIN_RESEARCH.md](docs/WORD_PLUGIN_RESEARCH.md) | Word planning: Mac reality, certs, macros, parity |
| [docs/ONLYOFFICE.md](docs/ONLYOFFICE.md) | ONLYOFFICE role, limits, workflow |
| [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md) | GitHub/website releases, GUI installers, no App Store |
| [docs/INSTALL-MAC-GATEKEEPER.md](docs/INSTALL-MAC-GATEKEEPER.md) | macOS Right-click → Open (unsigned downloads) |
| [onlyoffice/README.md](onlyoffice/README.md) | ONLYOFFICE plugin install and use |
| [docs/LIBREOFFICE_FRAMES.md](docs/LIBREOFFICE_FRAMES.md) | LO experiments and frame parameters |
| [docs/WORD_FINDINGS.md](docs/WORD_FINDINGS.md) | Word experiments (May–June 2026) |
| [docs/TARGET_LAYOUT.md](docs/TARGET_LAYOUT.md) | LO frames vs Word textboxes |
| [docs/CONVENTIONS.md](docs/CONVENTIONS.md) | Typing order; compound clusters; user workflow |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Phased build plan |
| [docs/BACKGROUND.md](docs/BACKGROUND.md) | Prior art survey |
| [docs/SOURCES.md](docs/SOURCES.md) | Bibliography |
| [docs/UNICODE_AND_MARINAMOJI.md](docs/UNICODE_AND_MARINAMOJI.md) | `;` shortcuts ↔ code points |

## Shared data

- [mapping.json](mapping.json) — marks, display glyphs, render hints

## LibreOffice extension (v0.3.7 — alpha, recommended)

Source and build instructions: [libreoffice/README.md](libreoffice/README.md)

**End users (macOS):** download `marinamoji-kaeriten-libreoffice-mac.dmg` from GitHub Releases — no Terminal.

**Developers:**

```bash
cd libreoffice
./build.sh      # MarinaMojiKaeriten.oxt
./install.sh    # optional: copy Python macros (same as Mac installer)
```

## Microsoft Word add-in (parked)

The Word add-in is **excluded from git** until the Mac renderer is stable. See [docs/WORD_ADDIN_DEV.md](docs/WORD_ADDIN_DEV.md) to resume development.

## ONLYOFFICE plugin (v0.1.0 — alpha, experimental)

**End users (macOS):** download `marinamoji-kaeriten-onlyoffice-mac.dmg` from GitHub Releases.

```bash
cd onlyoffice
./build.sh
./install-mac.sh   # developers only
```

Plugins → **marinaMoji Kaeriten** sidebar.

## Status

**LibreOffice extension (alpha)** — render / unrender / refresh / clipboard export. **Use this for real work today.**

**ONLYOFFICE plugin (alpha, experimental)** — same commands via sidebar; inline content controls. Compound mark layout is imperfect.

**Word add-in (parked)** — development paused; not shipped in releases.
