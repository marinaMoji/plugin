# LibreOffice Writer source notes — warichū / two-line combine

**Tree:** https://github.com/LibreOffice/core (master inspected 2026-10-29)  
**Host tested:** LibreOffice Writer **26.8.0.3**

## Critical distinction (do not confuse)

| Mechanism | What it is | Limit | marinaMoji use |
|---|---|---|---|
| **`SvxTwoLinesItem` / `RES_CHRATR_TWO_LINES`** → **`SwDoubleLinePortion`** | Asian “double lines” / ODF `style:text-combine="lines"` / UNO `CharCombineIsOn` | Full note string; two mini-lines | **This is warichū** |
| **`SwCombinedCharField` / `SwCombinedPortion`** | “Combined characters” field | **≤ 6** characters; grid paint; default proportion **55%** | **Not** scholarly warichū |

Comments in `pormulti.hxx` mention “combined characters” on `SwMultiPortion` generically; the **field** path lives in `porfld.cxx`. Warichū notes of length 10 (`割り注は、良いです。`) go through **`SwDoubleLinePortion`**.

## Attribute / API stack

| Layer | Symbol / location |
|---|---|
| Pool item | `include/editeng/twolinesitem.hxx` — `SvxTwoLinesItem` |
| Fields | `bool bOn`; `sal_Unicode cStartBracket`, `cEndBracket` only |
| Which-id | `RES_CHRATR_TWO_LINES` |
| UNO | `CharCombineIsOn`, `CharCombinePrefix`, `CharCombineSuffix` (map onto the item) |
| ODF | `style:text-combine="lines"` (+ optional start/end chars) |
| Attr stack | `sw/source/core/text/atrstck.cxx` (two-line activation) |
| Creator | `SwTextFormatter::GetMultiCreator` in `pormulti.cxx` → `SwMultiCreatorId::Double` |
| Portion ctor | `SwDoubleLinePortion` in `pormulti.cxx` / `pormulti.hxx` |
| Layout build | `SwTextFormatter::BuildMultiPortion` in `pormulti.cxx` |
| Portion factory | `SwTextFormatter::NewPortion` in `itrform2.cxx` (`new SwDoubleLinePortion`) |

**There is no division-point, alignment-mode, or inner-font-size field on `SvxTwoLinesItem`.**

## How `BuildMultiPortion` lays out double lines

Source: `sw/source/core/text/pormulti.cxx` — `SwTextFormatter::BuildMultiPortion`.

1. **Scale:** for `rMulti.IsDouble()`, create a temporary font with **`SetProportion(50)`** (hard-coded 50% of surrounding face for the annotation).
2. **Width search:** iteratively format into a candidate width `nActWidth` (binary-search-like between min and max):
   - Format **first** inner line via `BuildPortions`.
   - If text remains, create a second `SwLineLayout` and format the **rest**.
   - If both lines still do not consume the whole multiportion length → guess was too **narrow** → widen.
   - If they fit with slack → tighten.
3. **Division rule:** the split is whatever the ordinary **line-break / portion** machinery puts on the first line given `nActWidth` — **not** an explicit midpoint character index. For equal-advance CJK runs this often *looks* like a mid-string split (classic 10-char example → 5+5).
4. **Unequal widths:** `SwDoubleLinePortion::CalcBlanks` measures `m_nLineDiff` and blank counts; then **`CalcNewBlock`** is applied to the **shorter** line to stretch it toward the longer width (justification-style space add; kashida skipped depending on paragraph adjust).
5. **Brackets:** `SwBracket` / `PaintBracket` / `FormatBrackets` when start/end bracket code points are non-zero on the item.

### Implications for marinaMoji

| Desired control | Host reality |
|---|---|
| Manual division | **No** item property; inserting U+0020 / ZWSP would be a fragile text mutation — **refuse** |
| Alignment modes (begin/centre/end/distributed) | Partially: shorter-line stretch via `CalcNewBlock`; **not** JLREQ-selectable modes |
| Annotation size 40–60% | **Hard-coded 50%** in `BuildMultiPortion` for double lines |
| Independent inner-line spacing | Not exposed; gap emerges from portion metrics |
| Prefix/Suffix | Stored on item; paint path fragile under UNO on LO 26.8 (empirically broken) |

## Related files (checklist)

- `sw/source/core/text/pormulti.hxx` / `.cxx` — multi / double / ruby / rotate
- `sw/source/core/text/itrform2.cxx` — creates `SwDoubleLinePortion`
- `sw/source/core/text/atrstck.cxx` — two-line attribute active
- `sw/source/core/text/porfld.cxx` — **`SwCombinedPortion`** (≤6; do not use for long notes)
- `include/editeng/twolinesitem.hxx` — public item shape
- ODF import/export for `text-combine` (filter modules; verify on each corpus save)

## Smallest plausible upstream enhancements

Ranked for scholarly value vs patch size (detail in `09-PRIORITIZED-CORRECTIONS.md`):

1. Fix bracket paint when Prefix/Suffix set via UNO (bugfix; no model change).
2. Optional **explicit break index** or soft break mark for `SvxTwoLinesItem` + ODF extension (larger; needs ODF discussion).
3. Configurable proportion instead of hard-coded 50.
4. Explicit alignment enum instead of only `CalcNewBlock` stretch.
5. Kinsoku-aware preference when choosing first-line width / break (behavioural change; needs tests).

Avoid replacing Writer’s text engine; prefer item + `BuildMultiPortion` / `SwDoubleLinePortion` patches with Cppunit fixtures.
