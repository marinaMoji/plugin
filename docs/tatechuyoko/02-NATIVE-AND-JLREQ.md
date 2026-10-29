# Tate-chū-yoko — native capability + JLREQ

## Stage A verdict (user smoke, vertical Writer)

marinaMoji’s `CharRotation=900` + `CharRotationIsFitToLine=True` produces a
legible horizontal `12` inside `令和12年` in vertical writing. Ordinary vertical
composition stacks the digits.

| Question | Answer |
|---|---|
| Mechanism | Character rotation + fit-to-line (Format → Character → Position) |
| `CharCombineIsOn`? | **No** (that is warichū / `text-combine=lines`) |
| Kumimoji? | **No** — different product concept |
| Suitable for conventional 2-digit 縦中横? | **Yes**, as LO’s documented approximation |
| First-class LO “tate-chū-yoko”? | **No** |
| ODF | `style:text-rotation-angle` (typically 90) |

## JLREQ (W3C)

- Vertical Latin/digits: rotate, upright, or **tate-chu-yoko** (horizontal-in-vertical).
- Main use: **two-digit European numerals**; also short Latin (about 2–3 letters).
- Characters keep normal orientation and sit on a horizontal baseline within the vertical line; proportional/half-width glyphs are typical.
- JIS X 4051 §4.8 referenced by JLREQ.

### Separation of concerns

| Layer | Content |
|---|---|
| **A. JLREQ convention** | Short horizontal runs (esp. 2 digits) in vertical text |
| **B. Editorial practice** | Years, chapter nos., short Latin labels |
| **C. marinaMoji policy** | Auto-apply only exact 2-grapheme digit/Latin; 3–4 confirm; Japanese prose refuse; never silently shrink an explicit selection |

## Difference from warichū / kumimoji

| Feature | Host property | Role |
|---|---|---|
| Tate-chū-yoko | `CharRotation` + fit | Short upright horizontal run in vertical text |
| Warichū | `CharCombineIsOn` | Two-line inline note |
| Kumimoji | (not used) | Combined emblem-like characters |
