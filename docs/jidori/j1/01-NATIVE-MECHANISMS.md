# Stage J1 — Native Writer mechanisms

**Host:** LibreOffice Writer **26.8.0.3**.  
**IDL:** `com.sun.star.style.CharacterProperties`.

## Properties (confirmed)

| UI (Position tab) | UNO | Unit / meaning | ODF tendency |
|---|---|---|---|
| Scale width | `CharScaleWidth` | `short`, percent; 100 = normal | `style:text-scale` |
| Spacing | `CharKerning` | `short`, **twips** (`CONVERT_TWIPS` in Writer map) | letter-spacing / kerning |
| Pair kerning | `CharAutoKerning` | boolean | leave alone for CJK jidori |
| Character style | `CharStyleName` | string | style linkage |
| Property state | `getPropertyState` | DIRECT / DEFAULT / AMBIGUOUS | needed for restore |

There is **no** first-class jidori / Fit Text UNO property. OOo proposal i90868: Fit Text UI writes Scale + Spacing only; **no file-format change**.

## Approaches

### A — Spacing only (`CharKerning`)

- **Expand:** extra advance = `(N − n) / (n − 1)` em per gap → convert to twips.  
- **Compress:** negative kerning (limited; glyphs may collide before reaching small N).  
- **Glyphs:** proportions preserved.  
- **JLREQ:** preferred for classic 字取り.  
- **Live H (2026-10-29):** at 10.5 pt, ~**10 pt** Spacing ≈ 1 em/gap; 3 kana → 5 cells matched visually.

### B — Scale only (`CharScaleWidth`)

- **Shrink:** `scale% ≈ 100 × N / n`.  
- **Expand:** scale > 100 widens glyphs (distorts; avoid for expand).  
- **Help wording:** “horizontally stretch or compress” — **vertical-axis behaviour is a release gate** (see `03-VERTICAL-GATE.md`).  
- **Live H:** ~**55%** for 5→3 cells (formula 60%); acceptable approximation.

### C — Combined

- Expand with A; shrink with B (OOo Fit Text equations).  
- **Recommended MVP policy** if vertical gate passes for each channel used.

## Endpoint model (spacing)

OOo Fit Text / JLREQ use **(n − 1) gaps** (space *between* characters).

**Live evidence (H):** Spacing that matched あいう → width of あいうえお used ~(N−n)/(n−1) em, not n trailing gaps. If Writer had added a full trailing cell after the last glyph, the run would have overrun ~1 em — it did not.

**Still verify in V writing and with justification/grid on** (smoke sheet).

## Script / measurement assumptions (MVP)

| Case | Policy |
|---|---|
| CJK ideograph / kana (fullwidth-like) | Assume ≈ 1 em/cell |
| Proportional Latin / digits | **Refuse or warn** until measured advance exists |
| Supplementary-plane (`𠮷`) | Count as one grapheme; assume 1 em if font has glyph |
| Mixed script | Refuse unsafe mix for MVP |

Do not promise mixed-script fitting without a real advance measure.
