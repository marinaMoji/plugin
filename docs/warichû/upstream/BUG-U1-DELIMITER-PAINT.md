# Upstream-ready: U1 — Double-line combine brackets collapse (draft)

**Do not file without approval.**

## Summary

Writer: Asian double-line / warichū (`style:text-combine="lines"`) with start/end brackets paints overlapping illegible glyphs.

## Version

LibreOffice Writer **26.8.0.3** (macOS), build id `bce0998afefdbc355585ca324285661a2170ba77`.

## Steps

1. New Writer document; Asian font (e.g. Hiragino Mincho ProN) 14 pt; Japanese locale.  
2. Type `本文` then `割り注は、良いです。`  
3. Select only `割り注は、良いです。`  
4. Enable character combine / double lines **with** brackets `（` `）` (UNO: `CharCombineIsOn=True`, `CharCombinePrefix=（`, `CharCombineSuffix=）`).  
5. Observe.

## Expected

Two reduced-size lines of the note, flanked by readable parentheses (JLREQ: delimiters often ~2× warichū character size).

## Actual

Annotation glyphs collapse/overlap into an illegible cluster; brackets distorted.

## Control

Same note with combine **without** brackets → correct two-line layout.

## Minimal reproducer

`plugin/libreoffice/spikes/warichu/artifacts/stage_b/warichu_stage_b_horizontal.odt` (cases B16–B17)  
Screenshot: `…/span_spike/screenshots/v4_A_pass_B_brackets_fail.png`  
PDF: `…/stage_b/warichu_stage_b_horizontal.pdf`

## JLREQ

Inline cutting note / warichū delimiters (brackets as optional convention; cl-28/cl-29). Spec: https://www.w3.org/TR/jlreq/

## Source

`sw/source/core/text/pormulti.cxx` — `SwDoubleLinePortion::FormatBrackets`, `PaintBracket`, `BuildMultiPortion` bracket branch. Item: `SvxTwoLinesItem`.

## Proposed correction

Fix width/position accounting so bracket reservation cannot collapse content layout; no UNO/ODF model change. See `17-DELIMITER-PATCH-NOTES.md`.

## Regression tests

Not run (no LO source build on reporter machine). Suggested: layout/UITest on B16 ODT; compare bare vs bracketed multiportion widths.

## Attachments checklist

- [ ] ODT (B16 only extract)  
- [ ] PNG before  
- [ ] PDF crop  
- [ ] Patch (when compiled)
