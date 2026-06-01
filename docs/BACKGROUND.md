# Background: computer kanbun markup today

## What “kanbun markup” means here

Following 篠原泰彦, *コンピューター上の漢文訓読表記法に関する現状と課題* (國學院中國學會報 65, 2024), we mean:

> Adding **返り点** and **送り仮名** (and related kunten) to a Chinese original on screen—not full syntactic analysis, not necessarily 書き下し文 generation.

marinaMoji solves **fast input** of mark symbols. This project solves **presentation** and **document engineering** in Office suites.

## Why not stop at Unicode?

Unicode block **Kanbun** (U+3190–U+319F) is ideal for:

- IME direct input (marinaMoji `;r`, `;1`, …)
- Plain-text interchange and corpus search

It is weak for:

- Compound stacks (一レ) as one typographic unit
- Placement in vertical layout
- Print-quality PDF without a renderer

**LibreOffice prototyping (2026)** confirmed that a **frame-based renderer** can produce acceptable compound kaeriten; the remaining work is keeping **canonical source text** in sync with those frames. See [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md).

## Existing approaches (summary)

| Approach | Idea | Strength | Weakness |
|----------|------|----------|----------|
| Manual Word subscript | レ/一/二 + ruby | Universal | Slow; weak on compounds |
| Word EQ / field codes | Positioned okurigana + レ | Fine control | Fragile |
| 訓点マクロ (千田大介) | Tag → convert | Batch | Two-step; 再読 unstable |
| 漢文エディタ | Excel tags → Word/HTML/TeX | Many outputs | Own syntax |
| 一太郎 文字パレット「漢文」 | Palette | Fast in 一太郎 | Mouse-heavy; lock-in |
| LaTeX `kunten2e` / `sfkanbun` | Markup → print | Publication | Not Word/LO |
| **marinaMoji + LO frames** | Unicode source + frame view | Keyboard + compounds in LO | LO-specific render; sync work |

篠原’s four recurring problems: hard install, tedious UI, unlike paper workflow, poor portability. marinaMoji addresses input tedium; **canonical Unicode + Copy as plain text** addresses portability; frames address typography inside LibreOffice.

## Where marinaMoji + this plugin fits

- **marinaMoji:** keyboard-first Unicode (`說㆒㆑者`).
- **Plugin:** render to frames for print; export TEI/LaTeX from source, not from frame pixels.
- **TeX:** still the path for camera-ready books; export from source layer.

We do not replace TeX in v1; we make Word Processor drafts and teaching materials feasible with compound kaeriten.
