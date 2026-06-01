# LibreOffice: frame-based kaeriten rendering

Hands-on prototyping (2026) confirmed that LibreOffice Writer can display **compound kaeriten** (e.g. 一二点 + レ stacked) at a level acceptable for scholarly use. This document records what was tried, what failed, and the parameters for the chosen approach.

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

### 3. Anchored borderless frame (chosen)

Tiny **borderless frame** anchored **as character**, containing stacked glyphs (e.g. 一 over レ).

| Parameter | Starting value |
|-----------|----------------|
| Anchor | As character (to preceding kanji) |
| Frame border | None |
| Content alignment | Bottom |
| Vertical offset | ~0.2 mm from bottom of line |
| Font size | Small (fixed pt in v1; ratio to base font in v2) |
| Typical stack | Top → bottom per mark order in source (e.g. `㆒㆑` → 一 / レ) |

| | |
|---|---|
| **Result** | Convincing for simple and compound kaeriten; survives editing; works in **vertical text** |
| **Decision** | **Primary render primitive** for LibreOffice |

## Stability tests

| Test | Result | Notes |
|------|--------|-------|
| Insert/delete text **before** annotated character | Pass | Frame stays attached |
| Search for base kanji alone (`說`) | Pass | |
| Search for base + following plain text (`說者`) | **Fail** | Frame sits **between** characters in text stream — expected |
| Copy/paste inside LibreOffice | Pass | Annotation preserved |
| Copy/paste to plain text (gedit) | **Fail** | Only underlying text; frames lost |
| Copy/paste to OnlyOffice | **Fail** | Frame object not preserved |
| Paragraph font 12 pt → 14 pt | **Problem** | Frame content keeps its own size until **Refresh rendering** |

## Conclusions

1. **LibreOffice can render professional kaeriten**, including compound stacks — the main technical risk for LO is resolved.
2. **LibreOffice has no native kaeriten type** (unlike ruby for furigana). The extension must **create and manage** its own annotation objects.
3. **Frames are a rendered view**, not the source of truth. Canonical meaning stays in Unicode (`說㆒㆑者`).
4. Users **format manually** (**Format kaeriten**); they **edit source**, not frame contents.

## Implementation notes (UNO)

- One frame per **mark cluster** after a base character (see [CONVENTIONS.md](CONVENTIONS.md#compound-kaeriten)).
- On **Format kaeriten**, hide or remove Unicode marks from visible flow and insert frame at anchor.
- **Refresh rendering** rebuilds frames when source marks or paragraph font size change.
- **Optional** editor-local tags (e.g. frame name `marinaMoji:kaeriten:<id>`) for finding objects on refresh — **not** for TEI/export semantics. See [ARCHITECTURE.md](ARCHITECTURE.md#metadata-and-export).
- Do **not** auto-format on every keystroke in v1.

## Related

- [ARCHITECTURE.md](ARCHITECTURE.md) — source vs view layers
- [WORD_FINDINGS.md](WORD_FINDINGS.md) — Word textbox parallel
- [TARGET_LAYOUT.md](TARGET_LAYOUT.md) — LO primary vs Word textboxes
- [ROADMAP.md](ROADMAP.md) — phased extension work
