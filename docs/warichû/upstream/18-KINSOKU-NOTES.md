# Experimental notes — U2 kinsoku at warichū break (NOT implemented)

**Status:** Feasibility analysis. Separate from U1. Do not combine patches.  
**Failures:** B11 (`）` starts 2nd line H); B19 (`、` starts 2nd V); B20 (`」` starts 2nd V).

## Can `BuildMultiPortion` reuse existing JP line-break rules?

**Likely yes, in principle.**

Writer already calls ICU/`BreakIterator` / `getLineBreak` elsewhere (see helpers near multiportion / `g_pBreakIt` in `pormulti.cxx`). The double-line path currently fills the first inner line by ordinary `BuildPortions` into a guessed width, so the break is whatever the first line’s last break opportunity is under that width — **not** a post-pass that forbids not-start characters at the head of line 2.

### Minimal isolated approach

After a candidate first-line end index `i` (from the width-search result):

1. If character at `i` is a **not-start** class (closing brackets, `、。`, small kana, etc. — reuse Writer’s existing forbidden-start table / `i18n::ForbiddenCharacters` / same data as body kinsoku).  
2. Move break left (or right) to the nearest legal opportunity within a small window, then re-format once.  
3. Abort adjustment if it would make the multiportion wider than the previous solution by more than a threshold (protect “otherwise valid” notes).

### Scope control

- Touch only `SwMultiCreatorId::Double` / `SwDoubleLinePortion` path.  
- Do **not** change ruby/bidi/rotate.  
- Default behaviour for clean B01/B02 should remain visually identical (add golden tests).

### If too extensive

If legal breaks require re-plumbing the entire first-line `BuildPortions` loop (not a post-adjust), **defer implementation** and propose design on the LO mailing list first.

**Stage C decision:** Documented as **feasible as a small post-adjust**; **not coded** (no LO build). Regression fixtures: B11/B19/B20 ODTs from Stage B corpus.

## JLREQ

Inner warichū break should follow the same kinsoku conventions as the main text (JLREQ line-breaking / character classes; Stage B matrix C6).
