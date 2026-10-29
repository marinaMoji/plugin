# LibreOffice next steps

## Ordered typography roadmap

| # | Feature | Status |
|---|---|---|
| 1 | Emphasis marks 圏点・傍点 | **0.3.26** — [`../emphasis/`](../emphasis/) |
| 2 | **Tate-chū-yoko 縦中横** | **0.3.30** (toolbar.v4) — smoke pending — [`../tatechuyoko/`](../tatechuyoko/) |
| 3 | Scholarly typography presets | pending |
| 4 | Kinsoku shori 禁則処理 (diagnostics) | **0.3.31 inspector (E2)** — [`../kinsoku/e2/`](../kinsoku/e2/) |
| 5 | Document-wide validation | pending |
| 6 | Punctuation and spacing | pending |
| 7 | Jidori 字取り | **0.3.33** — Apply/Remove; V compress refused — [`../jidori/`](../jidori/) |
| 8 | Furiwake 振り分け | pending (distinct from jidori) |

## Phase 3 — ruby + warichū coexistence (**0.3.22** smoked)

- Native **group-ruby** Apply / Remove (`ruby.py`).
- Still deferred: jukugo / mono auto-split / ruby metrics UI / stretch-mode UI / Word.

## Parked upstream

- [tdf#174224](https://bugs.documentfoundation.org/show_bug.cgi?id=174224) delimiter paint — patch deferred.
- U2 kinsoku — re-verify before filing.
- Scholarly manual division — maintainer discussion only.

## Release

- **0.3.16** warichū validated.
- **0.3.22** ruby + warichū coexistence smoked.
- **0.3.26** emphasis marks (toolbar.v2).
- **0.3.27** tate-chū-yoko (90° + fit) MVP.
- **0.3.28** tate-chū-yoko selection policy + caret detection.
- **0.3.30** toolbar.v4 — equal-length `m01`…`m18` item names (fixes LO
  `LengthContentsCompare` scramble). Smoke pending. See [`../libreoffice/CHANGELOG.md`](../../libreoffice/CHANGELOG.md).
