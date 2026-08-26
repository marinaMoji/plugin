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

In 横書き the mark sits after the kanji, slightly **below the baseline**. That is intentional; it should not look like furigana (above the character).

Word’s image renderer also has `below_baseline_em` (default `0.42`). That is the empty slot under the line that the glyph sits in. If you change `glyph_ratio` a lot, set `below_baseline_em` to the **same number** so the mark does not float in leftover space or get clipped.

LibreOffice and ONLYOFFICE pin the image as a character at the bottom of the line; they do not use `below_baseline_em`.

縦書き uses a different side of the column (traditionally the **left**). See [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md) for `vertical_vert_orient` and related nudges.

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
