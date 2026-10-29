# Stage J1 — Test corpus

Record for each row: font (Mincho + Gothic), size, writing mode, grid on/off, applied UNO values, visual pass/fail.

| Text | n | Target N | Intent | MVP expect |
|---|---:|---:|---|---|
| `日本` | 2 | 3 | Expand | Spacing; 1 em in the single gap |
| `日本` | 2 | 4 | Expand | 2 em in the gap |
| `東京大学` | 4 | 6 | Expand | ⅔ em per gap |
| `令和` | 2 | 3 | Conventional short | Spacing |
| `一二三` | 3 | 5 | Expand | 1 em/gap (matches prior H smoke) |
| `日本語` | 3 | 3 | Baseline noop | No visual change |
| `日本語` | 3 | 2 | Compress | Scale ≈ 67% |
| `ABC` | 3 | 4 | Latin | **Refuse** (proportional; not 1 em) |
| `12` | 2 | 3 | Numeric | **Refuse** or treat as Western block |
| `漢𠮷` | 2 | 3 | SIP | Count graphemes; Spacing if font OK |

## Visual acceptance (H already smoked)

- Glyphs legible; proportions preserved on expand.  
- Approximate N-cell advance.  
- No unexpected trailing gap after last character.  
- No spacer characters inserted.
