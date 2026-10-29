# F. Upstream issues (ruby) — do not file without approval

Keep separate from warichū **tdf#174224**.

## R1 — Sticky empty `text:ruby` after clearing `RubyText` (observation)

| Field | Detail |
|---|---|
| Summary | After setting and clearing `RubyText` on a cursor flow, later inserts can be wrapped in `<text:ruby>…<text:ruby-text/></text:ruby>` with empty readings |
| Expected | Cleared ruby leaves ordinary text runs |
| Actual | Empty ruby wrappers appear on headings / following text in automated inserts |
| JLREQ | N/A (host serialization) |
| LO | 26.8.0.3 |
| H/V | Both |
| PDF | Invisible; ODF polluted |
| marinaMoji | Avoid clearing `RubyText` on unrelated runs; product apply only touches the selection |

**Status:** Documented. Not filed. Mitigate in spikes by not broadcasting empty RubyText on every insert.

## R2 — No native jukugo-ruby model

| Field | Detail |
|---|---|
| Summary | Writer stores one reading per contiguous base; no jukugo overhang/split semantics |
| Expected (scholarly) | Per-character readings with compound rules (JLREQ) |
| Actual | Group or manual mono only |
| Status | Limitation, not a “bug” — feature gap. No Bugzilla unless maintainers want an enhancement. |

## R3 — Vertical LEFT looks like “broken centering”

| Field | Detail |
|---|---|
| Summary | `RubyAdjust=LEFT` places short ruby at the start of the base in vertical writing |
| Expected | Correct for LEFT; wrong if the user intended CENTER/BLOCK |
| Actual | Matches LEFT |
| Status | **Not a Writer defect** if LEFT was set. Use INDENT_BLOCK/BLOCK/CENTER. marinaMoji 0.3.19 defaults to INDENT_BLOCK. |

## Not claimed as upstream defects

- Ruby-to-base gap in vertical (host metrics; matches native phonetic guide).  
- Overhang of long readings into neighbours (JLREQ-permitted; Writer allows).  
- Grey field shading while editing (View → Field Shadings).

## Reproducers

Minimal ODTs: `libreoffice/spikes/ruby/artifacts/align_spike/ruby_align_{horizontal,vertical}.odt`  
(Open with field shading off; compare LEFT / CENTER / BLOCK rows.)
