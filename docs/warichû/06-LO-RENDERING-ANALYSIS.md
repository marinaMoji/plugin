# LibreOffice warichū rendering analysis (Stage A)

**Scope:** Baseline for refinement. No implementation changes claimed here.

## Environment (known working)

| Item | Value |
|---|---|
| LibreOffice | **26.8.0.3** (macOS, user machine) |
| OS | darwin (Apple Silicon / Intel as installed) |
| Extension | marinaMoji Kaeriten **0.3.15** |
| Creation method | UNO `CharCombineIsOn=True` on **character selection** (not whole paragraph); Prefix/Suffix **omitted** |
| Document | ODT (primary); DOCX export **not** fully audited yet |
| Writing direction | Horizontal for classic screenshot; vertical **pending** corpus |
| Document grid | Not systematically compared yet |
| Asian layout | CharCombine via Asian Layout dialog / UNO |

## Classic example (matches user screenshot)

**Main:** `本文`  
**Annotation (continuous string):** `割り注は、良いです。` (10 characters)

Observed split:

| Line | Text |
|---|---|
| Upper | `割り注は、` |
| Lower | `良いです。` |

That is a **character-count midpoint** for this string (5+5). It is **not** proof of a general algorithm (glyph advance, grapheme clusters, or kinsoku).

ODF shape (working):

```xml
本文
<text:span text:style-name="T_combine">割り注は、良いです。</text:span>
```

Style family **text** with `style:text-combine="lines"`.  
**Do not** put `text-combine` on the paragraph style — that paints overlapping illegible text on LO 26.8.

## Vertical positioning (qualitative)

From the screenshot and JLREQ J6:

- Upper warichū line extends **above** the top of full-size `本`/`文` glyphs.
- Lower warichū line sits **above** the main-text baseline (not sitting on it like a subscript).
- This is **compatible with** JLREQ’s description that warichū is wider than one main character and is **centered** on the main line, jutting into the line gap.

**Not yet measured:**

1. Exact host formula for combined height.
2. Whether combined block ≈ one main character frame width/height.
3. Whether paragraph line height changes systematically.
4. Font-to-font variance (Noto / Source Han / IPAex / LO default).
5. Document-grid on vs off.

**Target (policy):** occupy intended typographic space without unjustified main-line rhythm change. Do **not** “fix” by centering glyph bboxes alone.

## Horizontal alignment (qualitative)

For the classic example, both lines appear to start at approximately the same horizontal origin (beginning alignment of two equal-length runs).

**Not yet proven for unequal lengths:** centre, distribute, compress, end-align, or punctuation half-width behaviour.

Corpus needed (see plan §25): ±1 / ±2 char imbalance; mixed punctuation; Latin/numerals.

## Line division — what we know vs guess

| Hypothesis | Evidence |
|---|---|
| Midpoint by Unicode scalar / character count | Strong for classic 10-char JP string |
| Glyph advance balancing | Untested |
| Grapheme clusters / VS / supplementary plane | Untested |
| Kinsoku-aware break | Untested; likely weak |
| Plugin-supplied break point | **No** UNO/ODF property found |

`SwCombinedPortion` in Writer is a **≤6 character** combined-character grid (kumimoji-like). Longer warichū text goes through a **multi-portion** path. Do not assume the ≤6 grid algorithm is what paints scholarly notes.

## Delimiters

| Method | Result on LO 26.8 (tested) |
|---|---|
| `CharCombinePrefix` / `CharCombineSuffix` via UNO | Collapsed / broken paint |
| Asian Layout UI with brackets | Historically worked for user in some cases; treat as fragile until retested |
| Literal `（` `）` inside the combined string | Possible text-integrity-preserving experiment; **not** cl-28/29 semantics |

## Character spacing

UNO character spacing on the combine span: **not** yet shown to adjust the two inner lines independently. If spacing applies to the whole annotation before split, it will not fix unequal-line alignment.

## Integrity rules (already enforced in MVP)

- Apply only to a **character span**, not whole paragraph.
- No spaces / ZWSP for alignment.
- No images / drawings as warichū.
- No Unicode normalization on apply.
- Remove clears combine flags on the span; leave characters intact.

## Screenshots / artifacts

Prior spike evidence lives under:

- `libreoffice/spikes/warichu/artifacts/` (span spike VERDICT A pass; B brackets fail)

PDF export comparison: **pending** formal corpus run.

## Open measurement backlog (Stage A → B)

1. Pixel / character-frame measurements for classic example across 3 fonts.
2. Unequal-length matrix.
3. Vertical writing mode screenshots.
4. Save/reopen + `content.xml` audit for every corpus ODT.
5. DOCX round-trip appearance vs text integrity.
