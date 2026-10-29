# Stage J2 — Reversibility design (draft)

## Problem

`CharScaleWidth` / `CharKerning` are ordinary character properties. After apply they are indistinguishable from hand-set Position values **unless** marinaMoji leaves an identity marker that survives ODT.

Resetting to 100 / 0 is **Reset spacing**, not **Remove jidori**.

## Candidate strategies

### A — Bookmark + document UserDefinedProperties (preferred draft)

1. On Apply, read prior `CharScaleWidth`, `CharKerning`, their `PropertyState`, and `CharStyleName`.  
2. Wrap the run in a named bookmark: `marinaMoji.jidori.<id>`.  
3. Store JSON (or delimited) restore payload in `UserDefinedProperties` key `marinaMoji.Typography.Jidori.<id>`: `{N, scale, kern, scaleState, kernState, charStyle, textHash?}`.  
4. Apply calculator values as **direct** formatting.  
5. On Remove: find bookmark intersecting selection → restore props → delete bookmark + UDP entry.  
6. Reapply: same id; recompute from baseline `n` and **stored** prior props; update N + applied values only.

**Pros:** Survives ODT if bookmarks + UDP round-trip; identifies “our” jidori; preserves prior formatting.  
**Cons:** Bookmarks visible in Navigator; edit/split may orphan metadata; must detect stale ids.

### B — Dedicated character style per N

`marinaMoji.Jidori.N5` etc. holding scale/kern.

**Fails** for: prior style replacement; shared style side effects; restore of previous style; unlimited styles.

### C — Marker character style only (empty) + direct scale/kern + UDP

Similar to A but identity = `CharStyleName == marinaMoji.Jidori` while restore lives in UDP keyed by… range? Without bookmarks, range identity after reopen is weak.

## Required proofs (J2 smoke)

| # | Test | Pass if |
|---|---|---|
| R1 | Apply on text with Scale 90% + custom Spacing | Remove restores **90% and custom Spacing**, not 100/0 |
| R2 | Apply with existing character style | Style name restored |
| R3 | Save ODT → reopen → Remove | Still restores |
| R4 | Select ordinary spaced text (not ours) → Remove | Message; **no change** |
| R5 | Reapply N=5 then N=7 → Remove | Restores **pre-first-apply** baseline |
| R6 | Copy-paste jidori run | Documented behaviour (may lose bookmark → refuse Remove) |

## Gate

If R1–R3 fail, **stop before toolbar**. Report limitation; do not ship Apply/Remove that lies about restore.
