# Punctuation spacing, compression, hanging, and line adjustment

Evidence base: JLREQ (verified), LO Help, UNO IDL, Writer/`i18npool` source on `core` master (2026-10-29). Corpus render results: **Pending** (K06–K08).

## Punctuation spacing (約物のアキ)

**JLREQ:** half-em character advance for commas/periods/brackets/middle dots, with added spacing beside kana/kanji so frames often *look* full-width; consecutive punctuation drops some gaps ([positioning of punctuation marks](https://www.w3.org/TR/jlreq/#positioning_of_punctuation_marks)).

**Writer:**

- Does **not** expose a full JLREQ spacing table through UNO.
- Asian–Western gap: paragraph `ParaIsCharacterDistance` → ODF `style:text-autospace`.
- Visible “full-width” punctuation often comes from **font metrics** + compression mode, not from marinaMoji-readable per-glyph aki properties.
- **Do not** diagnose “wrong aki” from glyph ink boxes alone.

## Punctuation compression (約物の詰め)

| Control | Scope | UNO |
|---|---|---|
| Options → Asian Layout → Character spacing | Application default | Seeds new docs / UI |
| Document setting | Per document | `CharacterCompressionType` (`NONE` / `PUNCTUATION_ONLY` / `PUNCTUATION_AND_KANA`) |
| Kern Asian punctuation | Document | `IsKernAsianPunctuation` |

**Not** among `ParagraphPropertiesAsian` booleans — compression is document-level (**Confirmed** IDL).

Corpus must compare the three compression modes at mid-line, line-end, consecutive punct, and Latin adjacency (K07).

## Hanging punctuation (ぶら下げ)

| Fact | Status |
|---|---|
| Paragraph toggle | `ParaIsHangingPunctuation` / ODF `style:punctuation-wrap` |
| Eligible glyphs (ja) | Locale `LineBreakHangingCharacters` = `、。，．` |
| Implemented in | `BreakIterator_CJK` + `SwTextGuess` → `SwHangingPortion` |
| Disabled when | Multiportion (`IsMulti`), table cell, field group — see `guess.cxx` |
| Distinct from | Forbidden-character pull-back |

Help wording matches: commas/periods stay at line end even into the margin.

## Line adjustment (行の調整)

Writer justifies / fits lines using break opportunities from the CJK+ICU iterator, hanging portions, and compression measurements. There is **no** UNO API that returns “amount of aki compressed on this line.”

Inspector implication: treat line-adjustment quality as **out of scope** for Stage E2 unless geometry APIs improve.

## Interaction summary

```text
ParaIsForbiddenRules ──► applyForbiddenRules in BreakIterator_CJK
ParaIsHangingPunctuation ──► allowPunctuationOutsideMargin (body only)
CharacterCompressionType ──► measurement / packing (document)
ParaIsCharacterDistance ──► Asian–Western autospace
Font metrics ──► visible ink vs full-width frame
```
