# Word add-in: what we tried (2026)

Chronicle of **Office.js** experiments for marinaMoji Kaeriten on **Word for Mac**, during hands-on debugging with Daniel (May 2026). This supplements the earlier manual tests in [WORD_FINDINGS.md](WORD_FINDINGS.md) and the research notes in [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md).

**LibreOffice** (working daily driver) inserts a borderless **frame anchored as character** after the base kanji, then removes the Unicode marks from the line. Word has no equivalent API; everything below is an attempt to approximate that behaviour.

**Current code** (plugin/word/, Mac QA ongoing): **OOXML `wp:inline` text boxes** as the default ([mapping.json](../mapping.json) `word_primary: ooxml`) — atomic cluster replace via `insertOoxml`. Fallback: content controls / inline `insertTextBox` when `word_mac_use_ooxml: false`.

---

## Model we keep everywhere

| Layer | What it is |
|-------|------------|
| **Source** | Visible Unicode in the document: `漢㆒㆑字` (typed with marinaMoji) |
| **View** | Small glyphs (一, レ, 上, …) beside the annotated kanji — disposable |
| **Commands** | Render → view; Unrender → restore Unicode marks; Refresh → rebuild view from source |

Users edit **source marks**, not the view. See [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Approaches rejected early (Word + LO)

Documented fully in [WORD_FINDINGS.md](WORD_FINDINGS.md):

- **Ruby / Phonetic Guide** — looks like furigana, not kaeriten.
- **Plain subscript / small characters only** — OK for a single レ; not acceptable for compound stacks.

---

## Renderer A: Rich-text content controls

**Idea:** Insert a locked **content control** immediately after the base kanji; store `MARINAMOJI:source=㆑` in the Tag; show display glyph **レ** inside at reduced font size. Closest built-in inline object in Word.

| Attempt | Result on Word Mac |
|--------|---------------------|
| `insertAfter` base kanji | Works for insertion point; frame often **invisible** |
| `appearance: boundingBox` + tint | Sometimes shows a box briefly; often **unwraps** to plain small text |
| `cannotEdit: true` | Intended to lock view; may contribute to unwrap |
| Compound: soft line breaks (`\u000b`, Shift+Enter) | Needed to stack 一 / 上 in **one** control |
| Compound: `insertParagraph` / `<br>` | **Splits across lines** or breaks layout |
| Compound: `insertOoxml` / `insertHtml` with `<w:p>` | **Corrupts document** (“problem with its content”, ~column 76) |
| Compound: `horizontalOnly` join (`一上` one line) | Avoids corruption but **wrong layout** (not stacked) |
| Multi-strategy fill (try break → catch → clear → retry) | On failure, cleanup called `cc.delete(false)` → **control removed**, small glyphs **left behind** |
| Single `insertText` fill only | Safer; current direction |

**Observed behaviour:** Render often ends with **small レ/一 beside the kanji but no visible box** — the semantic goal (compact mark beside kanji) is partly met, but not the LibreOffice-style frame.

**Code:** `plugin/word/src/render.js` (`insertContentControlAfterBase`, `fillContentControlGlyphs`, `insertKaeritenView`).

---

## Renderer B: Floating text boxes (`insertTextBox`)

**Idea:** Use **WordApiDesktop 1.2** [`Paragraph.insertTextBox`](https://learn.microsoft.com/en-us/javascript/api/word/word.paragraph?view=word-js-preview#word-word-paragraph-inserttextbox-method) — borderless box, stacked glyphs inside — similar to LO frames ([WORD_FINDINGS.md](WORD_FINDINGS.md) manual experiments).

**Microsoft docs:** `insertTextBox` **inserts a floating text box** (default geometry often `left:0`, `top:0`). That is not the same as LibreOffice “anchor as character”; it is closer to OOXML **anchored** drawings (`wp:anchor`), not **`wp:inline`**.

| Attempt | Result on Word Mac |
|--------|---------------------|
| Default `left: 0`, `top: 0` on insert | Box at **left margin** of page — **left of the kanji**, not beside it |
| Anchor at `baseRange.getRange(End)` | Still wrong; insert anchors at **beginning** of passed range |
| Anchor at **start of first mark** (`insertBefore` mark) | No visible change |
| After insert: `relativeHorizontalPosition: Character`, `left: 0` | **Single** mark sometimes **closer** to correct; still unreliable |
| `left ≈ 1 em` nudge after Character anchor | Theoretical fix for “box left of glyph”; not sustained in testing |
| Strip marks **before** insert (LO order) | Correct workflow; positioning still wrong for floats |
| Compound: stacked lines in text box body | Separate from anchor issue; box position was the blocker |
| **縦書き (vertical text)** | Floats use **page-relative** coords; box on **wrong side** of column |
| Skip text box in vertical; use content control only | Vertical still problematic |

**Decision in code:** Text boxes are **off by default**. Enabled only if [mapping.json](../mapping.json) sets `"word_primary": "textbox"` (not the current default).

**Code:** `plugin/word/src/wordTextBox.js` (`anchorTextBoxToCharacter` targets **floating** shapes), `wordRenderOptions()` in `render.js`.

---

## Renderer D: OOXML `wp:inline` (`insertOoxml`) — Mac default (June 2026)

**Idea:** Replace the **entire cluster** in one step (`問㆒㆑` → `問` + inline drawing), matching the LibreOffice rule: one atomic unit, no `moveStart` / delete-then-insert.

| Piece | Role |
|--------|------|
| `buildClusterReplaceOoxml()` | `plugin/word/src/wordOoxml.js` — `pkg:package` with `wp:inline` + `wps:txbx` |
| `wp:docPr descr` | `MARINAMOJI:source=㆒㆑` for **Unrender** (same as shape alt text) |
| `mapping.json` | `word_primary: ooxml`, `word_mac_use_ooxml: true` |

**Risks:** Earlier tests showed **document corruption** when OOXML included extra `<w:p>` inside content controls. This path replaces **document text** only; if Word reports “problem with its content”, revert `word_primary` to `content_control`.

**Safeguards (June 2026):** `wordOoxmlProbe.js` — structural checks, then `insertOoxml` at **document end** (probe) and delete before replacing the cluster (`word_mac_ooxml_probe_with_word`). Word has no validate-only API; probe + API fallback is the practical guard.

**Code:** `renderClusterWithOoxml()` in `render.js`, `probeOoxmlWithWord()` in `wordOoxmlProbe.js`.

---

## Renderer C: Inline text box (`textWrap.type = inline`) — implemented, QA pending

**Idea (June 2026, from API review):** After `insertTextBox`, set [`shape.textWrap.type = Word.ShapeTextWrapType.inline`](https://learn.microsoft.com/en-us/javascript/api/word/word.shapetextwraptype?view=word-js-preview) (“Places the shape **in line with text**”). That is the Office.js equivalent of flowing with the paragraph — much closer to LO **frame anchored as character** / OOXML **`wp:inline`** than Renderer B’s float + `relativeHorizontalPosition: Character` + `left`/`top` nudges.

**Microsoft docs (inline shapes):** On [`Word.Shape`](https://learn.microsoft.com/en-us/javascript/api/word/word.shape?view=word-js-preview), `left`, `top`, and `relativeHorizontalPosition` **return 0 and cannot be set** for inline shapes. Renderer C **does not** call `anchorTextBoxToCharacter()`; sizing is only `width`/`height` on insert.

| Step | Status |
|------|--------|
| Insert at collapsed range after base kanji (same as LO strip-then-insert order) | ✅ |
| `textWrap.type = inline` immediately after insert | ✅ |
| Borderless box + stacked glyphs in `shape.body` | ✅ (`fillTextBoxGlyphs`) |
| Metadata: `altTextDescription = MARINAMOJI:source=…` (same as Renderer B) | ✅ |
| Unrender / Refresh via shape scan + bookmarks | ✅ (same shape path as B) |
| QA: horizontal 横書き — mark moves with line break | ⏳ |
| QA: Word Mac + Word Windows (`WordApiDesktop` 1.2) | ⏳ |
| QA: 縦書き | ⏳ (skipped in code; falls back to content control) |

**Spike checklist (one cluster `說㆒㆑`):**

1. Require `Office.context.requirements.isSetSupported("WordApiDesktop", "1.2")`.
2. `insertTextBox("", { width, height })` at gap after 說.
3. `shape.textWrap.type = Word.ShapeTextWrapType.inline`; `await context.sync()`.
4. Do **not** set `relativeHorizontalPosition`, `left`, or `top`.
5. Compare screenshot to LO frame; verify line-wrap behaviour.
6. If inline fails on Mac, log `shape.textWrap.type` after insert and consider [`insertOoxml`](https://learn.microsoft.com/en-us/javascript/api/word/word.paragraph?view=word-js-preview#word-word-paragraph-insertooxml-method) (fragile; see Renderer A OOXML corruption).

**Official samples:** [manage-shapes-text-boxes.yaml](https://github.com/OfficeDev/office-js-snippets/blob/prod/samples/word/45-shapes/manage-shapes-text-boxes.yaml) (wrap examples use `square`; extend with `inline`).

**Code:** `insertKaeritenInlineTextBox()` in `plugin/word/src/wordTextBox.js`.

**Mac default (2026-06):** When `word_mac_prefer_inline_textbox` is true (default in [mapping.json](../mapping.json)), Word on Mac uses inline text boxes even if `word_primary` is `content_control`. Inline path: set `textWrap` **before** frame styling; fixed `width`/`height` + `autoSize: none`. **OOXML default:** `wp:inline`, zero `bodyPr` insets, `a:noFill` + no outline (publication-safe). **Optional hack:** `word_mac_force_solid_fill` + `word_mac_fill_color` (e.g. `FFFFFF`) + `word_mac_no_outline` — try if Mac still flattens; document as workaround, not the real fix (colour must not be required for correctness). Content-control fallback on Mac uses `appearance: tags` (not `boundingBox` / `cannotEdit`, which unwrap).

**LO parity (2026-06):** Render finds the **whole cluster** (`searchClusterOccurrences`), deletes the **marks run** with `marksRangeAfterBase` + `delete` (no `moveStart`/`moveEnd`), then inserts the view at `baseRange.getRange(End)` (`說` + box + `者`). Font size and margins apply to `shape.body.getRange()` (TextFrame text), not the shape wrapper. Mac may still spill plain glyphs — `clearPlainTextBetweenBaseAndShape` uses `expandTo` only. Shared helpers: `plugin/word/src/wordRange.js`.

---

## Renderer E: Inline pictures (`insertInlinePictureFromBase64`) — Mac default (June 2026)

**Why (the turning point):** Every renderer above asks Word for Mac to preserve a **live view object** — a content control, a floating/inline text box, or an OOXML `wp:inline` drawing. Word for Mac **flattens, unwraps, or corrupts** all of them, and the round-trip (Unrender) kept failing no matter how many times we patched the bookmark / `seenMarks` logic. Inline pictures are different: they are a **first-class Office.js object** that Word for Mac actually keeps across save/reload, they **flow with the text** like a character, and they **reliably retain `altTextDescription`**.

**Idea:** Draw the mark cluster (single レ, or a stacked 一/レ) on an off-screen `<canvas>` in the task-pane webview — which has the system CJK fonts — export it to a base64 PNG, and insert it **in place of the marks run** via [`Range.insertInlinePictureFromBase64`](https://learn.microsoft.com/en-us/javascript/api/word/word.range?view=word-js-preview#word-word-range-insertinlinepicturefrombase64-member(1)). Compound stacking is trivial because *we* paint the glyphs; we never fight Word's layout engine.

| Command | How |
|---------|-----|
| **Render** | `問㆒㆑` → `問` + inline PNG; alt text `MARINAMOJI:kaeriten:id=…;source=㆒㆑` |
| **Unrender** | Walk `body.inlinePictures`, read alt text, `getRange("Whole").insertText(marks, Replace)` |
| **Refresh** | Redraw PNG at current host font size; replace picture in place |
| **Export** | Read source marks from alt text; picture shows as `\uFFFC` in text, spliced to `問㆒㆑` (no document mutation) |

**Geometry:** each glyph cell ≈ half an em (`glyph_ratio`, default 0.5) of the base kanji's font; a single mark is one cell, a compound stack is one column of N cells (or a row if `compound_layout: "row"`). Drawn at `supersample`× (default 4) for crisp print, then sized in points via `pic.width`/`pic.height`. Background is transparent (publication-safe); `color` defaults to black.

**Requirement set:** `WordApi 1.2` (`insertInlinePictureFromBase64`) + `1.1` (`body.inlinePictures`, `altTextDescription`). `wordHasInlinePictureApi()` guards the path; falls back to the previous renderer if unavailable.

**Trade-off:** the view is a raster image, so it is not selectable text and not searchable — but the view is **disposable** (always re-derived from the source marks), and the source round-trips perfectly via the alt text. Accessibility/search live on the **source**, not the view.

**Code:** `plugin/word/src/wordInlinePicture.js` (`drawKaeritenImage`, `insertKaeritenInlinePicture`, `listMarinaMojiInlinePictures`, `unrenderOneInlinePicture`, `refreshInlinePicture`); wired in `render.js` (`renderClusterWithInlinePicture`, plus unrender/refresh/export). Config: [mapping.json](../mapping.json) `word_primary: "inline_picture"` + `word_inline_picture` block.

**Revert:** set `word_primary` back to `ooxml` (or `content_control`) in [mapping.json](../mapping.json) to use the earlier renderers.

---

## Placement and cluster handling (both renderers)

| Attempt | Notes |
|--------|--------|
| Search full string `漢㆒㆖` | Word search often **fails** on multi-codepoint mark string |
| Search `漢㆒` only | Cluster too short → only first mark stripped |
| Find each mark **in order** after base (`marksRangeAfterBase`) | Needed for compound |
| `expandTo` last mark | Sometimes works; per-char search more reliable |
| `getRange(End)` for insertion gap | Use **only** `baseRange.getRange(End)` — do **not** use VBA-style `moveStart`/`moveEnd` (not reliable Office.js on Mac) |
| Index-based `rangeAtTextOffsets` | **Removed** — use search + `expandTo` per mark/glyph (`wordRange.js`) |
| Render **back-to-front** in selection | Avoid index shift when deleting marks |

**Code:** `searchClusterOccurrences`, `deleteMarksFromCluster`, `wordRange.js` (`marksRangeAfterBase`, `insertPointAfterBase`) in `render.js`.

---

## Vertical layout (縦書き)

| Attempt | Notes |
|--------|--------|
| Same floating text box + Character anchor | Tall empty box **left of column**; marks stray |
| Detect `font.orientation` (VerticalFarEast, etc.) | Skip text box; force content control path |
| Compound in vertical: row layout (`一上`) vs stack | Row beside glyph in column |
| `ShapeTextOrientation` horizontal inside box | Experimental; float position still wrong |

**Status:** Vertical QA **not passed**. Horizontal is the tested case.

**Code:** `plugin/word/src/wordLayout.js`.

---

## Unrender: what we tried

| Attempt | Problem |
|--------|---------|
| Empty selection → scan **whole document** | Too aggressive |
| Match any small **レ / 一 / 上** by font size + mapping | **Deleted unrelated text** (“Unrender deletes everything”) |
| `cc.delete(false)` after failed fill | Removes control **and** content; leaves orphan small text or wipes text |
| `insertBefore` + `cc.delete(false)` | Fragile on Mac; wrong neighbour text |
| `insertReplace` with marks + `cc.delete(true)` | **Current** for tagged controls |
| Require **selection** for Unrender | Avoids silent full-doc scan |
| Only touch controls with **`MARINAMOJI:source=`** tag or mark-only Title | No guesswork from glyph shape |
| Hidden bookmark `_MMK_<hex>…` per view | Lets Unrender find glyphs when **CC wrapper is gone** |
| Scan **all document** bookmarks (not only `getBookmarks` on selection) | Mac often omitted `_MMK_` from selection-scoped bookmark list |
| Orphan fallback: exact display-glyph match + font ≤ ~42% of base | Only when CC/shape/bookmark all missing; avoids blind “any small レ” |
| Text box: `shape.select` + `insertText` | `select` can grab **too much** text; guarded by selection length |

**Observed:** After Render, **no box** and Unrender finds **nothing** → CC already unwrapped; use bookmark scan + orphan fallback (2026-06).

**Code:** `unrenderKaeritenDocument`, `unrenderOneControl`, `listMarinaMojiBookmarks` in `render.js`.

---

## Infrastructure / API pitfalls (Mac)

| Issue | Mitigation |
|-------|------------|
| `Word.Units.character` undefined | String literals via `wordEnums.js` |
| `paragraphFormat` on content control | Avoid; font-only styling |
| HTTPS + `127.0.0.1:3000` for sideload | mkcert; see [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) |
| Compléments browser preview | Office.js often **never connects** — use ribbon task pane |
| Selection required for Render | `getWorkRangeForRender` — avoids silent failure |

---

## OOXML vocabulary (Word vs LibreOffice)

| Term in conversation | LibreOffice | Word OOXML (approx.) | marinaMoji today |
|----------------------|-------------|----------------------|------------------|
| Anchor as character | UNO frame `anchor as character` | `wp:inline` drawing | CC (inline text); LO frames |
| Floating box beside text | Floating frame | `wp:anchor` drawing | Renderer B (`insertTextBox` default) |
| In-flow small glyphs | — | Plain runs / content control | Renderer A (default) |

We do **not** author `wp:anchor` or `wp:inline` by hand in the add-in; Word generates XML from Office.js calls unless we use `insertOoxml`.

---

## Summary table

| Approach | Beside kanji (horizontal) | Compound | 縦書き | Unrender reliable | LO-like box |
|----------|---------------------------|----------|--------|-------------------|-------------|
| Content control (bounding box) | Partial (small text) | Fragile | Untested | Tag + bookmark | Rarely visible |
| Content control (plain inline) | Partial | Fragile | Untested | Tag + bookmark | No |
| Floating text box (Renderer B) | Poor | Poor | Poor | Alt-text on shape | Briefly / wrong place |
| Inline text box (`textWrap.inline`) | Flattens on Mac | Flattens | ⏳ | Unreliable | Briefly |
| OOXML `wp:inline` (Renderer D) | Flattens / corrupts | Flattens | No | Unreliable | Sometimes |
| **Inline picture (Renderer E)** | **Yes (image)** | **Yes (painted)** | **⏳** | **Yes (alt text)** | **Yes (image)** |
| **LO frames** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** |

---

## Current defaults (code)

```json
"word_primary": "content_control"
```

in [mapping.json](../mapping.json). Implementation files:

| File | Role |
|------|------|
| [plugin/word/src/render.js](../word/src/render.js) | Render / Unrender / Refresh |
| [plugin/word/src/wordTextBox.js](../word/src/wordTextBox.js) | Optional text box renderer |
| [plugin/word/src/wordLayout.js](../word/src/wordLayout.js) | Vertical detection |
| [plugin/word/src/exportCore.js](../word/src/exportCore.js) | Clusters, bookmarks, export |

---

## What would be worth trying next

Prioritized for future sessions:

1. **Renderer C spike:** `insertTextBox` + `textWrap.type = inline` (see above) — best MS-documented path toward LO “as character” without raw OOXML.
2. **Pragmatic v0.1:** Keep content controls; improve **Unrender/Refresh** + bookmarks when the CC wrapper vanishes on Mac.
3. **Word for Windows:** Check whether content controls keep a visible bounding box more reliably than Mac.
4. **OOXML:** Custom `wp:inline` via `insertOoxml` only if Renderer C fails (high effort; Renderer A showed `<w:p>` inside CC corrupts files).
5. **Field codes** or **style-based** marks (no wrapper) with metadata in custom style names.
6. **Do not prioritize:** More `relativeHorizontalPosition: Character` + `left`/`top` tuning on **floating** boxes — that fights the default `insertTextBox` model per Microsoft docs.

---

## Related docs

- [WORD_FINDINGS.md](WORD_FINDINGS.md) — product-level conclusions (ruby, frames vs textboxes)
- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) — build, sideload, HTTPS
- [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md) — requirement sets, distribution
- [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md) — what “working” looks like
- [word/README.md](../word/README.md) — npm scripts
