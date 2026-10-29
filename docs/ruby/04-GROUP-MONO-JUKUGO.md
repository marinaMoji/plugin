# D. Group / mono / jukugo analysis

## Test cases (align spike + UNO)

| Base | Reading | Intent | Writer representation | H note | V note |
|---|---|---|---|---|---|
| `本` | `ほん` | Mono | One-char group = mono | Solid / centred | Same |
| `本文` | `もと` | Short group | Group (`text:ruby` over 2 chars) | CENTER vs BLOCK differ clearly | LEFT looks “top-stuck” |
| `日本` | `にほん` | Longer group | Group; overhang both ends | Overhang into neighbours | Same |
| `国際` | `こくさい` | Long reading | Group; strong overhang | Spacing of neighbours may tighten | Same |
| `今日` | `きょう` | Jukugo-*like* reading | Still one group span — **not** true jukugo | Looks fine as group | Same |
| `明日` | `あした` | Irregular compound | Same — group only | — | — |

## What Writer can represent

1. **Group ruby** — select any contiguous base, one `RubyText`. Unbreakable as one ruby object in layout practice.  
2. **Mono-ruby** — only by applying ruby **once per character** with the correct sub-reading. No automatic segmentation.  
3. **Jukugo-ruby** — **not** a first-class Writer/ODF model in this path. True jukugo needs per-character readings plus compound overhang; Writer’s single-span group cannot express “reading A belongs to char 1, reading B to char 2” while still allowing jukugo-style line split.

## marinaMoji policy

- Apply creates **group ruby** over the selection (honest about what the host stores).  
- Does **not** silently split into mono or invent jukugo.  
- Scholars who need mono must select one character at a time (or use host UI repeatedly).  
- Jukugo remains future work / upstream territory — document, do not fake.

## Editing / persistence

| Concern | Observation |
|---|---|
| Base editable | Yes — characters stay in the text stream |
| Reading editable | Via re-apply or Asian Phonetic Guide |
| ODT | `text:ruby` / `text:ruby-base` / `text:ruby-text` |
| DOCX export | Not exhaustively tested this pass; treat as host-dependent |
| Save/reopen | `RubyAdjust` values round-trip (spike ODF) |
