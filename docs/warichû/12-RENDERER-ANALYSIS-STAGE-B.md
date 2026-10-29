# Stage B — Renderer analysis (observed + source)

Connects corpus visuals to Writer functions. Stage A paths remain valid; this adds empirical behaviour.

## Pipeline (unchanged from Stage A)

1. `SvxTwoLinesItem` / `RES_CHRATR_TWO_LINES` / UNO `CharCombine*`
2. `GetMultiCreator` → `SwMultiCreatorId::Double`
3. `SwDoubleLinePortion`
4. `SwTextFormatter::BuildMultiPortion` (`pormulti.cxx`)
5. Unequal widths → `CalcBlanks` → `CalcNewBlock` on shorter line

## Division algorithm — how well it performs

### Mechanism (source)

`BuildMultiPortion` iteratively formats into candidate width `nActWidth`:

- Format first inner line (`BuildPortions`).
- Remainder → second `SwLineLayout`.
- If text does not fit → widen guess; if slack → tighten.
- Font for double lines: **`SetProportion(50)`** before formatting (advances measured **after** scale).

**Not** an explicit midpoint index. Mid-looking splits are a side effect of equal-advance CJK under a balanced width.

### Observed performance (LO 26.8.0.3)

| Observation | Evidence | Inference |
|---|---|---|
| Classic 10-char → 5+5 | B01 PDF | Width search ≈ mid for equal advance |
| Odd lengths → 3+2 | B04 | Avoids naïve 2+3 mid when search balances |
| Shorter line stretched | B06 H; B18/B20 V | `CalcNewBlock` **does** fire for pure kana/CJK (not only ASCII blanks) — Stage A blank-only hypothesis **revised** |
| Closing punct at 2nd-line start | B11 H (`）`); B19 V (`、`); B20 V (`」`) | Line-break inside multi **does not** reliably apply JLREQ not-start rules |
| Very long notes still two rows | B07 | Fits by widening multiportion; may affect body line |

### Candidate improvement (not implemented)

Score candidate first-line ends by:

1. Width difference after 50% metrics  
2. Predicted `CalcNewBlock` stretch magnitude  
3. Kinsoku not-start / not-end  
4. Prefer second line ≤ first  
5. Punctuation class (comma preferably ends upper)

Implementable as a **local change** inside the double-line branch of `BuildMultiPortion` (try a few break indices near the width-search result) without new UNO — **if** maintainers accept behaviour change. Needs Japanese layout review + Cppunit fixtures.

## `CalcNewBlock` in warichū context

| Question | Finding |
|---|---|
| How is extra width distributed? | Via existing block/justify machinery on the shorter inner line (`CalcNewBlock`) |
| Uniform vs class-aware? | **Unverified** at glyph-class level; visually looks like inter-character tracking increase |
| Punctuation over-spaced? | Possible in B12/B20 — **questionable**, not proven wrong |
| Excessive stretch? | Mild in B06; stronger in vertical B20 — still readable |
| Inherently incorrect? | **No.** JLREQ allows spacing adjustment. Problem is **when** stretch papers over a bad break (B20) |

**Conclusion:** Do not add alignment-mode UI yet. Prefer better **division** so stretch stays small.

## Vertical composition

| Item | Result |
|---|---|
| Page `WritingMode` RL_TB | Applied successfully |
| Two-line combine in vertical | Paints; B18–B20 readable |
| “Upper/lower” in vertical | Along inline axis: first line toward start side (right in RL_TB preview) |
| Kinsoku | **Weaker:** B19 second line starts with `、`; B20 with `」` |
| B21 UNO brackets | Thumbnail shows 2×2 split; **delimiter paint not clearly confirmed** — treat vertical brackets as **needs re-check** vs horizontal collapse |

## Positioning vs JLREQ frames

Jutting above body cap-height remains **compatible** with JLREQ centering of a taller warichū block on the main line. Not classified as a defect without frame-metric measurement.

## Glyph advances vs character cells

Width search uses formatted portion widths at 50% font → effectively **glyph/advance based** after scaling, not a pure Unicode count. Equal kanji often coincide with count midpoints.
