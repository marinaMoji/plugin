# Native capability matrix — LibreOffice warichū

**Legend**

| Code | Meaning |
|---|---|
| N | Supported natively (UI / ODF / stable paint) |
| L | Supported with limitations |
| U | Achievable through UNO today |
| W | Achievable via reliable native-document workaround |
| C | Requires LibreOffice core (or ODF) changes |
| X | Unsupported / refuse |

Plugin must **not** expose a control that silently does something else.

| Feature | Classification | Notes |
|---|---|---|
| Apply two-line warichū to selection | **N / U** | `CharCombineIsOn` + text span; ODF `style:text-combine="lines"` |
| Remove warichū, keep text | **U** | Clear combine props; caret-aware remove still polish |
| Whole-paragraph combine | **X** (refuse) | Overlap / illegible on LO 26.8 |
| Exact text preservation | **N** (policy) | MVP does not rewrite characters |
| Inherit writing direction | **N** | Surrounding paragraph |
| Explicit annotation font size | **L / C** | Host scales; no proven UNO inner size |
| Inner interline gap = 0 (JLREQ) | **L / C** | Observe only; no control |
| Vertical centering on main line | **L** | Appears roughly correct; unmeasured |
| Automatic line division | **N** | Host algorithm; opaque |
| Manual division point (logical) | **C** | No ODF/UNO break marker found; do **not** insert spaces |
| Pre-check / warn bad midpoint | **U** (soft) | Plugin can analyze string; cannot force host split |
| Beginning alignment of both lines | **L** | Observed for equal lengths |
| Centre shorter line | **C** (likely) | Not exposed |
| End alignment | **C** | Not exposed |
| Distributed spacing to equal width | **C** / maybe **L** | Char spacing may be whole-span only |
| Scholarly correspondence points | **C** / future engine | Beyond JLREQ |
| Japanese punctuation spacing inside | **L** | Untested systematically |
| Kinsoku at inner break | **L / C** | Untested; enforce only via upstream or soft warn |
| UNO Prefix/Suffix delimiters | **X** on 26.8 UNO path | Paint collapse |
| UI delimiters | **L** | Retest; treat fragile |
| Literal bracket characters in note | **W** (provisional) | Not true cl-28/29; document trade-off |
| Vertical composition | **L** | Needs corpus; inherit mode |
| Interaction with ruby / kaeriten | **L** | Phase 3 smoke |
| ODT round-trip | **N** (expected) | Must stay in corpus |
| DOCX export fidelity | **L** | Document gaps; text first |
| Font-independent metrics | **L** | Multi-font corpus required |
| Shared typography engine driving LO paint | **C** / deferred | Engine may **advise**; paint stays host |

## Alignment modes (desired vs reality)

| Mode | Status |
|---|---|
| Automatic JLREQ | **Aspirational** — host auto only |
| Beginning | **Partial** — equal-length cases |
| Centre | **Core** unless proven via spacing hack (refuse fragile hacks) |
| End | **Core** |
| Distributed | **Core** or whole-span spacing only |
| Scholarly | **Future** — not JLREQ; do not fake |

## Decision rule for the UI

Only ship controls that map to **N**, **U**, or documented **W**.  
Mark **C** items as “LibreOffice limitation” in docs/help — never as a silent fallback.
