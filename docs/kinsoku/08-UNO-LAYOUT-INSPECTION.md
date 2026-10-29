# UNO layout inspection — what marinaMoji can actually see

**Verdict (Stage E1, refined):** reliable **settings** and **textual** inspection — **yes**. Rendered line-start detection — **Partial**: possible in a **live Writer view** via `XLineCursor` / accessibility `LINE`, **not** suitable as the core of Stage E2 (view-dependent, fragile on vertical/annotations, unreliable headless). Prefer textual + settings for E2; keep layout as optional experimental.

Evidence from source/IDL follow-up ([layout UNO probe](b6a46880-186a-49ca-9e5b-70bee2e20d42)): `isAtStartOfLine()` → Writer `IsAtLeftMargin()`; a11y line breaks from `SwAccessiblePortionData::LineBreak()`.

## Candidate mechanisms

| Mechanism | Exposes | Needs view? | Headless? | Vertical? | Stable text offset? | Alters doc? | Verdict |
|---|---|---|---|---|---|---|---|
| Paragraph `ParaIs*` via text cursor | Effective Asian toggles | No | Yes | Yes (same props) | N/A | No | **Use (E2)** |
| Doc `ForbiddenCharacters` / `CharacterCompressionType` | Lists + compression | No | Yes | N/A | N/A | No if read-only | **Use (E2)** |
| `XBreakIterator.getLineBreak` + `LineBreakUserOptions` | Algorithmic break indices | No | Yes | N/A | String indices | No | Soft heuristic only (≠ full Writer layout) |
| `XLineCursor.isAtStartOfLine` after `gotoRange` | Layout line-start boolean | **Yes** (`SwView`) | No | Uncertain (left-margin semantics) | Model range if mapped carefully | Selection may move | **Partial** — E2 debug / opt-in only |
| `XViewCursor.goDown` + line walk | Visual line iteration | Yes | No | Fragile | Weak | Selection may move | Prototype only |
| Accessibility `getTextAtIndex(..., LINE)` / `XAccessibleMultiLineText` | Screen-line segments from layout | Layout + usually window | Poor | Untested | Accessible string ≠ raw model (fields) | Read-only if careful | **Partial** — corroboration |
| `XAccessibleText.getCharacterBounds` | Char rects | Window required | No | Untested | Partial | No | Heavy; not E2 core |
| `TextLayoutCursor` / `getPosition()` | Pages / pixel point | View | — | — | No line API | — | **Not useful** for kinsoku |
| PDF export geometry | Drawn glyphs | Indirect | Possible | Possible | Not document offsets | Creates export | Human evidence only |
| Internal `SwLineLayout` / VCL `GetTextLines` | True breaks | Not via UNO | — | — | — | — | **Unavailable** |

## Critical distinctions

1. **`isAtStartOfLine` is layout-grounded**, not a free-form guess — but it still requires a formatted view and is **not** a public break table.  
2. Multiportions (ruby / warichū), fields, tables, hanging punctuation, and vertical writing can disagree with naive “first char on line” expectations.  
3. Warichū **inner** mini-lines are **not** exposed as ordinary paragraph line starts through UNO.  
4. PDF glyph positions ≠ document character indices (ruby investigation lesson).

## Prototype map

| Prototype | Goal | Location |
|---|---|---|
| A | Read `ParaIs*` + forbidden/compression | `spikes/kinsoku/scripts/proto_a_read_asian_para.py` |
| B | Textual punctuation ranges | `proto_b_textual_punctuation.py` |
| C | Line-head via `XLineCursor.isAtStartOfLine` | `proto_c_viewcursor_line_heads.py` (experimental) |
| D | H vs V caret / line-start comparison | extend C |
| E | Warichū: combine detection only | document-only |

## Stop condition (honoured)

Stage E2 ships **textual + settings** diagnostics first. Layout line-start (`KINSOKU_LINE_START`) stays behind a debug flag until corpus proves acceptable false-positive rates on vertical + annotated text.
