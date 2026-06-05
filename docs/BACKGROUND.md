# Background: computer kanbun markup today

## What “kanbun markup” means here

Following 篠原泰彦, *コンピューター上の漢文訓読表記法に関する現状と課題* (國學院中國學會報 65, 2024), we mean:

> Adding **返り点** and **送り仮名** (and related kunten) to a Chinese original on screen—not full syntactic analysis, not necessarily 書き下し文 generation.

marinaMoji solves **fast input** of mark symbols. This project solves **presentation** and **document engineering** in Office suites.

## Why not stop at Unicode?

Unicode block **Kanbun** (U+3190–U+319F) is ideal for:

- IME direct input (marinaMoji `;r`, `;1`, … — see [marinaMoji/marinaMoji](https://github.com/marinaMoji/marinaMoji))
- Plain-text interchange and corpus search

It is weak for:

- Compound stacks (一レ) as one typographic unit
- Placement in vertical layout
- Print-quality PDF without a renderer

**LibreOffice and Word prototyping (2026)** confirmed that **disposable view objects** (LO frames; Word content controls and text boxes) can produce acceptable compound kaeriten when **canonical Unicode source** (`說㆒㆑者`) stays authoritative and views are regenerated with a manual **Format kaeriten** command—not edited inside the views. Word’s next documented API path for LO-like “as character” placement is **`insertTextBox` + `textWrap.type = inline`** (not default floating insert). See [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md), [WORD_FINDINGS.md](WORD_FINDINGS.md), [WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md), [ARCHITECTURE.md](ARCHITECTURE.md).

## Existing approaches (summary)

| Approach | Idea | Strength | Weakness |
|----------|------|----------|----------|
| Manual Word subscript | レ/一/二 + ruby | Universal | Slow; weak on compounds |
| Word EQ / field codes | Positioned okurigana + レ | Fine control | Fragile |
| 訓点マクロ (千田大介) | Tag → convert | Batch | Two-step; 再読 unstable |
| 漢文エディタ | Excel tags → Word/HTML/TeX | Many outputs | Own syntax |
| 一太郎 文字パレット「漢文」 | Palette | Fast in 一太郎 | Mouse-heavy; lock-in |
| LaTeX `kunten2e` / `sfkanbun` | Markup → print | Publication | Not Word/LO |
| **marinaMoji + LO/Word views** | Unicode source + frame/textbox view | Keyboard + compounds; manual format | Per-host renderer; refresh from source |

篠原’s four recurring problems: hard install, tedious UI, unlike paper workflow, poor portability. marinaMoji addresses input tedium; **canonical Unicode + Copy as plain text** addresses portability; frames address typography inside LibreOffice.

## Where marinaMoji + this plugin fits

- **marinaMoji:** keyboard-first Unicode (`說㆒㆑者`).
- **Plugin:** **Render kaeriten** (manual) builds inline images/frames for print; **Refresh** rebuilds views; **Copy plain** reads canonical Unicode from source + `mapping.json`, not from hidden metadata or object pixels.
- **TeX:** still the path for camera-ready books; export from source layer.

We do not replace TeX in v1; we make Word Processor drafts and teaching materials feasible with compound kaeriten.
