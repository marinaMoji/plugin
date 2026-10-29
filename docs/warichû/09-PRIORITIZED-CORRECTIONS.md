# Prioritized corrections — LibreOffice warichū (Stage A → B)

**Rule:** report and classify before substantial product UI. Do not hide renderer limits with spaces, images, or fake structure.

## Ranking criteria

Scholarly value · JLREQ relevance · Implementation complexity · Compatibility risk · Upstream acceptance likelihood.

---

## P0 — Already correct enough for scholarly MVP (keep)

| Item | Action |
|---|---|
| Character-span `CharCombineIsOn` only | Keep; refuse whole-paragraph |
| Exact Unicode preservation | Keep |
| No UNO Prefix/Suffix | Keep until paint bug fixed |
| Toolbar Apply / Remove | Keep; polish caret-aware remove |

## P1 — Plugin work (high value, low risk)

| # | Correction | Why | Complexity | Risk |
|---|---|---|---|---|
| P1.1 | Formal smoke checklist + golden ODTs for classic example | Evidence for Gate 1 completeness | Low | Low |
| P1.2 | Soft **division preview / warning** (string analysis only): show host-likely mid-split and flag kinsoku-risky midpoints | Scholars see risk without claiming control | Low–med | Low |
| P1.3 | Document host limits in Help / dialog copy | Honest UI | Low | None |
| P1.4 | Vertical writing smoke + screenshot | JLREQ primary mode | Low | Low |
| P1.5 | Multi-font smoke (Noto / IPAex / LO default) | Metrics variance | Low | Low |

**Do not** ship alignment-mode pickers, size sliders, or “manual break” that rewrite text.

## P2 — Narrow investigations (may unlock small prototypes)

| # | Question | Success = |
|---|---|---|
| P2.1 | Does `CharKerning` / character spacing on the **combine span** change shorter-line stretch behaviour? | Documented yes/no with ODTs |
| P2.2 | Literal `（` `）` *outside* vs *inside* the combine span | Visual + XML comparison; label as workaround if used |
| P2.3 | Paragraph Adjust (left/justify) effect on `CalcNewBlock` inside warichū | Document interaction |
| P2.4 | DOCX export of `text-combine` | Text integrity first; appearance second |

Any P2 prototype must be reversible and text-safe.

## P3 — Upstream LibreOffice (proper fixes)

| # | Proposal | Scholarly / JLREQ | Complexity | Compat | Upstream odds |
|---|---|---|---|---|---|
| U1 | Fix UNO/UI Prefix/Suffix paint collapse | Delimiters (J4) | Med | High if regression-tested | **Good** (bugfix) |
| U2 | Replace hard-coded `SetProportion(50)` with item or doc setting | Size (J2) | Med | Medium | Fair |
| U3 | Explicit alignment for shorter line (left/centre/right/justify) instead of only `CalcNewBlock` | Alignment modes | Med–high | Medium | Fair |
| U4 | Optional soft break / division index on `SvxTwoLinesItem` + ODF | Manual division (J8) | High | Needs ODF story | Harder |
| U5 | Prefer kinsoku-legal first-line breaks when searching `nActWidth` | J9 | High | Behaviour change | Needs careful tests |

**Smallest high-impact upstream patch:** **U1** (brackets), then **U2** (size), then **U3** (alignment). **U4** is the scholarly “perfect” control but needs standards work.

## P4 — Deferred / refuse

| Item | Reason |
|---|---|
| Space / ZWSP alignment hacks | Violates text integrity |
| Image / drawing warichū | Not editable scholarly text |
| Claiming JLREQ conformance | Host still owns paint |
| Word-first work | User: perfect LO first |
| Full shared typography engine driving LO paint | Engine may **advise**; paint stays host until U4-class APIs exist |

## Recommended next execution order

1. Finish smoke (NEXT-LO.md) + corpus ODTs for classic / unequal / punctuation / vertical.  
2. Soft diagnostics only if useful during smoke.  
3. File or draft upstream notes for **U1** with minimal repro (UNO Prefix/Suffix).  
4. Only after measurements: consider one P2 spacing experiment as a **documented** spike, not product default.

## Success criteria (refinement phase)

A professional Japanese typesetter should be able to say: marinaMoji applies **native** warichū correctly, documents **exactly** what Writer does (50% scale, width-balanced wrap, shorter-line stretch), and does not pretend to control what `SvxTwoLinesItem` cannot express.
