# A. Native ruby capability matrix

**Host:** LibreOffice Writer **26.8.0.3** (spike environment)  
**API path:** character properties on `XPropertySet` (same props Asian Phonetic Guide uses)

## UNO properties

| Property | Type / values | Persists | Notes |
|---|---|---|---|
| `RubyText` | string | Yes → ODF `text:ruby-text` | Empty string removes the reading; Writer may leave empty `text:ruby` wrappers on following runs if sticky attrs remain |
| `RubyAdjust` | enum 0–4 | Yes → `style:ruby-align` | See mapping below |
| `RubyPosition` | enum (LO 6.1+) | Yes → `style:ruby-position` / `loext:ruby-position` | `0` = ABOVE (above in H; right side in V) |

marinaMoji does **not** set a separate ruby font size or family. Metrics follow the host character style / Asian font of the base.

## RubyAdjust → ODF `style:ruby-align`

| UNO | Name | ODF |
|---|---|---|
| 0 | LEFT | `left` |
| 1 | CENTER | `center` |
| 2 | RIGHT | `right` |
| 3 | BLOCK | `distribute-letter` |
| 4 | INDENT_BLOCK | `distribute-space` |

Verified by saving ODTs from the align spike (`Ru1`…`Ru5` automatic styles).

## Representation model

| Model | Native Writer? | marinaMoji |
|---|---|---|
| **Group ruby** (one reading over a multi-character base) | Yes — select N chars, set one `RubyText` | **This is what Apply ruby creates** |
| **Mono-ruby** (one reading per base character) | Yes — apply separately per character | Not automated; user can select one character |
| **Jukugo-ruby** (per-character readings with compound overhang rules) | **No** distinct model | Not implemented; would need multiple mono spans + custom overhang |

## Writing direction

Same properties in horizontal and vertical. `RubyPosition ABOVE` means:

- Horizontal: reading above the base  
- Vertical: reading on the **right** of the base (JLREQ conventional side)

No separate vertical UNO API was found or needed.

## Operations

| Operation | Native | marinaMoji |
|---|---|---|
| Insert | Asian Phonetic Guide / UNO | Dialog + UNO |
| Remove | Clear phonetic guide | Clear `RubyText` (selection or caret-expanded span) |
| Edit reading | Host UI | Re-apply or host UI |
| Search base | Yes | Yes (base remains document text) |
| ODT round-trip | Yes | Yes |
| Usable without marinaMoji | Yes | Yes |

## Not exposed / not used by marinaMoji

- Per-ruby font size override via UNO (host styles only for now)
- Explicit overhang controls beyond alignment mode
- Dual ruby (two readings on one base)
- Katatsuki vs nakatsuki as named modes (alignment enum is the substitute)
