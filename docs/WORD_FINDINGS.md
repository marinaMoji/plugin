# Microsoft Word: kaeriten experiments (May–June 2026)

Hands-on tests on **Word for macOS**, aligned with LibreOffice prototyping. Conclusions match [ARCHITECTURE.md](ARCHITECTURE.md): **semantic source text + disposable visual view**.

## Starting question

Can MarinaMoji provide professionally formatted kaeriten in modern word processors, and what is the best technical approach?

We investigated LibreOffice, Microsoft Word, IME vs. document plugins, and semantic storage vs. visual rendering.

## Architectural conclusion

We started with:

```text
IME → formatted kaeriten
```

We ended with:

```text
IME → semantic text
Plugin → rendering
```

**Canonical representation:** `說㆒㆑者` in the document body (Unicode Kanbun from marinaMoji).

**Rendering layer:** anchored objects (textboxes in Word; frames in LibreOffice) that can always be **regenerated** from source.

> The rendered object is not data. The rendered object is a view.

## Approaches tested in Word

### Ruby / Phonetic Guide

| | |
|---|---|
| **Result** | Same problem as LibreOffice |
| **Problems** | Designed for pronunciation; looks like furigana, not kaeriten |
| **Decision** | **Reject** |

### Character styling (subscript, small Unicode)

| | |
|---|---|
| **Result** | Acceptable for isolated レ only |
| **Problems** | Inadequate for compound kaeriten; poor horizontal positioning |
| **Decision** | **Fallback** only |

### Content controls (add-in default)

Rich-text **content controls** with small glyphs and tag `MARINAMOJI:source=…`. On **Word for Mac** they often appear as **plain small inline text** with **no visible box** — the wrapper may appear briefly then unwrap. Compound marks can **split across document lines** when Word wraps. **Do not** insert raw `<w:p>` OOXML inside a control — it corrupts the file.

| | |
|---|---|
| **Result** | Small glyphs beside kanji sometimes OK; **visible frame rare** on Mac |
| **Problems** | Unrender needs tag or hidden bookmark if wrapper is lost |
| **Decision** | **Default in add-in** ([mapping.json](../mapping.json) `word_primary: content_control`) |

### Text boxes (`insertTextBox`, WordApiDesktop 1.2)

Manual experiments and add-in prototypes: tiny borderless text box after the kanji, stacked glyphs inside — in theory closer to LibreOffice frames.

| | |
|---|---|
| **Result** | Manual tests: visually convincing on some builds |
| **Add-in on Mac (floating path)** | Box often at **page left margin** or **left of kanji**, not in the gap after the base character |
| **Problems** | Microsoft documents `insertTextBox` as inserting a **floating** text box; our optional renderer then sets `relativeHorizontalPosition: Character` and manual `left`/`top` — still unreliable; 縦書き worse |
| **Decision** | **Optional only** (`word_primary: textbox`); not default |

**Not the same as OOXML `wp:anchor` in our code:** we never inject raw WordprocessingML. Floating `insertTextBox` is the API’s default; LibreOffice “anchor as character” is closer to **`wp:inline`** or Office.js **`textWrap.type = inline`** on a shape (documented but **not yet implemented** in the add-in).

| Renderer | Office.js | Status |
|----------|-----------|--------|
| A — content controls | `insertContentControl` | **Default** in add-in |
| B — floating text box | `insertTextBox` + Character position + nudge | Optional; failed Mac QA |
| C — inline text box | `insertTextBox` + `textWrap.type = inline` | **Planned spike** — see [WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md) |

**API references:**

- [Paragraph.insertTextBox](https://learn.microsoft.com/en-us/javascript/api/word/word.paragraph?view=word-js-preview#word-word-paragraph-inserttextbox-method) — “floating text box”
- [ShapeTextWrapType.inline](https://learn.microsoft.com/en-us/javascript/api/word/word.shapetextwraptype?view=word-js-preview) — “in line with text”
- [WordApiDesktop 1.2](https://learn.microsoft.com/en-us/javascript/api/requirement-sets/word/word-api-desktop-1-2-requirement-set)

**Full chronicle of add-in attempts:** [WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md).

## Critical UX discovery

Textboxes are **excellent for display** and **terrible for editing**.

Users must **not** be expected to click inside annotation boxes to change kaeriten.

Correct workflow:

```text
Edit:  說㆒㆑者     (source / Show source)
           ↓
Format kaeriten  (manual command)
           ↓
View:  說 [box: 一/レ] 者   (read-only view)
```

After mark or style changes → run **Format kaeriten** / **Render** again (rebuild boxes from source).

## Interoperability (Word + LibreOffice)

| Test | Result |
|------|--------|
| Visual quality in host app | Good with frames/textboxes |
| Copy within same app | Usually preserves objects |
| Copy to plain text / gedit | **Fails** for visuals — only underlying Unicode survives |
| Copy LibreOffice → OnlyOffice | **Fails** for frame objects |
| Search base kanji (`說`) | Pass |
| Search across annotation (`說者`) | **Fail** when object sits between characters — expected |
| Paragraph font size change | **Fail** until refresh — objects keep fixed internal size |

**Implication:** Visual objects are editor-specific views. **Plain Unicode source** is the portable archive format.

## Metadata (Word-specific note)

Custom XML, RDF, or hidden document properties are **not required** for v1 semantics. The string `說㆒㆑者` already encodes meaning.

Optional **editor-local** tags (bookmark names, textbox IDs, picture alt text) may help the Word add-in **find and refresh** its own views. **Copy plain** reads **canonical Unicode** + [mapping.json](../mapping.json), not Word-only hidden fields.

See [ARCHITECTURE.md](ARCHITECTURE.md#metadata-and-export).

## Relation to LibreOffice

| Concern | Shared? |
|---------|---------|
| Canonical `說㆒㆑者` | **Yes** — same across Word, LO, plain text |
| `mapping.json` stack rules | **Yes** |
| Frame vs. textbox implementation | **No** — per-host renderer |
| Import LO frames into Word | **No** — re-render from source in Word |

## OnlyOffice

OnlyOffice does **not** preserve LibreOffice frame objects on paste. Do not plan shared hidden metadata across three suites for v1.

OnlyOffice users should rely on **visible Unicode source** (and optional subscript fallback), not cross-app frame parity. See [ARCHITECTURE.md](ARCHITECTURE.md#onlyoffice) and the full guide **[ONLYOFFICE.md](ONLYOFFICE.md)**.

## Future plugin features (same model)

These fit **semantic text + generated view**:

- Compound kaeriten (already in source clusters)
- Vertical writing helpers
- Variant characters, hentaigana, kuzushiji
- Scholarly transcription symbols
- Copy plain export from source (TEI/LaTeX not shipped in v1)

## Office.js add-in (development, May 2026)

Hands-on add-in in [word/](../word/). See **[WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md)** for everything tried (anchors, text boxes, unrender, 縦書き, bookmarks).

| Topic | Choice |
|-------|--------|
| **Default renderer** | Locked **content controls** + hidden `_MMK_` bookmark |
| **Optional renderer** | Floating **text boxes** if `mapping.json` sets `word_primary: textbox` (Mac QA poor) |
| **Next spike (documented)** | **Inline text box:** `insertTextBox` + `textWrap.type = inline` — [WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md) |
| **Mac reality** | Visible **box often absent** with CC; small inline glyphs may remain |
| **Dev URL** | `https://127.0.0.1:3000` — local HTTPS server required |
| **Mac trust** | mkcert CA in system keychain, or Microsoft `office-addin-dev-certs` |
| **Mac UI** | Ribbon on **Accueil → Kaeriten**; task pane from **Kaeriten pane** |
| **Compléments browser** | Preview only — Office.js often never connects |

**Status:** Render/Unrender work in development on Mac with limitations above; LibreOffice remains the reliable formatter.

Resume checklist and troubleshooting: **[WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md)**.

## Related

- [WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md) — chronicle of add-in experiments (anchors, unrender, compound, vertical)
- [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md) — Mac add-in reality, certs, macros, parity matrix
- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) — Mac sideload, HTTPS, next session plan
- [ONLYOFFICE.md](ONLYOFFICE.md) — ONLYOFFICE in the marinaMoji stack
- [word/README.md](../word/README.md) — build and npm scripts
- [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md) — LO parallel experiments
- [TARGET_LAYOUT.md](TARGET_LAYOUT.md) — per-host renderers
- [ROADMAP.md](ROADMAP.md) — Phase 3 Word work
