# U1 Bugzilla report — **for your review before filing**

**Do not submit until you approve.**  
**Classification:** LibreOffice **Writer defect** (CJK / Asian Layout double-line painting).  
**Not** a marinaMoji feature request. marinaMoji is mentioned only as discovery context.

---

## Duplicate search (2026-10-29)

| Method | Result |
|---|---|
| Web / prior Stage B search | No bug matching “text-combine / double lines + brackets → glyph collapse” |
| Bugzilla REST `quicksearch` | Partial results; unrelated hits (Draw SVG overlap, ordinary parenthesis line-break, etc.) |
| Terms tried | `two lines`, `text-combine`, `CharCombine`, `combine` + bracket/collapse, `warichu` |

**Assessment:** No clear duplicate found. Please glance at Bugzilla once more when filing (`Writer` + “two lines” / “combine characters” / “Asian”). If a duplicate exists, mark as such instead of opening a new bug.

---

## Confirmed vs hypothesis

| Claim | Status |
|---|---|
| With ODF `style:text-combine="lines"` **and** start/end chars `（` `）`, Writer paints an illegible overlapping cluster | **Confirmed** (screen + PDF) |
| Same text with `text-combine="lines"` **without** start/end chars paints readable two lines | **Confirmed** |
| Defect occurs with **native ODF** (no marinaMoji extension required) | **Confirmed** — see reproducer below |
| Exact root cause in `FormatBrackets` / width search | **Hypothesis only** — do **not** put in Bugzilla description as fact; optional “Notes for developers” |

---

## Proposed Bugzilla fields

| Field | Value |
|---|---|
| Product | LibreOffice |
| Component | Writer |
| Version | 26.8.0.3 Released |
| Hardware / OS | aarch64/x86_64 macOS (also ask for Linux confirmation) |
| Severity | normal (or major if triage prefers — layout illegible) |
| Summary | Writer: Asian double-line (text-combine) with start/end brackets paints overlapping illegible glyphs |

---

## Description (paste-ready)

```
Description:
In Writer, character-level Asian “double lines” / ODF style:text-combine="lines"
renders correctly without brackets. When the same formatting also sets
style:text-combine-start-char / end-char (UI: double lines with brackets;
UNO: CharCombinePrefix/Suffix), the combined text paints as an overlapping,
illegible cluster.

This is independent of any third-party extension: the attached ODT uses only
native ODF text styles.

Steps to Reproduce:
1. Open the attached ODT in LibreOffice Writer 26.8.0.3 (or create a new
   document: Japanese Asian font 14pt, e.g. Hiragino Mincho ProN / Noto CJK).
2. Observe paragraph “CONTROL bare combine”: 本文 + combined note without
   brackets — two readable mini-lines.
3. Observe paragraph “FAIL with brackets”: same note with （ ） combine
   brackets — glyphs collapse/overlap.
4. Optional UI-only path (no attachment): Format → Character → Position /
   Asian Layout (wording varies by version) → enable double lines / combine
   with brackets （ ） on a Japanese character span after 本文.

Actual Results:
Combined annotation with brackets is unreadable (overlapping glyphs).
Bare combine without brackets is fine.

Expected Results:
Two reduced-size lines of the annotation, with readable flanking brackets
(conventional Japanese warichū / inline cutting note presentation).

Reproducible: Always (on Writer 26.8.0.3 macOS).

User Profile Reset: No

Additional Info:
- LibreOffice 26.8.0.3, build id bce0998afefdbc355585ca324285661a2170ba77
- ODF: style:family="text" + style:text-combine="lines"
  + style:text-combine-start-char="（" + style:text-combine-end-char="）"
- PDF export shows the same collapse (not screen-only)
- Related reading: W3C JLREQ warichū / inline cutting note
  https://www.w3.org/TR/jlreq/
- Developer note (unverified hypothesis): bracket width handling in
  sw/source/core/text/pormulti.cxx (SwDoubleLinePortion::FormatBrackets /
  PaintBracket / BuildMultiPortion). Please treat as a hint only.
```

---

## Attachments to upload

| File | Path |
|---|---|
| Minimal ODT (native ODF) | `docs/warichû/upstream/u1-reproducer/u1_text_combine_brackets_collapse.odt` |
| PDF evidence | `…/u1_text_combine_brackets_collapse.pdf` |
| PNG preview | `…/u1_text_combine_brackets_collapse.pdf.png` |

Optional: Stage B span_spike screenshot  
`libreoffice/spikes/warichu/artifacts/span_spike/screenshots/v4_A_pass_B_brackets_fail.png`

---

## Independence from marinaMoji

The minimal ODT was authored as hand-written ODF (`text-combine` styles only).  
Verification: headless `soffice --convert-to pdf` of that ODT on LO **26.8.0.3** — control line readable; bracketed lines collapsed. **No extension loaded for that conversion.**

---

## After you approve

1. Create account / log in at https://bugs.documentfoundation.org/  
2. New bug → paste fields above → attach ODT (+ PDF/PNG)  
3. Record the bug number in `U1-BUGZILLA-FILED.md` (create when filed)

**U2 (kinsoku)** is **not** included in this report.
