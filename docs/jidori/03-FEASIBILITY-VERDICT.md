# Jidori — feasibility verdict

**Date:** 2026-10-29  
**Decision:** **Go** for a small Apply/Remove command (Scale width + Spacing approximation). Still **no** Word `w:fitText` claim; J5–J7 remain pre-release smoke.

**Live smoke (2026-10-29, LO Writer):** **J1–J4 pass** via Format → Character → Position. No toolbar spike was used.

**Calibration (10.5 pt Asian face):**
- Expand 3 → 5 cells: Spacing **≈ 10 pt** per gap ≈ 1 em (formula predicts 10.5 pt).
- Shrink 5 → 3 cells: Scale width **≈ 55%** (pure em formula predicts 60%). Close enough for approximation; product copy should say “approximate.”

## Summary

Writer has **no** first-class 字取り / Fit Text object. A marinaMoji command can still be useful if it:

1. Asks for target **N** (character cells).  
2. Sets `CharScaleWidth` and/or `CharKerning` on the selection using the OOo Fit Text equations.  
3. Clears those properties on Remove.  
4. Documents that this is an **approximation**, not Word `w:fitText`.

## Go criteria (Stage A spike)

| # | Test | Pass if | Status |
|---|---|---|---|
| J1 | `CharScaleWidth` 75% visible on LO 26.8 | Glyphs visibly condensed | **Pass** (live) |
| J2 | Positive `CharKerning` expands CJK run | Gaps visibly widen | **Pass** (live; ODT round-trip still optional) |
| J3 | Compute fit 3 kana → 5 cells | Approximate width matches 5 em visually | **Pass** (~10 pt Spacing at 10.5 pt) |
| J4 | Compute fit 5 kana → 3 cells | Scale (or kern) compresses; still legible | **Pass** (~55% Scale; predicted 60%) |
| J5 | Vertical writing | Same properties; no rotation side effects | Pending |
| J6 | Remove | Restores defaults; text unchanged | Pending |
| J7 | Coexistence | Does not break ruby / warichū / tate on **disjoint** spans | Pending |

If **J1 fails** (scale ignored), stop and reassess (upstream / kerning-only expand).

## No-go / defer

- Shipping a toolbar button before J1–J4.  
- Inserting spacer characters.  
- Claiming DOCX/`fitText` fidelity.  
- Whole-line 均等割り付け (that is Furiwake, #8).  
- Auto-jidori on large prose selections.

## Recommended next implementation slice (after spike)

Smallest product: **Apply jidori (N cells)** + **Remove jidori** on a short selection, policy similar to tate-chū-yoko (refuse warichū overlap; confirm long selections). No inspector integration required for MVP.

## Relation to Stage E2 inspector

Optional later diagnostic: “run uses non-default CharScaleWidth/CharKerning” as informational — not part of jidori Stage A.
