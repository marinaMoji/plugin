# C. Horizontal / vertical comparison

## Environment (align spike)

| Item | Value |
|---|---|
| LibreOffice | 26.8.0.3 |
| OS | macOS (darwin) |
| Font | Hiragino Mincho ProN (also present: Songti SC / Noto Sans SC as fallbacks in ODT font decls) |
| Main size | 14 pt |
| Ruby size | Host default (~½) — not set by plugin |
| Paragraph | Standard + Asian `ja-JP` |
| Grid | None forced |
| Creation path | Same UNO as marinaMoji / Asian Phonetic Guide (`RubyText` + `RubyAdjust` + `RubyPosition`) |
| Field shading | Off for PDF thumbs |

Artifacts: `libreoffice/spikes/ruby/artifacts/align_spike/`  
(`ruby_align_horizontal.odt/.pdf/.png`, `ruby_align_vertical.odt/.pdf/.png`, `ruby_align_report.json`, `odf_*.json`)

## marinaMoji vs native LibreOffice

**Result:** Identical when the same UNO values are set.

marinaMoji does not use a custom layout path. Asian Phonetic Guide and marinaMoji both write `RubyText` / `RubyAdjust` / `RubyPosition`. If properties match, ODF and rendering match.

Implication: a vertical layout that looks “wrong” under CENTER is **not** a marinaMoji-only bug; it is either (a) a suboptimal alignment choice relative to JLREQ, or (b) a Writer layout quirk shared with the native UI.

## Horizontal (`本文` / `もと`)

| Adjust | Appearance (14 pt Mincho) |
|---|---|
| LEFT | Reading packed toward the start of the base |
| CENTER | Solid reading centred over the base — attractive |
| RIGHT | Packed toward the end |
| BLOCK | Letters of `もと` spaced to span the base — JLREQ stretch |
| INDENT_BLOCK | Similar stretch with inset ends |

Ruby-to-base gap: moderate, consistent; matches host phonetic-guide metrics. Not treated as a defect.

## Vertical

| Adjust | Appearance |
|---|---|
| LEFT | Reading toward the **top** (start) of the base column — matches the “stuck at the beginning” look in the supplied vertical screenshot |
| CENTER | Reading as a solid block **centred** beside the base (works when CENTER is actually set) |
| RIGHT | Toward the **bottom** (end) of the base |
| BLOCK | Reading characters distributed along the full height of `本文` |
| INDENT_BLOCK | Distributed with insets |

**Interpretation of the user’s vertical screenshot:** grey field shading on `もと` plus adjacency to warichū made a **LEFT-like / start-heavy** appearance easy to see. With field shading off and CENTER correctly applied, vertical centering is available. For shorter group-ruby, marinaMoji defaults to **INDENT_BLOCK** (Fig.124); **BLOCK** remains the Fig.125 alternative.

## Combined example (ruby + warichū + `国際`)

Warichū on the following span does **not** rewrite `RubyAdjust` on the ruby span. Visual tension can still appear because:

1. Warichū doubles the line thickness of the note span.  
2. Start-aligned (LEFT) or tight CENTER solids leave empty space along the base next to the note.  
3. INDENT_BLOCK / BLOCK distribute along the base axis (different end insets).

Control: isolated ruby vs ruby+warichū in the spike — same UNO values; warichū does not invert alignment.

## PDF export

Alignment differences survive PDF export (spike PDFs). Grey field shading does **not** appear in PDF when shading is off.
