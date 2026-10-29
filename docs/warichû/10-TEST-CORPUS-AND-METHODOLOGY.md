# Stage B — Test corpus and methodology

**Status:** Corpus generated and executed on host binary. Visual splits recorded from PDF preview where noted.  
**Do not confuse** offline division heuristics with Writer’s actual break.

## Environment

| Item | Value |
|---|---|
| LibreOffice binary | **26.8.0.3** (`bce0998afefdbc355585ca324285661a2170ba77`) |
| OS | macOS (darwin) |
| Stage A source tree | LibreOffice/core **master** via GitHub (not the exact 26.8 tag) |
| Discrepancy | Behaviour claims for `BuildMultiPortion` / `SwDoubleLinePortion` are from **master source**; paint tests are on **26.8.0.3**. Treat as matching family unless a regression is proven. |
| Font used in run | **Hiragino Mincho ProN** (selected) |
| Preferred fonts unavailable | Noto Serif CJK JP, Source Han Serif, IPAex Mincho **not** installed; Noto Sans JP present but not selected this run |
| Extension baseline | marinaMoji Kaeriten **0.3.15** (`warichu.py`: span `CharCombineIsOn` only) |
| Word for DOCX compare | **Not run** this stage |

## Artifacts

| Path | Role |
|---|---|
| `libreoffice/spikes/warichu/fixtures_stage_b.json` | Case definitions |
| `libreoffice/spikes/warichu/warichu_stage_b_corpus.py` | In-process LO macro |
| `libreoffice/spikes/warichu/run_stage_b_corpus.sh` | Install + launch |
| `libreoffice/spikes/warichu/analyze_division_heuristics.py` | Offline preferred-break scorer |
| `libreoffice/spikes/warichu/artifacts/stage_b/` | ODT, DOCX, PDF, JSON, checklist |
| Prior: `artifacts/span_spike/` | Bracket collapse screenshot (A pass / B fail) |

### Generated documents (2026-10-29 run)

- `warichu_stage_b_horizontal.odt` / `.docx` / `.pdf` (+ `.pdf.png` preview)
- `warichu_stage_b_vertical.odt` / `.docx` / `.pdf` (`WritingMode` RL_TB set)
- `stage_b_report.json`, `odf_horizontal.json`, `odf_vertical.json`
- `division_heuristics.md` / `.json`
- `VISUAL_CHECKLIST.md`, `SUMMARY.md`

**PDF via UNO `storeAsURL`:** failed (`ErrorCodeIOException` 0x81a).  
**PDF via** `soffice --headless --convert-to pdf`: **succeeded**. Methodology: prefer headless convert for PDF evidence.

## Insertion recipe (native only)

1. Body text outside combine.
2. Note span: `CharCombineIsOn=True` only (bare), **or** Prefix/Suffix `（` `）` for bracket repro cases.
3. Never paragraph-level `text-combine`.
4. No tables, text boxes, images, or inserted spaces for layout.

## Case groups

| Group | IDs | Intent |
|---|---|---|
| Balance | B01–B07 | Equal/odd/short/long/stretch |
| Punctuation | B08–B12 | Comma, brackets, mixed punct near break |
| Mixed | B13–B15 | Latin/digits, historical kana, VS16 |
| Brackets | B16–B17, B21 | UNO delimiter paint |
| Vertical | B18–B21 | RL_TB page writing mode |

## What we can and cannot measure automatically

| Observable | Method | Status |
|---|---|---|
| Exact note Unicode | ODF `content.xml` + UNO `getString` | **Measured** |
| `text-combine="lines"` on text styles | ODF | **Measured** |
| Bracket start/end chars in ODF | ODF T2 style | **Measured** |
| ODT reopen integrity | Reload ODT | **Measured** (classic + 葛 present) |
| DOCX `w:eastAsianLayout w:combine="true"` | OOXML | **Measured** (present; Word paint **unverified**) |
| Actual upper/lower split | Visual / PDF | **Partially recorded** (see checklist / 11–12) |
| Twip widths of inner lines | Layout dump / measurement UI | **Not automated** |
| Multi-font matrix | Re-run macro with forced fonts | **Deferred** (one font this run) |

## Reproduction

```bash
cd plugin/libreoffice/spikes/warichu
./run_stage_b_corpus.sh
# then:
/Applications/LibreOffice.app/Contents/MacOS/soffice --headless --convert-to pdf \
  --outdir artifacts/stage_b artifacts/stage_b/warichu_stage_b_horizontal.odt
python3 analyze_division_heuristics.py
```

## Integrity spot-check (this run)

From `stage_b_report.json`:

- Reopen horizontal ODT: **ok**
- Contiguous `割り注は、良いです。` still in document text: **true**
- VS16 sequence `葛` + U+E0100 preserved in note span: **true** (ODF code points confirmed)
- Source strings after apply: `source_preserved: true` for all cases including bracket cases (text intact; **paint** may still fail)
