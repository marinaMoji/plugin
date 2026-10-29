# Stage E2 implementation recommendations

**Do not start E2 until this Stage E1 package is reviewed.**

## Smallest useful E2 (recommended)

**Japanese Typography → Inspect Paragraph (read-only dialog)**

Implements:

1. Show effective `ParaIsForbiddenRules`, `ParaIsHangingPunctuation`, `ParaIsCharacterDistance`.  
2. Show document `CharacterCompressionType` and whether `ja` forbidden lists are present (read-only dump of begin/end strings, truncated).  
3. Textual scan of selection/paragraph:
   - mixed half-width / full-width Japanese punctuation (`PUNCTUATION_MIXED_WIDTH`);
   - soft/hard explicit breaks immediately before characters in the **document** not-start list (`EXPLICIT_BREAK_BEFORE_NOTSTART`).  
4. Optional advisory: selection contains warichū (`CharCombineIsOn`) — remind that inner breaks are not body-kinsoku-guaranteed (`WARICHU_INTERNAL_BREAK` informational).

**Does not implement:** automatic correction, Options rewriting, rendered line-head detection, profile UI, Word adapter, toolbar buttons beyond a single Inspect entry if approved.

## Priority order

| Priority | Item | Why |
|---|---|---|
| P0 | Settings readout (Prototype A productionized) | High value, reliable UNO, no layout risk |
| P0 | Mixed-width punct textual rule | Scholarly usefulness, host-independent |
| P1 | Explicit break before not-start | Textual; catches author-inserted breaks |
| P1 | Warichū advisory pointer to known limitation | Reuses Stage B knowledge |
| P2 | Controlled corpus completion + screenshot matrix | Hardens claims in `02`/`03` |
| P3 | Live-view `isAtStartOfLine` / a11y `LINE` experiments | Opt-in only; gate on vertical + annotation false positives |
| Defer | True `KINSOKU_LINE_START` layout diagnostics | Unreliable without layout API |
| Defer | Composition **controls** UI (write toggles) | Inspector-first; avoid surprising global Options |
| Defer | Scholarly profile UI | After inspector exists |
| Defer | Upstream U2 / new Bugzilla | Needs approval |

## Composition controls before inspector?

**No compelling reason.** Writer already exposes Asian Typography. marinaMoji’s gap is **understanding / advising**, not missing checkboxes. If E2 adds controls later, they must write **paragraph** properties only, never application Asian Layout, and remain undoable.

## Upstream LibreOffice changes?

| Issue | Needed for E2 inspector? |
|---|---|
| tdf#174224 delimiter paint | No |
| U2 warichū kinsoku | No for textual inspector; yes for perfect warichū layout |
| New UNO line-geometry API | Would unlock deferred layout rules; out of marinaMoji’s hands |

## Safety checklist (carry into E2)

- Read-only default.  
- No Unicode normalization.  
- No invisible characters inserted.  
- No style or grid mutation.  
- Selection-scoped analysis.  
- Profile-aware wording even if only `modern_ja` is hard-coded at first.
