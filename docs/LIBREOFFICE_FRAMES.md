# LibreOffice: image + frame kaeriten rendering

Hands-on prototyping (2026) confirmed that LibreOffice Writer can display **compound kaeriten** (e.g. 一二点 + レ stacked) at a level acceptable for scholarly use. The current default is an **as-character SVG image**: the extension paints the kaeriten cluster itself, then inserts it as a Writer graphic with `MARINAMOJI:source=...` metadata. Borderless text frames remain as a fallback.

Word parallel tests: [WORD_FINDINGS.md](WORD_FINDINGS.md). Shared architecture: [ARCHITECTURE.md](ARCHITECTURE.md).

## Approaches tested

### 1. Ruby (Asian phonetic guide)

| | |
|---|---|
| **Result** | Technically works; visually poor |
| **Problems** | Mark too far from base character; looks like furigana, not kaeriten; cannot naturally stack compound marks |
| **Decision** | **Reject** as primary solution |

### 2. Character styling (Unicode + subscript + size)

| | |
|---|---|
| **Tried** | Full-size ㆑, subscript, reduced font size, spacing tweaks |
| **Result** | Acceptable for simple レ alone |
| **Problems** | Unconvincing for compound kaeriten; negative spacing ineffective; still “ordinary text” |
| **Decision** | **Fallback** only (quick export, simple marks) |

### 3. Anchored borderless frame (fallback)

Tiny **borderless frame** anchored **as character**, containing stacked glyphs (e.g. 一 over レ).

| Parameter | Starting value |
|-----------|----------------|
| Anchor | As character (to preceding kanji) |
| Frame border | None |
| Frame spacing (margins) | 0 — `LeftMargin` … `BottomMargin` in UNO |
| Frame padding (border distance) | 0 — `BorderDistance` / `*BorderDistance` in UNO |
| Frame on line | `VertOrient` = CHAR_BOTTOM (not BOTTOM) |
| Content in frame | `TextVerticalAdjust` = BOTTOM; height from glyph count |
| Vertical nudge | `vert_orient_position_hmm` (1/100 mm; negative raises) |
| Font size | `font_size_ratio` × host kanji height (fallback `font_size_pt`) |
| Typical stack | Top → bottom per mark order in source (e.g. `㆒㆑` → 一 / レ) |

| | |
|---|---|
| **Result** | Convincing for simple and compound kaeriten; survives editing; works in **vertical text** |
| **Decision** | **Fallback**; vertical compounds exposed Writer text-layout limits (line wrapping, ineffective kerning) |

### 4. As-character SVG image (current default)

Tiny **SVG graphic** anchored **as character**, containing painted glyphs rather than Writer text. This mirrors the Word inline-picture approach while avoiding an added Pillow dependency.

| Parameter | Starting value |
|-----------|----------------|
| Anchor | As character (after preceding kanji) |
| Image source | Runtime SVG file loaded into a `TextGraphicObject` |
| Source metadata | `Description = MARINAMOJI:source=...` |
| Font size | `glyph_ratio` / `compound_glyph_ratio` × host kanji height |
| Compound spacing | `compound_line_gap_ratio`, or `compound_touch` + `compound_touch_overlap_ratio` |
| Vertical side | `vertical_vert_orient = char_bottom` → left of the vertical column |

| | |
|---|---|
| **Result** | Compounds are painted, so no Writer-internal line wrap; touching is deterministic |
| **Decision** | **Primary render primitive** for LibreOffice (`libreoffice_primary: "inline_image"`) |

## Stability tests

| Test | Result | Notes |
|------|--------|-------|
| Insert/delete text **before** annotated character | Pass | Frame stays attached |
| Search for base kanji alone (`說`) | Pass | |
| Search for base + following plain text (`說者`) | **Fail** | Frame sits **between** characters in text stream — expected |
| Copy/paste inside LibreOffice | Pass | Annotation preserved |
| Copy/paste to plain text (gedit) | **Fail** | Only underlying text; frames lost |
| Copy/paste to OnlyOffice | **Fail** | Frame object not preserved |
| Paragraph font 12 pt → 14 pt | Pass | **Refresh rendering** rescales from host kanji / paragraph style |

## Conclusions

1. **LibreOffice can render professional kaeriten**, including compound stacks — images avoid nested Writer text-layout problems.
2. **LibreOffice has no native kaeriten type** (unlike ruby for furigana). The extension must **create and manage** its own annotation objects.
3. **Frames are a rendered view**, not the source of truth. Canonical meaning stays in Unicode (`說㆒㆑者`).
4. Users **format manually** (**Format kaeriten**); they **edit source**, not frame contents.

## Implementation notes (UNO)

- One image or frame per **mark cluster** after a base character (see [CONVENTIONS.md](CONVENTIONS.md#compound-kaeriten)).
- **Image renderer (default):** `libreoffice_primary: "inline_image"` inserts a `com.sun.star.text.TextGraphicObject`. `_svg_for_marks()` paints the display glyphs into SVG coordinates; `_insert_graphic()` loads that SVG through `GraphicProvider`, stores `MARINAMOJI:source=...` in the object's description, and anchors the graphic as a character.
- **Compound touching:** `libreoffice_image.compound_touch` uses the same idea as Word: when true, stack gap becomes `-cell * compound_touch_overlap_ratio`. Because this is applied in SVG geometry, it does not depend on LibreOffice `CharKerning` or vertical text line wrapping.
- **Writing direction (縦書き):** `_is_vertical_writing()` reads the paragraph `WritingMode` (falling back to the page style) and treats `TB_RL`/`TB_LR` as vertical. For an as-character view the perpendicular `VertOrient` axis rotates 90° in vertical text, so it selects the **column side**: horizontal uses `CHAR_BOTTOM` (lower-left, traditional); vertical uses `vertical_vert_orient` (mapping, default `char_bottom` → **left** of the column, traditional kanbun kaeriten beside okurigana on the right). Use `char_top` for the right side, or nudge with `vertical_orient_position_hmm`.
- **Page direction toggle:** `toggle_page_writing_mode()` changes the current page style's `WritingMode` between `LR_TB` (horizontal left-to-right) and `TB_RL` (vertical right-to-left), matching the setting in Writer's page-style dialog. After changing the style it refreshes existing rendered kaeriten views so placement follows the new direction.
- **Vertical frame layout (flush + no line break):** in 縦書き the frame's own `WritingMode` is set to `TB_RL` so compound glyphs stack down a **single column** — `frame_text()` joins them with no newline (`一レ`), instead of the horizontal `\n` stack. `vertical_box_hmm()` then sizes the box: width = column thickness (`vertical_box_width_factor`, default 1.18 em — a touch over 1 em so the glyph isn't **clipped on the right**, since in vertical text the column thickness is the line spacing and must match the width); height = *n* ems down the column (`vertical_box_height_factor`), minus the compound kern, so it hugs the marks with no empty space below. Compound spacing is tightened with `CharKerning` = `vertical_glyph_kern_hmm` (default −40 = −0.4 mm; more negative = tighter). Content is centered. Horizontal text keeps the newline stack and the bottom-anchored, taller box. `Refresh rendering` rewrites existing frames' text + size + kern, so older compounds and over-tall boxes pick up the new layout.
- **Render finds marks even when frames exist:** `_collect_mark_runs()` enumerates paragraphs → text portions (skipping `Frame` portions) instead of doing `goRight` offset arithmetic over `work_range.getString()`. An as-character frame is its own portion that adds no characters to `getString()` but still counts as one cursor position, so the old offset approach desynced after the first render and **skipped/misplaced** later kaeriten. Walking portions keeps every `goRight` inside a single frame-free run; runs are processed last→first so edits don't shift the live cursors still pending.
- On **Format kaeriten**, hide or remove Unicode marks from visible flow and insert frame at anchor.
- **Refresh rendering** redraws images and rebuilds/styling legacy frames when source marks or paragraph font size change.
- **Optional** editor-local tags (e.g. frame name `marinaMoji:kaeriten:<id>`) for finding objects on refresh — **not** for TEI/export semantics. See [ARCHITECTURE.md](ARCHITECTURE.md#metadata-and-export).
- Do **not** auto-format on every keystroke in v1.
- **Toolbar** (v0.2.3+): `OfficeToolBar` in `Addons.xcu`; enable via **View → Toolbars → marinaMoji**.
- **Toolbar only** (v0.3.5+): no menu bar; **Copy plain text** on the clipboard. Optional `install.sh` for Tools → Macros / APSO.

## Related

- [ARCHITECTURE.md](ARCHITECTURE.md) — source vs view layers
- [WORD_FINDINGS.md](WORD_FINDINGS.md) — Word textbox parallel
- [TARGET_LAYOUT.md](TARGET_LAYOUT.md) — LO primary vs Word textboxes
- [ROADMAP.md](ROADMAP.md) — phased extension work
