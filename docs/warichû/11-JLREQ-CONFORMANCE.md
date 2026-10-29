# Stage B — JLREQ conformance matrix (warichū)

**Spec:** [W3C JLREQ](https://www.w3.org/TR/jlreq/) (warichū / inline cutting note; punctuation; line adjustment; kinsoku).  
**Host:** LibreOffice Writer **26.8.0.3**, font Hiragino Mincho ProN.  
**Evidence:** Stage B corpus PDF/ODT + span_spike screenshot.  
**Legend:** Conformant · Acceptable alternative · Questionable · Nonconformant · Unverified

| ID | JLREQ locus | Requirement (summary) | Mode | Writer behaviour | Evidence | Assessment | Cause | Correction |
|---|---|---|---|---|---|---|---|---|
| C1 | Warichū intro | Two lines of reduced characters inline | H/V | Bare `text-combine="lines"` paints two mini-rows | B01–B15 PDF; span A | **Conformant** (basic) | `SwDoubleLinePortion` + `BuildMultiPortion` | None for on/off |
| C2 | Character size ~ half / by spec | Annotation smaller than body | H/V | Hard-coded **50%** proportion | Visual; source `SetProportion(50)` | **Acceptable alternative** (fixed 50%; not user-specifiable) | `BuildMultiPortion` | U5 configurable size |
| C3 | Inner line gap ≈ 0 | Two warichū lines tight | H | Appears tight / near-touching | PDF preview | **Conformant** (qualitative) | Portion metrics | Measure before changing |
| C4 | Centers with main line; may jut into line gap | Vertical centering on main character frame | H | Block roughly mid-line; upper row often above body cap-height | B01 PDF; Stage A note | **Conformant** (qualitative) | Double-line ascent/height | Do not “fix” by glyph-bbox centering alone |
| C5 | Balance two lines; 2nd not longer than 1st | Prefer equal lengths; permitted breaks | H | Width-search wrap; often balanced for equal-advance CJK | B01 5/5; B02 balanced; B04 3/2 | **Mostly acceptable**; **questionable** when 2nd longer (B04) | `BuildMultiPortion` width loop | Soft improve break scoring (U2) |
| C6 | Same kinsoku as body | Avoid prohibited starts/ends at inner break | H | **B11** observed: lower line starts with `）` | `warichu_stage_b_horizontal.pdf.png` B11 | **Questionable / likely nonconformant** for that case | Ordinary break inside multi width; weak JP class use | U2 kinsoku-aware candidate scoring |
| C7 | Punctuation spacing inside | JP punctuation rules | H | No systematic half-width audit; B12 looks uneven | PDF B12 | **Unverified** quantitatively | Unknown / font | Corpus + metrics later |
| C8 | Delimiters often （） at ~2× warichū size | Optional brackets | H/V | ODF stores start/end chars; **UNO Prefix/Suffix paint collapses** | B16–B17 PDF; span_spike B | **Nonconformant paint** when delimiters set via combine props | Bracket path in `SwDoubleLinePortion` / paint | **U1** bugfix; do not use in plugin |
| C9 | Vertical composition preferred context | Warichū in vertical writing | V | RL_TB page mode set; notes combine; preview generated | vertical ODT/PDF | **Partially verified** — orientation needs careful human check of thumbnail | Page `WritingMode` | Expand vertical visual pass |
| C10 | Annotation may affect perceived line gap | Design wider kihon gap if needed | H | Line box grows with combined height (expected) | Visual | **Acceptable** | Layout | Document for users |
| C11 | Manual / intentional division | Scholarly (beyond JLREQ) | — | Not in model | — | **Unsupported** | `SvxTwoLinesItem` shape | U3 proposal |

## Case-level notes (horizontal PDF)

| Case | Observed split (visual) | Heuristic preferred | Issue? |
|---|---|---|---|
| B01 | `割り注は、` / `良いです。` | Same | None |
| B02 | Balanced (comma at end of upper) | Same | None |
| B03 | Rough mid; upper appears shorter | Prefer comma on upper | Possible inferior break — **confirm on zoom** |
| B04 | 3 / 2 | Prefer 3 / 2 (avoid lower longer via mid 2/3) | Mid would be worse; OK |
| B06 | 6 / 5 with **visible stretch** on shorter | 6 / 5 | Stretch present — not inherently wrong |
| B09 | `「` on upper | Prefer `」` not at lower start | Appears OK vs naïve mid |
| B10 | `」` ends upper | Same family | OK |
| B11 | Upper ends `乙`; lower starts `）` | Prefer after `）` | **Demonstrable kinsoku defect** |
| B16–B17 | Collapsed illegible + distorted （） | n/a | **Confirmed paint bug** |

## Normative caution

JLREQ allows alternatives. Beginning-aligned unequal lines can be an acceptable convention. Distributed stretch (B06) is not automatically wrong. Classify defects only when evidence shows prohibited breaks, illegible paint, or clear inferiority to another **permitted** division.
