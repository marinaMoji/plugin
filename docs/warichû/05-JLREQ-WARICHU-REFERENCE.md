# JLREQ warichū technical reference (Stage A)

**Sources:** [W3C JLREQ](https://www.w3.org/TR/jlreq/) (inline cutting note / 割注, §3.3.5 area; character classes cl-28/cl-29); JIS X 4051 §4.16 as cited by JLREQ.  
**Status:** Extracted for marinaMoji planning. Not a claim that marinaMoji or LibreOffice currently conform.

Labels for “normative force”: **D** = descriptive JLREQ practice; **C** = conventional / common; **A** = alternative allowed; **K** = kinsoku-related; **V/H** = vertical / horizontal relevance.

| ID | Spec locus | Behaviour | Force | Mode | LO today (26.8) | Plugin can influence? | Needs LO core? |
|---|---|---|---|---|---|---|---|
| J1 | JLREQ warichu intro | Two lines of small characters inserted inline (“割り書き”). | D | V primary; H rare | Partial: `text-combine="lines"` / `CharCombineIsOn` | Apply/remove span | No for basic on/off |
| J2 | Character size | Usually ~6 pt relative to kihon-hanmen; size “by specification.” | C | Both | Scale appears **host-fixed** (~half / combined portion proportion); no UNO size for inner lines found | Unlikely via UNO alone | Yes for explicit scale |
| J3 | Inner line gap | Space between the two warichū lines is **0**. | C | Both | Appears tight/overlapping at times; not separately controllable | No | Yes for inner gap |
| J4 | Delimiters | Common: `(` `)` at **2×** warichū character size; solid to adjacent kana/kanji. Alt: spacing instead of brackets. | C / A | Both | UNO Prefix/Suffix **breaks paint** on tested build; UI Asian Layout may differ | Literal chars in text (unverified typography); not UNO brackets | Yes to fix UNO/UI delimiter paint |
| J5 | cl-28 / cl-29 | Warichū brackets are **separate character classes** from ordinary brackets (spacing/kinsoku differ). | D | Both | Unknown whether LO treats Prefix/Suffix as cl-28/29 | No | Likely yes for correct classes |
| J6 | Centering on main line | Warichū block wider than main character; **centers** aligned with main line in line-progression direction; jut into line gap both sides equally. | D | V (stated); H analogous | Plausible for working span cases (annotation sits mid-line height); not measured | No | Maybe for metric accuracy |
| J7 | Kihon-hanmen line gap | Main line gap unchanged globally; gap *looks* narrower beside warichū; design wider kihon gap if warichū expected. | D | Both | Paragraph line spacing user-controlled; warichū may inflate line box | Indirect (paragraph spacing) | Soft |
| J8 | Balance two lines | Lengths as equal as possible; break at **permitted** break; second line **not longer** than first. | D | Both | Empirical: 10-char `割り注は、良いです。` → `割り注は、` / `良いです。` (midpoint). Algorithm not proven generally | Soft advice only; **no native division-point property** | Yes for explicit break |
| J9 | Same kinsoku as body | Inner break uses same line-break rules as main text. | D / K | Both | Unknown; no plugin control of inner break | Soft pre-check / diagnostics only | Yes for guaranteed kinsoku |
| J10 | Punctuation inside | Body punctuation rules apply inside warichū. | D | Both | Unknown / font-dependent | Limited | Possibly |
| J11 | Straddle main lines | May wrap across 2+ main lines with defined reading order; >3 rare — prefer other note styles. | D | Both | Untested | N/A until tested | Maybe |
| J12 | Vertical preferred | Warichū common in vertical; uncommon in horizontal (study guides/encyclopedias). | C | V/H | LO has both writing modes | Inherit writing mode | No |

## Defaults proposal (marinaMoji scholarly profile)

Pending measurement against (J2)–(J8). Working defaults for the **plugin**:

| Property | Proposed default | Notes |
|---|---|---|
| Type | Native warichū span | Confirmed workable |
| Lines | Two | Host |
| Size | Host default (~half) | Do not fake with CharHeight on whole span without tests |
| Division | Host automatic | Do not claim plugin-controlled split |
| Inner gap | Host (target 0) | Upstream if wrong |
| Alignment | Host automatic | Modes below are **aspirational** |
| Delimiters | None (MVP) | Literal `（）` experiment later; not UNO Prefix/Suffix |
| Writing direction | Inherit | |
| Font | Inherit Asian font | |
| Text | Exact preservation | Non-negotiable |

**Do not equate** nominal half-size, glyph bbox, character frame, baseline, and line height — JLREQ talks in character-frame / kihon-hanmen terms.
