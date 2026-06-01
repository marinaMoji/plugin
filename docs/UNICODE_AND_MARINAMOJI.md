# Unicode Kanbun ↔ marinaMoji shortcuts

IME definitions live in `mozc/src/data/preedit/kaeriten.tsv` (DirectInput).

Machine-readable mapping: [../mapping.json](../mapping.json).

## Mapping table

| marinaMoji input | Unicode | Unicode name (short) | Typical scholarly mark |
|------------------|---------|----------------------|-------------------------|
| `;r` | U+3191 ㆑ | Ideographic annotation reverse mark (*re*) | レ点 |
| `;1` | U+3192 ㆒ | … one mark | 一点 |
| `;2` | U+3193 ㆓ | … two mark | 二点 |
| `;3` | U+3194 ㆔ | … three mark | 三点 |
| `;4` | U+3195 ㆕ | … four mark | 四点 |
| `;u` | U+3196 ㆖ | … top mark | 上点 |
| `;m` | U+3197 ㆗ | … middle mark | 中点 |
| `;d` | U+3198 ㆘ | … bottom mark | 下点 |
| `;k` | U+3199 ㆙ | … first mark | 甲点 |
| `;o` | U+319A ㆚ | … second mark | 乙点 |
| `;h` | U+319B ㆛ | … third mark | 丙点 |
| `;t` | U+319C ㆜ | … fourth mark | 丁点 |
| `;te` | U+319D ㆝ | … heaven mark | 天点 |
| `;ti` | U+319E ㆞ | … earth mark | 地点 |
| `;ji` | U+319F ㆟ | … man mark | 人点 |
| `;.` | U+30FB ・ | (not Kanbun block) | 中黒 |
| `;,` | U+3001 、 | | 読点 |

Block **U+3190** ㆐ is “linked mark”; marinaMoji does not assign a `;` shortcut in current `kaeriten.tsv`.

## Formatter target glyphs (Word/LO v1)

For layout, convert Kanbun code points to **normal Japanese characters + formatting**:

| Unicode | Replace with | Formatting |
|---------|--------------|------------|
| ㆑ | レ (katakana) | Subscript (下付き) |
| ㆒ | 一 | Subscript |
| ㆓ | 二 | Subscript |
| ㆔–㆟ | 三, 四, 上, 中, 下, 甲, 乙, 丙, 丁, 天, 地, 人 | Subscript (confirm typography per your style sheet) |

Keep mapping in **one JSON file** (`mapping.json`) shared by the LO extension, exporters, and (later) Word.

## Compound clusters

Multiple marks after one kanji form **one** rendered annotation, e.g.:

```
說㆒㆑者  →  one frame at 說: 一 over レ  →  visible flow: 說者
```

Rules: [CONVENTIONS.md](CONVENTIONS.md). Stack order: `stack_order` in `mapping.json`.

## Verification

Same character in every app:

```bash
printf '%s\n' '㆑' | xxd   # expect e3 86 91
```

If paste hex differs, the problem is not the formatter.
