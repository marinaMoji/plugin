# Experimental notes — U1 delimiter paint (NOT compiled)

**Status:** Hypothesis + patch sketch only. **No local LO build.** Do not submit upstream yet.  
**Repro:** Stage B B16–B17; `artifacts/stage_b/warichu_stage_b_horizontal.odt`; span_spike B screenshot.  
**Host binary:** 26.8.0.3 · Source examined: `LibreOffice/core` master `pormulti.cxx`.

## Observed failure

With `CharCombineIsOn` + Prefix/Suffix `（` `）` (ODF `text-combine-start-char` / `end-char`), horizontal paint **collapses** annotation glyphs into an illegible cluster. Bare combine (no brackets) is fine. ODF stores brackets correctly; text is preserved.

## Likely locus (no debugger yet)

| Function | File |
|---|---|
| `SwDoubleLinePortion::FormatBrackets` | `sw/source/core/text/pormulti.cxx` |
| `SwDoubleLinePortion::PaintBracket` | same |
| `SwTextFormatter::BuildMultiPortion` (bracket branch) | same |

Brackets use `SetProportion(100)` (full size) while body uses 50% — correct vs JLREQ (~2× warichū size).

### Leading hypothesis

`FormatBrackets` subtracts full-size bracket widths from `nMaxWidth`. If remaining width is insufficient, it sets:

```cpp
m_pBracket->nPreWidth = 0;
nMaxWidth = 0;
```

(and similarly for post). Combined with `BuildMultiPortion`’s iterative width search, content may be formatted into a **near-zero** width while brackets still participate in paint/positioning → overlap. Alternatively, X-advance after open bracket may disagree with the width used for the multi body.

**Not yet proven** — needs breakpoint on `FormatBrackets` / first `BuildPortions` inside double-line with B16.

### Minimal correction direction (preserve layout algorithm)

1. **Do not** change `SvxTwoLinesItem` / UNO / ODF.  
2. When brackets are present, ensure content `nActWidth` never collapses below the natural two-line content width (floor), **or** fail bracket width reservation without zeroing content width.  
3. Keep existing width-search and `CalcNewBlock`.  
4. Regression: UITest or layout dump with B16 ODT; assert multiportion width ≥ sum of glyph advances + brackets; visual PDF compare.

### Sketch (illustrative — not tested)

In `FormatBrackets`, replace “set `nMaxWidth = 0`” with leaving a minimum content width / marking brackets as not fitting without destroying content measure — exact patch requires a debug build.

## Environment gate

See `16-LO-BUILD-ENVIRONMENT.md`. Until then: **delimiter patch does not work (unverified).**

## Separate from kinsoku

This file is **U1 only**. Kinsoku = `18-KINSOKU-NOTES.md`.
