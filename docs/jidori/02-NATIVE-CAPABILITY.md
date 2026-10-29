# LibreOffice — native capability for jidori

**Environment:** LibreOffice 26.8.0.3 (marinaMoji kinsoku/inspector baseline).  
Confidence: **Confirmed** (Help / IDL) · **Hypothesis** (equations / Word import).

## No first-class “Fit Text / 字取り” API

Current Writer Help and `CharacterProperties` IDL do **not** expose a dedicated jidori property or a Fit Text dialog tab.

An OpenOffice.org proposal ([Alignment Distributed / Fit Text](https://wiki.openoffice.org/wiki/Alignment_Distributed), issue i90868) described Fit Text as a **UI convenience** that writes existing Position-tab properties — **not** a new file-format attribute. Status was preliminary; LO 26.8 Help still documents Scale width + Spacing under **Format → Character → Position**, with no separate Fit Text page.

## Primitives that can approximate jidori

| Mechanism | UI | UNO | ODF (typical) | Role for jidori |
|---|---|---|---|---|
| Scale width | Character → Position → Scale width | `CharScaleWidth` (`short`, %; 100 = normal) | `style:text-scale` | Compress when target &lt; natural width |
| Character spacing | Character → Position → Spacing | `CharKerning` (`short`, **twips**) | letter-spacing / kerning attrs | Expand (or tighten) gaps between characters |
| Pair kerning | Position → Pair kerning | `CharAutoKerning` | — | Usually leave alone for CJK jidori |
| Fit to line | Position → Fit to line | `CharRotationIsFitToLine` | — | **Tate-chū-yoko**, not jidori |
| Distributed alignment | Paragraph alignment | `ParaAdjust` / last-line justify | fo:text-align | **Furiwake-like**, whole line |

### OOo proposal equations (historical, still the practical approach)

From the Fit Text wiki proposal:

- **Shrink (target narrower):**  
  `CharScaleWidth ≈ 100 × (target_width / current_width)`  
- **Expand (target wider):**  
  Extra space split across gaps:  
  `(target_width − current_width) / (n_chars − 1)` → Spacing / `CharKerning`

marinaMoji would implement the **calculator + apply/clear**; Writer remains the renderer.

### Live check (2026-10-29, 10.5 pt)

| Target | Predicted | Observed (Position dialog) |
|---|---|---|
| あいう → 5 cells | +1 em/gap ≈ **10.5 pt** Spacing | **~10 pt** Spacing (equal to あいうえお) |
| あいうえお → 3 cells | Scale **60%** | **~55%** Scale (visually ≈ 3 cells) |

Equations are good enough for an approximation UI; expect small font-metric drift.

## Measuring “current width”

True rendered run width is the same hard problem as kinsoku layout geometry (view/accessibility only; fragile headless).

**Pragmatic spike assumption for CJK-fullwidth runs:**

`current_width ≈ n_graphemes × Asian_em`  
`target_width ≈ N_cells × Asian_em`  

where `Asian_em` comes from `CharHeightAsian` (or Western height if Asian unset).

Validate visually against Format → Character measurements; do not trust the approximation for proportional Latin without further work.

## Document grid

Asian document grid changes the **page** character cell geometry. Jidori target “N cells” should eventually respect grid em if the page uses a character grid — **Pending** spike with grid on/off.

## Word / DOCX

| Host | Native fit-to-width |
|---|---|
| Word | `w:fitText` |
| Writer | No dedicated property; DOCX import mapping of `fitText` → LO spacing/scale is **unverified** in this stage (filter search did not surface an obvious live mapping in the paths checked). |

Do not promise DOCX round-trip in an MVP.

## Known risk: CharScaleWidth regressions

Bug discussions around LO 26.2 (`tdf#171389`) reported `style:text-scale` / Scale width ignored after glyph-scaling work (`tdf#168251`). **Must re-test on 26.8.0.3** before shipping any apply command that depends on scale.

## Capability matrix (interim)

| Need | Writer native | UNO | ODF persist | Vertical | marinaMoji path |
|---|---|---|---|---|---|
| Dedicated jidori object | **No** | — | — | — | Approximate |
| Fit run to N cells | Approximate via scale + kerning | `CharScaleWidth`, `CharKerning` | Yes (those attrs) | Likely same props | Spike → MVP if smoke OK |
| Whole-line distribute | Yes (alignment) | Para adjust | Yes | Yes | Defer to Furiwake |
| Word fitText parity | No | — | Lossy | — | Later / Word host |
