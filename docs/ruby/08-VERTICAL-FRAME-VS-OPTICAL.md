# Vertical ruby: character frames vs optical centres

**Scope:** `本文` + `もと` in vertical writing under `CENTER`, `BLOCK`, `INDENT_BLOCK`.  
**Constraint:** No product default change; no artificial spaces.  
**Artifacts:** `libreoffice/spikes/ruby/artifacts/vertical_geometry/`  
**Host:** LibreOffice 26.8.0.3 · fonts Hiragino Mincho ProN + Hiragino Sans (角ゴ) · grid ON/OFF

## 1. What JLREQ actually prescribes

JLREQ positions ruby using **square character frames and advances**, not the optical centres of ink ([§2 character frames](https://www.w3.org/TR/jlreq/); group-ruby placement after §3.3.7).

For **group-ruby shorter than the base** (`本文` 2×1em, `もと` 2×½em solid = 1em, free space = 1em):

| Method | JLREQ | Writer / ODF | Frame geometry (block axis, em) |
|---|---|---|---|
| JIS X 4051 “balanced” 1:2:1 | Fig. **124** — lead : inter : trail = 1 : 2 : 1 | `INDENT_BLOCK` / `distribute-space` | も centre **0.5**, と centre **1.5** (= 本 / 文 frame centres) |
| Edge-aligned stretch | Fig. **125** — flush first/last edges; space only between ruby letters | `BLOCK` / `distribute-letter` | も centre **0.25**, と centre **1.75** (Δ −0.25 / +0.25 vs base centres) |
| Solid centred block | Equal-length case generalised; permitted alternative when not stretching | `CENTER` / `center` | Solid 1em block centred: も **0.75**, と **1.25** |

So for this exact 2×½-on-2×1 case:

- **INDENT_BLOCK** is the JIS/JLREQ Fig.124 arrangement: each ruby **frame** sits on each base **frame** centre.  
- **BLOCK** is the JLREQ Fig.125 alternative: ruby frames hug the start/end of the base span, with a large gap between も and と.  
- Neither method asks the engine to centre **glyph ink**.

A result can look uneven and still be typographically correct on character frames.

## 2. What the screenshots show (Writer)

Spike pages (field shading off, 28pt body):

| Adjust | Vertical appearance |
|---|---|
| **CENTER** | もと solid in the middle of 本文; empty frame space above も and below と |
| **BLOCK** | も near the top of 本, と near the bottom of 文; clear gap between ruby letters (Fig.125-like) |
| **INDENT_BLOCK** | Same distributed family as BLOCK, with a slight inset from the outer edges (Fig.124-like) |

Mincho and Gothic show the **same distribution pattern**. Document grid ON/OFF does not change which adjust mode is which; grid mainly affects overall line rhythm, not ruby letter distribution logic.

## 3. Font metrics: advance (frame) vs ink

Hiragino Mincho ProN and Hiragino Sans W3 (CFF), measured with fontTools:

| Char | Advance (em) | Ink centre vs frame centre (approx.) |
|---|---|---|
| 本 | **1.0** (square) | ~0 em cross-axis; ink sit slightly low in the em-box (~−0.12 em design-y) |
| 文 | **1.0** | similar |
| も | **1.0** | ink narrower in the box; centre near frame centre cross-axis |
| と | **1.0** | ink slightly more inset; tiny cross-axis bias vs も (~0.01 em) |

**Conclusion:** Layout uses **full-width advances** (character frames). Optical centres of 本/文/も/と are **not** identical to geometric frame centres. Any “と looks further out than も” reading is overwhelmingly **ink-inside-frame**, not a different advance width.

## 4. Is Writer using advances or glyph centres?

| Evidence | Implication |
|---|---|
| ODF stores `ruby-align` = center / distribute-letter / distribute-space | Alignment is a **frame/advance** policy |
| BLOCK vs CENTER screenshots match Fig.125 vs solid-centre **frame** models | Engine distributes along the base **span**, not ink centroids |
| All tested JP glyphs have advance = 1em | No proportional advance driving the gap |
| PDF text layer often **omits** body ruby glyphs | Export/measurement caveat; on-screen paint still shows frame distribution |

Writer’s vertical ruby algorithm here is **character-frame / advance based**. It is not an optical-centre aligner.

## 5. Cause of the perceived misalignment

Ordered by importance:

1. **BLOCK’s frame geometry (Fig.125)** — も is not meant to sit on 本’s centre; と is not meant to sit on 文’s centre. The large mid gap is correct for edge-aligned stretch.  
2. **Optical unevenness inside frames** — Mincho/Gothic letter faces are not centred in the em-box; と is optically lighter/narrower than も.  
3. **Not** marinaMoji mis-setting UNO (same props as Asian Phonetic Guide).  
4. **Not** fixed by document grid alone.  
5. **Not** fixed by inserting spaces (forbidden; would corrupt text).

## 6. UNO vs upstream

| Change | Via UNO? | Notes |
|---|---|---|
| Prefer Fig.124 pairing (`INDENT_BLOCK`) for short group-ruby | **Yes** | **marinaMoji 0.3.19+ default** — frame pairing for 本文/もと; still not optical |
| Prefer solid centre (`CENTER`) | **Yes** | Host UI / alternative convention |
| Keep Fig.125 stretch (`BLOCK`) | **Yes** | Valid JLREQ alternative; retained internally for future controls |
| Align ruby ink to optical centres of base ink | **No** | Not exposed; would need font/layout engine work |
| Per-glyph side-bearing compensation in vertical | **No** | Upstream / font feature territory |

**Verdict:** Perceived “misalignment” under `BLOCK` is largely **correct Fig.125 frame distribution** plus normal optical variation — not a Writer defect. marinaMoji’s **product default** is Fig.124 via `INDENT_BLOCK` (0.3.19+). That is a typographic policy choice, not a claim that JLREQ forbids Fig.125.

Do **not** file Bugzilla unless a reproducer shows stored `distribute-letter` while painting clearly violates Fig.125 frame edges (we did not establish that).

## 7. Measurement limits

- Body ruby often absent from PDF text extraction → automated bbox pairing against も/と in the PDF layer is unsafe (labels polluted earlier runs).  
- Visual comparison of spike PDFs/PNGs + theoretical frame model + font advances are the reliable evidence chain.  
- Scripts: `ruby_vertical_geometry_spike.py`, `measure_vertical_ruby_geometry.py`, `run_ruby_vertical_geometry_spike.sh`.

## 8. Product implication (0.3.19)

- Default **`INDENT_BLOCK`** (Fig.124 / JIS 1:2:1 / ODF `distribute-space`).  
- Document both Fig.124 and Fig.125 as JLREQ-valid; marinaMoji picks Fig.124.  
- Never “fix” vertical look with spaces or zero-width characters.
