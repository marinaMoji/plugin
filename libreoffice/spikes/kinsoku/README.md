# Stage E1 spikes — kinsoku / punctuation

Isolated experiments. **Not** part of the released extension.

## Layout

| Path | Purpose |
|---|---|
| `scripts/proto_a_read_asian_para.py` | Read `ParaIs*` + ForbiddenCharacters |
| `scripts/proto_b_textual_punctuation.py` | Host-independent textual rules (runnable outside LO) |
| `scripts/proto_c_viewcursor_line_heads.py` | Experimental view-cursor line heads (not production) |
| `scripts/kinsoku_corpus_macro.py` | Generate narrow-page horizontal ODT corpus |
| `fixtures/ja_JP_forbidden_defaults.json` | Locale default lists from LO `ja_JP.xml` |
| `artifacts/` | Generated ODT/PDF/PNG (gitignored binaries) |

## Docs

See [`../../../docs/kinsoku/`](../../../docs/kinsoku/).

## Safety

Read-only inspection preferred. Corpus macro writes **new** ODTs only under `artifacts/` (or Desktop fallback). Never rewrite user Options from these scripts.
