# Tweaking kaeriten size and appearance

The plugins do **not** yet have a slider in the Word / LibreOffice / ONLYOFFICE UI. Size, colour, and related layout live in one shared file: [`mapping.json`](../mapping.json).

Think of that file as a style sheet for kaeriten. You change a few numbers, rebuild or reinstall the plugin, then run **Render** again so existing marks pick up the new values.

## What “size” means

Each mark is drawn as a small glyph whose height is a **fraction of the host kanji**.

```text
kaeriten height  ≈  glyph_ratio  ×  paragraph font size
```

The default is **`0.42`** (42% of the kanji). That is a screen-and-PDF compromise: clearly smaller than the body text, still readable.

| Look you want | Typical `glyph_ratio` |
|---------------|----------------------|
| Closer to woodblock / movable type (often about **¼**) | `0.28`–`0.32` |
| **Default** (scholarly, but legible on a monitor) | `0.42` |
| A bit bolder on screen; closer to Word subscript | `0.45`–`0.50` |

Compound stacks (一 over レ, 上 over レ, …) use a **second**, slightly smaller ratio so the pile does not tower over the line:

- `glyph_ratio` — single marks (レ, 天, 一, …)
- `compound_glyph_ratio` — each glyph in a stack (default `0.34`)

If you shrink or enlarge singles, move the compound ratio in the same direction (keep it a little below the single-mark ratio).

**After you change body font size** (12 pt → 14 pt, etc.), you do not need to edit these ratios. Run **Render** again; the plugin scales from the current host size.

## Where to edit

Open [`mapping.json`](../mapping.json). The same idea is repeated in **three** image blocks so LibreOffice, Word, and ONLYOFFICE stay in sync. Change all three, or only the host you are testing.

| Host | JSON object | Keys |
|------|-------------|------|
| LibreOffice (default SVG images) | `rendering.libreoffice_image` | `glyph_ratio`, `compound_glyph_ratio`, `color` |
| Word (default inline PNG) | `rendering.word_inline_picture` | same, plus `below_baseline_em` (see below) |
| ONLYOFFICE (default inline PNG) | `rendering.onlyoffice_inline_image` | `glyph_ratio`, `compound_glyph_ratio`, `color` |

Example — woodblock-like singles on all three hosts:

```json
"glyph_ratio": 0.30,
"compound_glyph_ratio": 0.24
```

Fallback renderers (LibreOffice text frames, Word content controls, ONLYOFFICE inline text) use **`font_size_ratio`** instead of `glyph_ratio`. If you still use those paths, keep `0.42` (or `"12:5"`, which is the same fraction) in:

- `rendering.libreoffice_frame.font_size_ratio`
- `rendering.onlyoffice_inline.font_size_ratio`
- `rendering.word_content_control.font_size_ratio` / `word_inline_textbox.font_size_ratio`

## Colour

Traditional kunten uses the **same ink** as the body text. The mapping default is `"color": "#000000"`.

On Word, small transparent PNGs can look **medium gray** even when the file asks for black (anti-aliasing plus how Word composites pictures). If marks look washed out, try a slightly heavier fill first — `glyph_fill` (default `0.94`, range 0–1) — before changing hue. Keep `color` as black unless you have a house-style reason not to.

## Position (horizontal text)

In 横書き the mark sits after the kanji with its bottom edge on the **bottom line of the characters** (about 0.067 em below the baseline for Hiragino and Yu fonts), not hanging below them. It should not look like furigana (above the character).

**LibreOffice** anchors the image to the baseline and computes its offset from the cell, so it works the same at any font size. Two keys in `rendering.libreoffice_image`:

- `bottom_line_em` — distance from the baseline down to the characters' bottom line (default `0.067`).
- `font_bottom_line_em` — per-font overrides by family-name prefix (`"Songti SC": 0.156`). Songti sets its characters lower than the other fonts; add an entry for any font whose marks sit too high or low.
- `vert_orient_position_hmm` — extra nudge in 1/100 mm.

**Word** draws each mark as an inline picture and lowers it with a run position. Keys in `rendering.word_inline_picture`:

- `bottom_line_em` — distance from the baseline down to the characters' bottom line (default `0.06`).
- `font_bottom_line_em` — per-font overrides (`"Songti SC": 0.122`). The add-in reads the host font from the base character.
- `ink_inset_em` — how far the mark's ink sits above the bottom of its picture (`0.066`, from the ㆑ glyph).

The shift is `-(bottom_line_em + ink_inset_em) × font size`; `baseline_shift_pt` is only the fallback when `bottom_line_em` is absent. Word stores the position in half-points, so at 12 pt the mark can be off by up to 0.02 em.

## Position (vertical text, LibreOffice)

In 縦書き the marks stay in the column like small characters: each sits in its own slot right after its base character, and its box's **left edge is on the characters' left edge** (the same margin), not beside the column.

| Key (`rendering.libreoffice_image`) | Meaning |
|---|---|
| `vertical_left_em` | Sideways shift, in em, from the unadjusted position to the characters' left edge (default `0.328`) |
| `vertical_font_left_em` | Per-font overrides by family-name prefix (Songti SC `0.317`, Yu Gothic `0.357`, …) |
| `vertical_orient_position_hmm` | Extra sideways nudge in 1/100 mm (positive = right) |

The per-font values come from measuring renders (the mark box's left edge against the typical left edge of the characters' ink). A font whose ink starts further left or right than the others needs its own entry. LibreOffice anchors the in-line image by its right edge, so the offset also subtracts the difference between a single mark's width and the picture's.

## Position (vertical text, Word)

The marks stay in the column as inline pictures, with their box's left edge on the characters' left edge, whatever the picture's width (single mark, stack or row). Word centres every inline picture on one axis in the column, so the add-in shifts each by that axis's distance minus half its width. `rendering.word_inline_picture.vertical_center_em` (`0.458`) is that axis's distance from the characters' left edge; it was the same for the fonts tested (Hiragino, Yu, Songti).

## Apply the change

1. Save `mapping.json`.
2. Rebuild / reinstall the host you use (the file is **copied into** each plugin at build time; editing the repo copy alone does not update an already-installed add-in).
3. In the document, run **Render** (LibreOffice menu: **Format kaeriten** / **Refresh rendering**). Existing views refresh when the mapping fingerprint changes.

| Host | After editing `mapping.json` |
|------|------------------------------|
| LibreOffice | `cd libreoffice && ./build.sh`, then Extension Manager → remove old extension → add `dist/MarinaMojiKaeriten.oxt` → restart Writer |
| Word (local dev) | `cd word && ./build.sh`, keep `npm run serve` running, reload the task pane if needed |
| Word (GitHub Pages testers) | rebuild and publish `word/dist/` (see [GITHUB_PAGES.md](GITHUB_PAGES.md)); the add-in loads `mapping.json` from the hosted URL |
| ONLYOFFICE | `cd onlyoffice && ./build.sh && ./install-mac.sh`, then **quit and reopen** ONLYOFFICE |

There is no need to retype the Unicode marks (`㆝`, `㆑`, …). **Render** redraws the pictures from the same source.

## What not to change for size

Leave these unless you are changing **which characters** are drawn, not how big they are:

- `marks[].display_glyph` — レ vs ㆑, 天 vs ㆝, …
- `marks[].unicode` / shortcuts — IME input, not layout
- `word_primary` / `libreoffice_primary` — which renderer to use (image vs frame vs text box)

Do **not** drag-resize pictures or frames in the document. The next **Render** will put them back to the mapping size.

## Related

- [CONVENTIONS.md](CONVENTIONS.md) — typing order; edit source, not the picture
- [ARCHITECTURE.md](ARCHITECTURE.md) — source vs view; why Render rebuilds layout
- [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md) — LO image/frame parameters, including 縦書き
- [mapping.json](../mapping.json) — the file itself
