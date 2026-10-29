# Stage E1 decision report

**Host:** LibreOffice Writer 26.8.0.3 (`bce0998afefdbc355585ca324285661a2170ba77`), macOS.  
**Date:** 2026-10-29.  
**Scope:** investigation + planning; **no** production inspector shipped.

---

## Native Writer capabilities

1. **Which Japanese kinsoku rules does Writer implement?**  
   Locale `ForbiddenLineBeginCharacters` / `ForbiddenLineEndCharacters` applied when `ParaIsForbiddenRules` is true, via `BreakIterator_CJK` on top of ICU. Defaults for `ja_JP` include `、。` , closing brackets, small kana, 々, ー, etc., and opening brackets/quotes at line end (see `02`).

2. **Punctuation-spacing conventions?**  
   Partial: Asian–Western autospace (`ParaIsCharacterDistance`); full JLREQ half-em aki tables are **not** exposed as controllable UNO spacing rules. Much “full-width look” is font + compression.

3. **Hanging punctuation?**  
   **Yes** for body text (`ParaIsHangingPunctuation`; hanging set `、。，．`). **Disabled** inside multiportions (`!IsMulti()`), tables, and field groups.

4. **Punctuation compression?**  
   **Yes**, document/Options level: `CharacterCompressionType` = none / punctuation / punctuation+kana; plus `IsKernAsianPunctuation`.

5. **UNO settings available?**  
   Paragraph: `ParaIsForbiddenRules`, `ParaIsHangingPunctuation`, `ParaIsCharacterDistance`. Document: `ForbiddenCharacters`, `CharacterCompressionType`, `IsKernAsianPunctuation`.

6. **Document vs application-wide?**  
   Paragraph toggles = para/style. Forbidden **lists** defaults live in Options Asian Layout but are accessible per document via `XForbiddenCharacters`. Compression = document setting (Options seeds defaults). **Do not** rewrite application Options from marinaMoji.

7. **ODT persistence?**  
   Paragraph toggles map to `style:line-break`, `style:punctuation-wrap`, `style:text-autospace` (**Confirmed** xmloff map). Forbidden lists / compression via settings export (**Confirmed** code path; sample dump still recommended).

8. **Horizontal vs vertical differences?**  
   Same UNO properties. Glyph orientation is font/writing-mode. Behavioural hanging/grid differences need corpus K09/K10 (**Pending** render), not assumed equal visually.

## JLREQ correspondence

9. **Which JLREQ conventions does Writer follow?**  
   Core not-start / not-end lists (configurable); hanging for commas/periods; rough compression modes; autospace. Not a full JLREQ engine.

10. **Where does behaviour differ?**  
    No complete cl-* spacing table; warichū-internal breaks lack kinsoku post-filter; hanging off in multiportions; strictness of small kana/々 is list-dependent (JLREQ allows relaxation).

11. **Configurable differences?**  
    Forbidden lists, paragraph toggles, compression type, hanging on/off.

12. **Genuine limitations?**  
    No headless/document-wide line-break table; warichū lacks inner line-2 kinsoku post-filter; incomplete scholarly spacing control. Live-view `isAtStartOfLine` / a11y `LINE` are only **Partial**.

13. **Font / grid confounds?**  
    Yes — always record font + grid before blaming Writer (esp. vertical punct orientation).

## Inspector feasibility

14. **Effective paragraph settings?** **Yes** (read `ParaIs*`).  
15. **Rendered line boundaries?** **Partial** in live view (`XLineCursor.isAtStartOfLine`, a11y `LINE`); **not** production-ready for E2 default.  
16. **Map line positions → text ranges?** **Partial** with view cursor / a11y; fragile around fields and multiportions.  
17. **Vertical line boundaries?** Untested; `IsAtLeftMargin` naming suggests horizontal bias — corpus required.  
18. **Warichū internal divisions?** **No** break index; combine detection only. Shared `Guess` path ≠ guaranteed kinsoku-safe inner split.  
19. **Without layout geometry?** Settings + mixed-width punct + explicit breaks + warichū advisory.  
20. **Needs stronger host info?** Default-on `KINSOKU_LINE_START` / `LINE_END`; aki measurement; headless whole-doc layout.

## Scholarly use

21. **Vary by profile:** mixed-width warnings; small-kana/々 strictness; treatment of kaeriten/marks; diplomatic suppression.  
22. **Misleading risks:** flagging historical punct; treating kaeriten as body punct; calling relaxed book practice an error.  
23. **Editorial vs defect:** severity + profile + mechanism label; advisory wording; never auto-normalize.

## Implementation decision

24. **Smallest useful E2:** read-only **Inspect Paragraph** (settings + textual rules). See `10`.  
25. **First diagnostics:** `PARA_FORBIDDEN_RULES_OFF`, `PUNCTUATION_MIXED_WIDTH`, `EXPLICIT_BREAK_BEFORE_NOTSTART`, optional warichū advisory.  
26. **Defer:** layout kinsoku detection, profile UI, Word, write-controls, upstream filings.  
27. **Upstream changes necessary for E2?** **No.**  
28. **Composition controls before inspector?** **No** — Writer already has Asian Typography; marinaMoji should advise first.

---

## Capability matrix (final for Stage E1)

| Feature | Writer native support | UNO access | ODF persistence | Vertical support | Inspector feasibility |
|---|---|---|---|---|---|
| Line-start prohibitions | Yes (lists + para toggle) | `ParaIsForbiddenRules` + `ForbiddenCharacters` | `style:line-break` | Same API; render Pending | Settings **yes**; layout **defer** |
| Line-end prohibitions | Yes | same | same | same | Settings **yes**; layout **defer** |
| Hanging punctuation | Yes (body); off in multiportion | `ParaIsHangingPunctuation` | `style:punctuation-wrap` | Pending corpus | Settings **yes**; layout **defer** |
| Punctuation compression | Yes (doc/Options) | `CharacterCompressionType` | settings.xml path | Pending | Settings **yes** |
| Line adjustment | Built-in | Indirect only | Indirect | Pending | **Not feasible** usefully |
| Rendered line boundaries | Internal layout | Partial (`XLineCursor` / a11y `LINE`) | N/A | Untested | **Defer from E2 default** |
| Warichū internal breaks | Shared `Guess`, no line-2 post-filter; known unsafe cases | Combine only | Combine attrs | Observed Stage B | **Advisory heuristic only** |

## Recommendation

Proceed to **Stage E2 textual/settings inspector** after review. Complete corpus screenshots as parallel hardening, not as a blocker for the settings readout. Treat live-view line-start APIs as a **later optional** track with a vertical + annotation false-positive gate—not the E2 default.
