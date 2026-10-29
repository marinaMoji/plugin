# Stage E1 test corpus plan

**Status:** plan + generator ready. ODTs under  
`libreoffice/spikes/kinsoku/artifacts/` (binaries gitignored).

**Generator:** `libreoffice/spikes/kinsoku/scripts/kinsoku_corpus_macro.py`  
→ `run_kinsoku_corpus_horizontal()` (LibreOffice Python macro).

## Environment (fill on each run)

| Field | Value |
|---|---|
| LibreOffice | 26.8.0.3 (`bce0998afefdbc355585ca324285661a2170ba77`) |
| OS | macOS (darwin) |
| Fonts | Prefer Hiragino Mincho ProN; Gothic: Hiragino Sans — record actual substitution |
| Asian support | Required ON |
| Page | ~70 mm width, 5 mm margins (macro) |
| Grid | Off for first pass; K10 later |
| Direction | H first; V = separate page-style corpus (Pending) |

## Method rules

1. Prefer **automatic** line breaks (narrow measure / long run).  
2. Do **not** use manual breaks to “prove” kinsoku.  
3. Keep one phenomenon per paragraph when possible.  
4. Preserve: ODT, PDF, screenshot, UNO dump, expected vs actual note.  
5. Distinguish body breaks vs warichū-internal (reuse Stage B for the latter).

## Locale reference lists

See [`../../libreoffice/spikes/kinsoku/fixtures/ja_JP_forbidden_defaults.json`](../../libreoffice/spikes/kinsoku/fixtures/ja_JP_forbidden_defaults.json).

## Planned / generated cases

| ID | Category | Seed idea | Variants | Status |
|---|---|---|---|---|
| K01 | Line-start | Force `。` toward wrap | Forbidden on | Macro includes |
| K01b | Line-start | same | Forbidden **off** | Macro includes |
| K02 | Line-start | `、` | on | Macro includes |
| K03 | Line-start | `）` `」` | on | Macro includes |
| K04 | Line-start | Small kana `ゃ` | on | Macro includes |
| K05 | Line-end | Opening `「（` | on | Macro includes |
| K06 | Consecutive | `。」` | spacing observation | Macro includes |
| K07 | Compression | punct mid/end/Latin | vary `CharacterCompressionType` | Pending (manual settings variants) |
| K08 / K08b | Hanging | `。` at edge | hanging on/off | Macro includes |
| K09 | Vertical | K01–K05 / K08 in vertical page | | Pending |
| K10 | Grid | subset with character grid | | Pending |
| K11 | Ruby | punct beside ruby at wrap | | Pending (reuse ruby fixtures) |
| K12 | Tate | `12。` / `「12` near wrap | | Pending |
| K13 | Emphasis | same string ± emphasis | | Pending |
| K14 | Warichū | B11/B19/B20 reuse | document-only | Reuse Stage B ODTs |

## Expected vs actual (template)

For each ID after visual check:

| ID | Expected (convention) | Actual (Writer) | Interpretation |
|---|---|---|---|
| K01 | `。` not at line head when forbidden ON | _TBD_ | |
| K01b | may appear at line head when OFF | _TBD_ | config finding ≠ engine bug |
| K08 | `。` may hang past measure when ON | _TBD_ | |
| K08b | `。` wraps or compresses when OFF | _TBD_ | |

## Control of line width

- Fixed page style + 14 pt Asian font.  
- Narrow page width (~70 mm) + short margins.  
- No soft breaks inserted by the author in test bodies.

## Distinction

**A.** Automatic breaks chosen by Writer (this corpus).  
**B.** Explicit author breaks (Prototype B textual rule).  
**C.** Annotation-internal breaks (warichū Stage B — not this macro).
