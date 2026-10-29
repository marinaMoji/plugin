# Division heuristics (offline — not Writer output)

Compare these preferred breaks to **observed** Writer splits after viewing the corpus ODT/PDF.

| Case | Note | Naive mid | Mid flags | Preferred | Pref flags |
|---|---|---|---|---|---|
| B01_classic | `割り注は、良いです。` | `割り注は、` / `良いです。` | — | `割り注は、` / `良いです。` | — |
| B02_equal_qianziwen | `天地玄黄、宇宙洪荒。` | `天地玄黄、` / `宇宙洪荒。` | — | `天地玄黄、` / `宇宙洪荒。` | — |
| B03_long_classical | `此書不知何人所撰、疑為後世偽作。` | `此書不知何人所撰` / `、疑為後世偽作。` | lower_starts_kinsoku | `此書不知何人所撰、` / `疑為後世偽作。` | — |
| B04_odd_length | `一二三四五` | `一二` / `三四五` | lower_longer | `一二三` / `四五` | — |
| B05_short_two | `割注` | `割` / `注` | — | `割` / `注` | — |
| B06_unequal_stretch | `あいうえおかきくけこさ` | `あいうえお` / `かきくけこさ` | lower_longer | `あいうえおか` / `きくけこさ` | — |
| B07_very_long | `これは割注の試験としてかなり長い文字列を用意した例である` | `これは割注の試験としてかなり` / `長い文字列を用意した例である` | — | `これは割注の試験としてかなり` / `長い文字列を用意した例である` | — |
| B08_punct_comma_mid | `甲乙丙、丁戊己。` | `甲乙丙、` / `丁戊己。` | — | `甲乙丙、` / `丁戊己。` | — |
| B09_punct_open_bracket_risk | `曰「天地」なり。` | `曰「天地` / `」なり。` | lower_starts_kinsoku | `曰「天地」` / `なり。` | — |
| B10_punct_close_start_risk | `天地」宇宙。` | `天地」` / `宇宙。` | — | `天地」` / `宇宙。` | — |
| B11_punct_paren | `（甲乙）丙丁。` | `（甲乙` / `）丙丁。` | lower_starts_kinsoku,lower_longer | `（甲乙）` / `丙丁。` | — |
| B12_punct_various | `『書』・甲―乙…。` | `『書』・` / `甲―乙…。` | lower_longer | `『書』・甲` / `―乙…。` | — |
| B13_mixed_latin_digits | `AB漢字12かな` | `AB漢字` / `12かな` | — | `AB漢字` / `12かな` | — |
| B14_historical_kana | `ゐゑをゝゞ` | `ゐゑ` / `をゝゞ` | lower_longer | `ゐゑを` / `ゝゞ` | — |
| B15_vs16 | `葛󠄀飾区試験` | `葛󠄀飾` / `区試験` | — | `葛󠄀飾` / `区試験` | — |
| B16_bracket_uno_classic | `割り注は、良いです。` | `割り注は、` / `良いです。` | — | `割り注は、` / `良いです。` | — |
| B17_bracket_uno_short | `割注試験` | `割注` / `試験` | — | `割注` / `試験` | — |
| B18_classic_vertical | `割り注は、良いです。` | `割り注は、` / `良いです。` | — | `割り注は、` / `良いです。` | — |
| B19_equal_vertical | `天地玄黄、宇宙洪荒。` | `天地玄黄、` / `宇宙洪荒。` | — | `天地玄黄、` / `宇宙洪荒。` | — |
| B20_punct_vertical | `曰「天地」なり。` | `曰「天地` / `」なり。` | lower_starts_kinsoku | `曰「天地」` / `なり。` | — |
| B21_bracket_vertical | `割注試験` | `割注` / `試験` | — | `割注` / `試験` | — |
