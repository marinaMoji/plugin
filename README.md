# marinaMoji Office plugins (planned)

Companion tools for [marinaMoji](https://github.com/marinaMoji/marinaMoji): turn IME output (Unicode Kanbun marks) into professionally laid-out kaeriten (返り点) in word processors—especially **compound** marks (e.g. 一 + レ).

## Problem

marinaMoji inserts **Unicode Kanbun** (e.g. `;r` → ㆑) for fast input. That text is correct for drafting and interchange, but LibreOffice and Word do not lay out those marks like printed kanbun unless a **renderer** builds proper annotation typography.

Font choice alone does not fix placement; the same U+3191 can look different sizes in gedit vs LibreOffice.

## Solution (validated on LibreOffice and Word)

**Two layers:**

| Layer | Content | Purpose |
|-------|---------|---------|
| **Canonical source** | `說㆒㆑者` (ordinary Unicode text) | marinaMoji input; search; git; copy plain to other apps |
| **Rendered view** | LO **SVG image**; Word **inline PNG picture**; ONLYOFFICE **inline PNG image** | Scholarly print layout; PDF; **not** the archival format |

Frames and textboxes are a **view**, not the source of truth. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

**LibreOffice (2026):** ruby rejected; subscript fallback only; **borderless frame** primary — [docs/LIBREOFFICE_FRAMES.md](docs/LIBREOFFICE_FRAMES.md).

**Microsoft Word (2026):** ruby and content controls rejected for final layout; **inline PNG picture** is the default renderer — [docs/WORD_FINDINGS.md](docs/WORD_FINDINGS.md), [docs/WORD_ADDIN_ATTEMPTS.md](docs/WORD_ADDIN_ATTEMPTS.md).

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
- **Copy plain text** reads canonical Unicode from the document (including marks recovered from rendered views). TEI/LaTeX export is **not** shipped in v1 — no single standard for kanbun markup in those formats.

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#metadata-and-export).

## Scope

| In scope (v1) | Later |
|---------------|-------|
| LO extension: frame render + refresh | Auto-format on save (optional) |
| Word add-in: inline picture render + refresh | Word Online QA |
| **Format kaeriten** + **Refresh** commands | 再読, okurigana |
| Canonical Unicode in document | |
| Render / Unrender / Refresh / Copy plain (all hosts) | |

| Out of scope (v1) | |
|-------------------|---|
| OnlyOffice frame parity (paste from LO) | |
| OnlyOffice plugin (inline image render + refresh) | |
| Hidden metadata as canonical semantics | |
| Auto-format while typing | |

## Related repo

- IME: `marinaMoji/src/data/preedit/kaeriten.tsv`
- Toolbar: `marinaMoji/src/unix/ibus/mozc_toolbar.cc`, `marinaMoji/src/mac/mozc_toolbar.mm`

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
| [docs/SELF_HOSTED_PUBLISHING_PLAN.md](docs/SELF_HOSTED_PUBLISHING_PLAN.md) | Step-by-step publish plan (LO, Word, ONLYOFFICE) |
| [docs/GITHUB_PAGES.md](docs/GITHUB_PAGES.md) | Host Word add-in on GitHub Pages |
| [docs/INSTALL-MAC-GATEKEEPER.md](docs/INSTALL-MAC-GATEKEEPER.md) | macOS Right-click → Open (unsigned downloads) |
| [onlyoffice/README.md](onlyoffice/README.md) | ONLYOFFICE plugin install and use |
| [docs/LIBREOFFICE_FRAMES.md](docs/LIBREOFFICE_FRAMES.md) | LO experiments and frame parameters |
| [docs/WORD_FINDINGS.md](docs/WORD_FINDINGS.md) | Word experiments (May–June 2026) |
| [docs/TARGET_LAYOUT.md](docs/TARGET_LAYOUT.md) | LO frames vs Word textboxes |
| [docs/CONVENTIONS.md](docs/CONVENTIONS.md) | Typing order; compound clusters; user workflow |
| [docs/STATUS.md](docs/STATUS.md) | Current state — pre-publish QA gate |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Phased build plan |
| [docs/BACKGROUND.md](docs/BACKGROUND.md) | Prior art survey |
| [docs/OTHER_HOSTS.md](docs/OTHER_HOSTS.md) | Google Docs, Word Online, and other hosts — expansion reflections |
| [docs/MARKDOWN_AND_RTF.md](docs/MARKDOWN_AND_RTF.md) | Markdown / HTML preview and Apple RTF / RTFD export study |
| [docs/RENDERING_IMPROVEMENTS.md](docs/RENDERING_IMPROVEMENTS.md) | Planned: OO inline images, Word whole-doc render, LO smart incremental render |
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

## Microsoft Word add-in (pre-release)

Inline-picture renderer; render / unrender / refresh / copy plain. **Pre-publish QA** and HTTPS hosting required before distribution. Dev: [word/README.md](word/README.md). Status: [docs/STATUS.md](docs/STATUS.md).

## ONLYOFFICE plugin (pre-release)

**End users (macOS):** download `marinamoji-kaeriten-onlyoffice-mac.dmg` from GitHub Releases.

```bash
cd onlyoffice
./build.sh
./install-mac.sh   # developers only
```

Plugins → **marinaMoji Kaeriten** sidebar.

## Status

See **[docs/STATUS.md](docs/STATUS.md)** for the full picture.

**All three plugins** — implementation complete for v1 (render, unrender, refresh, copy plain). **Pre-publish QA** on each host before GitHub/website release.

**LibreOffice** — recommended daily driver after QA (inline SVG images, vertical text, compound touching).

**Word** — inline pictures; developers use localhost + mkcert; end users need hosted `dist/`.

**ONLYOFFICE** — sidebar plugin; inline images; experimental parity with LO/Word.

**Export:** **Copy plain Unicode only.** TEI and LaTeX buttons removed — no consensus standard for kanbun in those formats.
