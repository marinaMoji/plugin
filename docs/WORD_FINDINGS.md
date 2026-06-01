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

### Anchored textboxes

Tiny borderless textboxes anchored **as character**, with stacked glyphs (e.g. 一 / レ).

| | |
|---|---|
| **Result** | Visually convincing; similar role to LO frames |
| **Advantages** | Flexible positioning vs. frames in some cases |
| **Problems** | Font-size changes do not scale box content; same search/copy limits as LO |
| **Decision** | **Primary Word render primitive** (Phase 3) |

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

After mark or style changes → **Refresh rendering** (rebuild boxes from source).

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

Optional **editor-local** tags (bookmark names, textbox IDs) may help the Word add-in **find and refresh** its own boxes. Export (TEI, LaTeX) should read **visible canonical text** + [mapping.json](../mapping.json), not Word-only hidden fields.

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

OnlyOffice users should rely on **visible Unicode source** (and optional subscript fallback), not cross-app frame parity. See [ARCHITECTURE.md](ARCHITECTURE.md#onlyoffice).

## Future plugin features (same model)

These fit **semantic text + generated view**:

- Compound kaeriten (already in source clusters)
- Vertical writing helpers
- Variant characters, hentaigana, kuzushiji
- Scholarly transcription symbols
- TEI/XML export from source

## Related

- [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md) — LO parallel experiments
- [TARGET_LAYOUT.md](TARGET_LAYOUT.md) — per-host renderers
- [ROADMAP.md](ROADMAP.md) — Phase 3 Word work
