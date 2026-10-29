# B. JLREQ comparison

Source: [W3C JLREQ](https://www.w3.org/TR/jlreq/) (Requirements for Japanese Text Layout), especially §3.3 Ruby and Emphasis Dots.

## Classification of `本文` + `もと`

| Question | Answer |
|---|---|
| Mono-ruby? | No — the reading is not attached per character (`本`≠`も`, `文`≠`と` as independent units) |
| Jukugo-ruby? | No — jukugo-ruby assigns readings to each kanji in a compound with split/overhang rules |
| **Group-ruby?** | **Yes** — one reading object over the whole base sequence; line break inside the base is prohibited |

This matches how Writer stores one `text:ruby` with `ruby-base` = `本文` and `ruby-text` = `もと`.

## Alignment when the reading is shorter than the base

JLREQ **§3.3.8** (conventional default, not the only permitted method):

> When the length of a ruby text … is **shorter** than the corresponding base text, the ruby text is, in general, **stretched by adding inter-character spacing between ruby characters** …

So for `本文` / `もと`, the JLREQ-conventional treatment is **stretch** (letter distribution), not solid centering or start-alignment.

| Mode | JLREQ fit for shorter group-ruby | Writer UNO / ODF |
|---|---|---|
| Stretch with 1:2:1 end spacing (JIS) | Fig. **124** — conventional JIS balance | `INDENT_BLOCK` / `distribute-space` |
| Stretch flush to base edges | Fig. **125** — permitted alternative | `BLOCK` / `distribute-letter` |
| Centre as a solid block | Permitted alternative | `CENTER` / `center` |
| Align to line-start of base | Alternative / katatsuki-like in some traditions | `LEFT` / `left` |
| Align to line-end of base | Alternative | `RIGHT` / `right` |

For `本文`/`もと` (2×½em ruby on 2×1em base), Fig.124 puts ruby **frame** centres on base **frame** centres; Fig.125 puts ruby frames at the span ends with a mid gap. See [08-VERTICAL-FRAME-VS-OPTICAL.md](08-VERTICAL-FRAME-VS-OPTICAL.md).

**marinaMoji 0.3.19+ default:** `INDENT_BLOCK` (Fig.124) — **product choice**, not a universal JLREQ mandate.  
**0.3.18 used:** `BLOCK` (Fig.125).  
**0.3.17 used:** `CENTER`.  
`BLOCK` remains a valid JLREQ alternative and is kept in code for possible future advanced controls.

## Size and side

| Topic | JLREQ | Writer / marinaMoji |
|---|---|---|
| Ruby size | Often ~½ base em | Host default (~½); plugin does not override |
| Horizontal position | Above | `RubyPosition` ABOVE |
| Vertical position | Right of base | Same ABOVE enum → right side |
| Overhang past base | Allowed with rules at edges / neighbours | Writer permits overhang for long readings; no separate UNO |

## Requirements vs preferences

| Item | Kind |
|---|---|
| Group vs mono vs jukugo as distinct models | Requirement for correct scholarly semantics |
| Stretch shorter group-ruby | Conventional default |
| Centre shorter group-ruby | Permitted alternative |
| Exact half-size | Conventional starting point |
| Visual beauty of one screenshot | Preference — do not drive representation |

## Not addressed by JLREQ (for this investigation)

- Interaction of ruby with warichū on the *next* span  
- LibreOffice field-shading grey behind ruby while editing  
- Sticky empty `text:ruby` wrappers after clearing `RubyText`
