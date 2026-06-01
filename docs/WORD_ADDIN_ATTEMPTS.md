# Word add-in: what we tried (2026)

Chronicle of **Office.js** experiments for marinaMoji Kaeriten on **Word for Mac**, during hands-on debugging with Daniel (May 2026). This supplements the earlier manual tests in [WORD_FINDINGS.md](WORD_FINDINGS.md) and the research notes in [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md).

**LibreOffice** (working daily driver) inserts a borderless **frame anchored as character** after the base kanji, then removes the Unicode marks from the line. Word has no equivalent API; everything below is an attempt to approximate that behaviour.

**Current code** (plugin/word/, not yet stable on Mac): **content controls** as the default renderer ([mapping.json](../mapping.json) `word_primary: content_control`), plus hidden **bookmarks** so Unrender can find views when Word strips the control wrapper.

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

**Idea:** Use **WordApiDesktop 1.2** `range.insertTextBox()` — borderless box, stacked glyphs inside — similar to LO frames ([WORD_FINDINGS.md](WORD_FINDINGS.md) manual experiments).

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

**Code:** `plugin/word/src/wordTextBox.js`, `wordRenderOptions()` in `render.js`.

---

## Placement and cluster handling (both renderers)

| Attempt | Notes |
|--------|--------|
| Search full string `漢㆒㆖` | Word search often **fails** on multi-codepoint mark string |
| Search `漢㆒` only | Cluster too short → only first mark stripped |
| Find each mark **in order** after base (`marksRangeAfterBase`) | Needed for compound |
| `expandTo` last mark | Sometimes works; per-char search more reliable |
| `getRange(End)` for insertion gap | **Unreliable on Mac** → `moveEnd` / `moveStart` collapse workaround |
| Render **back-to-front** in selection | Avoid index shift when deleting marks |

**Code:** `searchClusterOccurrences`, `stripMarksFromCluster`, `anchorAfterBaseKanji`, `collapsedRangeAfterKanji` in `render.js`.

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
| Text box: `shape.select` + `insertText` | `select` can grab **too much** text; guarded by selection length |

**Observed:** After Render, **no box** and Unrender finds **nothing** → CC already unwrapped; bookmark path must run (newer code).

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

## Summary table

| Approach | Beside kanji (horizontal) | Compound | 縦書き | Unrender reliable | LO-like box |
|----------|---------------------------|----------|--------|-------------------|-------------|
| Content control (bounding box) | Partial (small text) | Fragile | Untested | Tag + bookmark | Rarely visible |
| Content control (plain inline) | Partial | Fragile | Untested | Tag + bookmark | No |
| Floating text box | Poor | Poor | Poor | Alt-text on shape | Briefly / wrong place |
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

Not implemented; listed for future sessions:

1. **OOXML** custom anchor outside Office.js high-level API (high effort, fragile).
2. **Word for Windows** only — check if content controls keep bounding box more reliably.
3. **Accept inline small glyphs** as the Mac “view” and improve **Unrender/Refresh** only (pragmatic v0.1).
4. **Field codes** or **style-based** marks (no wrapper) with metadata in `STYLEREF` / custom style names.
5. Re-test **text box** after a confirmed **Character** anchor with measured `left` from host font metrics.

---

## Related docs

- [WORD_FINDINGS.md](WORD_FINDINGS.md) — product-level conclusions (ruby, frames vs textboxes)
- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) — build, sideload, HTTPS
- [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md) — requirement sets, distribution
- [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md) — what “working” looks like
- [word/README.md](../word/README.md) — npm scripts
