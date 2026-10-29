# Native emphasis-mark capability (LibreOffice Writer)

Source of truth: ODF `style:text-emphasize` + UNO `CharEmphasis` / `com.sun.star.text.FontEmphasis`.

## Host repertoire (faithful only)

| ODF tokens | UNO (`CharEmphasis`) | Semantic id | Japanese UI | English UI | Exposed |
|---|---|---|---|---|---|
| `accent above` | `ACCENT_ABOVE` = 4 | `BLACK_SESAME` | 黒ゴマ | Black sesame (accent) | **Yes — default** |
| `disc above` | `DISK_ABOVE` = 3 | `BLACK_DOT` | 黒丸 | Filled disc | **Yes** |
| `circle above` | `CIRCLE_ABOVE` = 2 | `WHITE_CIRCLE` | 白丸 | Open circle | **Yes** |
| `dot above` | `DOT_ABOVE` = 1 | `DOT` | 点 | Dot | **Yes** (distinct from disc) |
| `accent below` etc. | `*_BELOW` 11–14 | — | — | — | No (conventional JP uses above / right via ABOVE) |
| — | — | `WHITE_SESAME` | 白ゴマ | White sesame | **Not native** |
| — | — | double circle / 蛇の目 / triangles | — | — | **Not native** |

### Naming honesty

- ODF/UNO call the sesame-shaped mark **accent**, not “sesame”.
- marinaMoji labels `ACCENT_ABOVE` as **黒ゴマ** because that is the conventional Japanese name for this mark shape in CJK composition (Word’s OOXML `comma` / sesame maps to the same typographic role).
- We do **not** label `DOT` or `DISK` as sesame.
- **白ゴマ** has no ODF/UNO value — omitted from the UI (no Unicode glyph workaround).

## Writing direction

ABOVE variants paint above in horizontal text and to the right in vertical text (UNO docs). No separate vertical enum.

## Persistence

`CharEmphasis` is ordinary character formatting → survives ODT save/reopen without marinaMoji.
Document **default preference** is separate metadata (`marinaMoji.Typography.EmphasisDefault`).
