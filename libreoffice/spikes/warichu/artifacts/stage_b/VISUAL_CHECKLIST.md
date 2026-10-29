# Stage B visual inspection checklist (filled from PDF previews)

LibreOffice: **26.8.0.3** · Font: **Hiragino Mincho ProN** · 2026-10-29  
Sources: `warichu_stage_b_horizontal.pdf.png`, `warichu_stage_b_vertical.pdf.png`, span_spike B screenshot.

| Case | Observed upper / first | Observed lower / second | Stretch visible? | Punct odd? | Pass/Fail/Unclear |
|---|---|---|---|---|---|
| B01_classic | 割り注は、 | 良いです。 | No (equal) | — | **Pass** |
| B02_equal_qianziwen | 天地玄黄、 | 宇宙洪荒。 | No | Comma ends first | **Pass** |
| B03_long_classical | ~mid (upper shorter visually) | rest | Mild? | Check zoom | **Unclear** / possible inferior |
| B04_odd_length | 一二三 | 四五 | Mild? | — | **Pass** |
| B05_short_two | 割 | 注 | — | — | **Pass** |
| B06_unequal_stretch | ~6 kana | ~5 kana | **Yes** | — | **Pass** (stretch OK) |
| B07_very_long | long / long | long / long | Likely | — | **Pass** readable |
| B08_punct_comma_mid | …、 | … | — | Comma on upper | **Pass** |
| B09_punct_open_bracket_risk | starts with 「… | … | — | Better than mid with 」 start | **Pass** |
| B10_punct_close_start_risk | …」 | … | — | 」 ends upper | **Pass** |
| B11_punct_paren | …乙 | ）丙… | — | **） starts 2nd** | **Fail** kinsoku |
| B12_punct_various | mixed | mixed | Uneven? | Looks uneven | **Unclear** |
| B13_mixed_latin_digits | AB漢字 | 12かな | — | Latin metrics | **Pass** readable |
| B14_historical_kana | ゐゑ… | … | — | — | **Pass** |
| B15_vs16 | (VS preserved in ODF) | | — | Glyph form TBD | **Pass** integrity; glyph **Unclear** |
| B16_bracket_uno_classic | collapsed | collapsed | n/a | Brackets broken | **Fail** paint |
| B17_bracket_uno_short | collapsed | collapsed | n/a | Brackets broken | **Fail** paint |
| B18_classic_vertical | 割り注は、 | 良いです | Yes (shorter) | — | **Pass** |
| B19_equal_vertical | 天地玄黄 | 、宇宙洪荒 | — | **、 starts 2nd** | **Fail** kinsoku |
| B20_punct_vertical | 曰「天地 | 」なり | Strong stretch | **」 starts 2nd** | **Fail** kinsoku |
| B21_bracket_vertical | 割注 / 試験 visible | | — | Delimiters unclear in thumb | **Unclear** (re-check brackets) |

## Integrity

- [x] Reopen ODT: combine styles on spans
- [x] Classic note string preserved
- [x] VS16 U+E0100 preserved in ODF
- [x] PDF via headless convert
- [ ] DOCX in Microsoft Word — **not tested**
- [ ] Multi-font re-run — **deferred**
