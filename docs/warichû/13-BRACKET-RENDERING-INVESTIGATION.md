# Stage B — Bracket / delimiter rendering investigation

## Verdict

**Confirmed defect** for UNO / ODF `text-combine-start-char` / `end-char` (Prefix/Suffix) on **horizontal** Writer **26.8.0.3** (macOS).

This is a **paint/layout** failure. The underlying note characters and ODF bracket attributes are stored correctly.

**Do not file upstream without maintainer/user approval.** Draft reproducer below.

## Reproduction (minimal)

| Step | Action |
|---|---|
| 1 | LibreOffice Writer 26.8.0.3, new document, Japanese, font Hiragino Mincho ProN 14pt |
| 2 | Insert `本文` then select only the following characters: `割り注は、良いです。` |
| 3 | Via UNO (or Asian Layout → Double lines / combine with brackets): set `CharCombineIsOn=True`, `CharCombinePrefix=（`, `CharCombineSuffix=）` |
| 4 | Observe paint |

**Expected (JLREQ conventional):** Two mini-lines flanked by full-height-ish `（` `）` (ideally ~2× warichū glyph size).

**Actual:** Glyphs overlap into an illegible cluster; brackets distorted or unreadable.

### Automated corpus evidence

| Artifact | Result |
|---|---|
| `artifacts/span_spike/screenshots/v4_A_pass_B_brackets_fail.png` | A bare combine OK; B with Prefix/Suffix collapsed |
| `artifacts/stage_b/warichu_stage_b_horizontal.pdf` B16–B17 | Collapse reproduced |
| ODF T2 style | `text-combine="lines"` + start/end `（` `）` **present** |
| UNO after apply | Prefix/Suffix read back as `（` `）`; `source_preserved=true` |

### Control (working)

Same note with **only** `CharCombineIsOn` → readable two lines (B01, span A).

## Horizontal vs vertical vs PDF

| Surface | Status |
|---|---|
| Horizontal screen / PDF | **Fail** (confirmed) |
| Vertical B21 | Thumbnail shows 2×2 text; **parentheses/collapse unclear** — re-check before claiming vertical also broken |
| PDF vs screen | Failure visible in exported PDF (not screen-only) |

## Suspected code locus (hypothesis)

| Area | Path |
|---|---|
| Item | `SvxTwoLinesItem` brackets |
| Portion | `SwDoubleLinePortion` — `FormatBrackets`, `PaintBracket`, `SwBracket` |
| Build | `BuildMultiPortion` when `HasBrackets()` — reserves width then formats body |

Likely classes of bug (pick via debugger; not yet proven):

- Incorrect bracket width subtracted from `nMaxWidth` → body formatted into too-narrow space → overlap  
- Bracket painted at wrong origin relative to multi-portion  
- Font size/script for brackets wrong  
- Interaction with sticky formatting on macOS Skia  

**Not** “missing from ODF.” Serialization works.

## Existing Bugzilla

Quick search did **not** surface a clear duplicate for “double lines / text-combine / CharCombine brackets collapse.” Related hits were mixed-script bracket / line-break issues (e.g. discussions around tdf#56408), not this combine-delimiter paint path.

## Draft upstream report (for approval only)

**Summary:** Writer: Asian double-line (warichū) with start/end brackets paints overlapping illegible glyphs (26.8.0.3 macOS)

**Steps:** as above  
**Attachments:** `warichu_stage_b_horizontal.odt` (B16), `v4_A_pass_B_brackets_fail.png`, PDF crop of B16  
**Workaround:** Use combine **without** brackets; or (unverified) literal `（` `）` characters outside/inside span with trade-offs  

**Components:** Writer, CJK  

## Plugin policy (unchanged)

marinaMoji **must not** set `CharCombinePrefix` / `Suffix` until fixed. MVP remains bare combine.
