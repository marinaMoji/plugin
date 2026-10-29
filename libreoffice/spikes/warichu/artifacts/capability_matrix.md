# LibreOffice warichū capability matrix (spike)

Host: LibreOffice **26.8.0.3** (macOS) · Font in screenshots: **Songti SC** 10.5 pt · UI language/locale showed **Chinese (simplified)**  
Artifacts: this folder · Screenshots: `screenshots/`

| Capability | Status | Evidence |
|---|---|---|
| T01 Insert `CharCombineIsOn` | **Verified** (API) | `spike_report.json` |
| T02 Inspect properties | **Verified** | Prefix/Suffix round-trip |
| Source string preserved | **Verified** | report `source_preserved` |
| T08 Save/reopen ODT | **Verified** | combine still on after reopen |
| ODF `style:text-combine="lines"` | **Verified** | `odf_combine_snippets.json` |
| T09 Write DOCX from Writer | **Verified** (write only) | `warichu_spike.docx` |
| T04 Visual two-line layout | **Failed / unusable** | Screenshots: overlapping glyphs; cannot judge alignment |
| T07 Vertical visual layout | **Failed / unusable** | Same overlap in TB_RL |
| T05 Manual break | Unknown | blocked by broken render |
| T10 Editability feel | Partially verified | text remains real Unicode; visual unusable |

## Visual finding (2026-10-29)

User screenshots show **stacked/overlapping full-size glyphs**, not a readable warichū block. Brackets sometimes appear. A few short runs (e.g. bottom of vertical view) hint at an attempted two-line split, but overall the feature is not usable for scholarly work on this host/font/build.

ODF stores combine on **paragraph automatic styles** (`style:family="paragraph"`), not `text:span` character styles — worth re-testing with an explicit character style / Format → Character → Position → “Combine characters” and a Japanese font (e.g. Hiragino Mincho) + Japanese Asian language.

## Product implication

Do **not** ship an LO warichū toolbar that only flips `CharCombineIsOn`. Next spike goals: (1) UI-applied combine with JP font/locale; (2) if still broken → Writer layout source trace / upstream bug (roadmap Phase 5).
