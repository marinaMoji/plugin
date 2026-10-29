# Upstream-ready: U2 — Warichū inner break allows not-start punctuation (draft)

**Do not file without approval.** Separate from U1.

## Summary

Writer double-line (warichū) division can place prohibited line-start punctuation at the beginning of the second annotation line.

## Version

LibreOffice Writer **26.8.0.3** (macOS).

## Examples

| ID | Note | Observed second-line start |
|---|---|---|
| B11 (horizontal) | `（甲乙）丙丁。` | `）` |
| B19 (vertical) | `天地玄黄、宇宙洪荒。` | `、` |
| B20 (vertical) | `曰「天地」なり。` | `」` |

## Steps

1. Apply bare `CharCombineIsOn` (no brackets) to the note span after `本文`.  
2. Use corpus ODT or recreate strings above.  
3. Inspect second warichū line start (horizontal or vertical page).

## Expected

Inner break respects the same Japanese line-breaking (kinsoku) restrictions as body text (JLREQ).

## Actual

Closing brackets / ideographic comma can begin the second line.

## Reproducer

`artifacts/stage_b/warichu_stage_b_horizontal.odt` (B11)  
`artifacts/stage_b/warichu_stage_b_vertical.odt` (B19, B20)  
Previews: `*.pdf.png`

## Source

`SwTextFormatter::BuildMultiPortion` double-line width-search / first-line fill (`pormulti.cxx`).

## Proposed correction

Post-adjust candidate break using Writer’s existing forbidden-start classes; re-format once; keep defaults for already-legal breaks. See `18-KINSOKU-NOTES.md`.

## Regression

B01/B02 must stay visually unchanged; B11/B19/B20 must move break.
