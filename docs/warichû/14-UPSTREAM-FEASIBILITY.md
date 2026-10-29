# Stage B — Upstream feasibility and contribution strategy

**Constraint:** No marinaMoji fork of LibreOffice. Prefer small, standards-compatible patches. **Do not submit** bugs/PRs without approval.

## Ranked candidates (scholarly value × cost × risk)

| ID | Proposal | Scholarly value | JLREQ | Complexity | UNO | ODF | DOCX | Compat | Upstream odds | Stage B evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| **U1** | Fix bracket paint for two-line combine | High (usable delimiters) | J4 | Med (debug paint/width) | None if item already correct | None | Improves export paint | High if regression-tested | **Best first contribution** | **Confirmed** H collapse |
| **U2** | JLREQ-aware automatic division (kinsoku + balance scoring) | High | C5–C6 | Med–High | None | None | Behavioural | Medium (docs change) | Good if fixtures + i18n review | **B11 H; B19/B20 V** bad breaks |
| **U5** | Configurable annotation proportion (replace hard 50%) | Medium | Size by spec | Med | New optional prop | Possible style attr | Soft | Medium | Fair | Source hard-code; not user-reported pain yet |
| **U4** | Explicit shorter-line alignment modes | Medium | Optional conventions | Med–High | New enum | Extension? | Hard | Medium | Needs design | Stretch already exists; modes not required for MVP |
| **U3** | Manual division index | **Very high** for editions | Beyond JLREQ | High | New prop | See below | Hard | Needs graceful degrade | Harder — discuss first | No model today |

**Recommended order:** U1 → U2 → (discuss) U3 → U5 → U4.

## Smallest useful contribution

**U1 bracket paint fix** with:

- Minimal ODT repro (B16)
- Before/after screenshots
- Cppunit or UI test if layout tests exist for multiportions
- Files: `pormulti.cxx` / `pormulti.hxx` (`FormatBrackets`, `PaintBracket`, `BuildMultiPortion` bracket branch)

Discuss with LibreOffice CJK/Writer maintainers **after** local root-cause in a LO build (not done this stage).

## U2 sketch (no patch yet)

Inside double-line formatting, after an initial width-search split (or instead of relying solely on first-line fill):

1. Collect candidate break indices near the current first-line end (±N chars).  
2. Reject not-start / not-end per selected kinsoku table.  
3. Score width delta + predicted stretch.  
4. Pick best; format once.

Regression risk: existing documents’ visual line breaks may shift → needs release-note and golden tests.

## Manual division (U3) — architectural proposal

### Goals

- Continuous editable annotation string (no split into two fields).  
- Explicit break index (or marker) for scholarly control.  
- Graceful degrade: older LO → automatic division.

### Design options

| Option | Store where? | Pros | Cons |
|---|---|---|---|
| A. Extend `SvxTwoLinesItem` with `sal_Int32 nBreak` (−1 = auto) | Pool item + UNO e.g. `CharCombineBreak` | Clean; round-trips with style | ODF needs attribute; old LO ignores unknown? |
| B. Soft hyphen / special char in text | In string | No item change | **Violates** “don’t mutate scholarly text”; editing nightmares |
| C. Parallel RDF / custom field | Metadata | Noninvasive to item | Not native; LO won’t paint from it |
| D. Two formatted runs faking warichū | Fake | — | Fragile; **reject** |

**Preferred:** **Option A** if upstream accepts.

### Compatibility questions (answers provisional)

1. **Item field?** Yes — natural place beside brackets.  
2. **UNO property?** Yes — required for marinaMoji.  
3. **ODF without extension?** Current ODF `style:text-combine` has no break index. Would need OASIS proposal **or** LO-namespaced attribute with documented ignore-on-import.  
4. **Older LO?** Unknown attribute ignored → auto division (acceptable degrade).  
5. **Edit before break?** Indices must update with text edits (same class of problem as bookmarks) — hard; may store as **bookmark-like** position or re-validate on format.  
6. **Insert/delete before break?** Break index must shift; invalid index → clamp or auto.  
7. **DOCX?** OOXML `w:eastAsianLayout` has `combine` / `combineBrackets` — **no** break index found. Export would drop to auto; import from Word never has manual break.  
8. **Graceful degrade?** Yes if −1/auto default and missing attribute = auto.

### Recommendation

Do **not** implement U3 in marinaMoji until U1/U2 land or a design mail thread with LO exists. Plugin may later offer “suggested break” diagnostics only.

## Track A — Plugin-only (immediate)

| Work | Notes |
|---|---|
| Keep bare combine apply/remove | Done |
| Smoke + caret-aware remove | NEXT-LO |
| Soft diagnostics: flag notes where heuristic says kinsoku-risky mid | Predictive only; label clearly |
| Help text: no delimiter via UNO; host owns split/size | Honest UI |
| Batch inspect combine spans | Optional |
| Literal brackets experiment | Only as documented workaround after visual OK |

## Track B — Upstream (short → long)

1. Short: U1 bugfix  
2. Short–mid: U2 auto division  
3. Long: U3 manual break + ODF  
4. Optional: U5 size; U4 alignment  

## Discussion before large patches

U3 and ODF extensions **must** be discussed on LibreOffice design / OASIS lists before coding. U1 can proceed as a normal bugfix once root-caused.
