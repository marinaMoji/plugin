# Stage E2 — Inspector architecture

## Layers

| Layer | Module | Depends on UNO? |
|---|---|---|
| A — Extraction | `typography_inspector.py` | Yes (read-only) |
| B — Analysis | `typography_analysis.py` | **No** |
| C — Presentation | `format_report` + dialog in inspector | UI only |

Toolbar command `org.marinaMoji.kaeriten:inspect_typography` → `inspect_japanese_typography()`.

## Scope

`InspectionScope.selection_kind`:

- `caret_paragraph` — caret’s paragraph  
- `selection_single` — selection within one paragraph (textual rules use selected string; settings from the paragraph)  
- `selection_multi` — all intersecting body paragraphs  
- `unsupported` — multi-object / unreadable selection  

Rules receive `ParagraphSnapshot` lists; they do not hard-code “current paragraph.”

## Read-only contract

Inspection must not write text, properties, preferences, or metadata. The adapter records `isModified()` before/after and restores it if a host quirk flips the flag.
