# LibreOffice next steps

## Ordered typography roadmap

Knock off in this order (feasibility vs native UNO, 2026-10-29):

| # | Feature | Status |
|---|---|---|
| 1 | **Emphasis marks 圏点・傍点** | **0.3.24 coded — smoke pending** — [`../emphasis/`](../emphasis/) |
| 2 | Tate-chū-yoko 縦中横 | pending |
| 3 | Scholarly typography presets | pending |
| 4 | Kinsoku shori 禁則処理 (diagnostics) | pending |
| 5 | Document-wide validation | pending |
| 6 | Punctuation and spacing | pending |
| 7 | Jidori 字取り | pending |
| 8 | Furiwake 振り分け | pending |

## Phase 3 — ruby + warichū coexistence (**0.3.22** smoked)

- Native **group-ruby** Apply / Remove (`ruby.py`) — see [`20-PHASE3-RUBY.md`](20-PHASE3-RUBY.md).
- Manual coexistence smoke **passed** (user 2026-10-29): ruby + warichū + vertical; Text-to-text Base line; Fixed line spacing.
- Package: `plugin/libreoffice/dist/MarinaMojiKaeriten.oxt` — **ready to publish** when you choose.
- Still deferred: jukugo / mono auto-split / ruby metrics UI / stretch-mode UI (INDENT_BLOCK/BLOCK) / shared rules engine / Word.

## Parked upstream

- [tdf#174224](https://bugs.documentfoundation.org/show_bug.cgi?id=174224) delimiter paint — patch deferred.
- U2 kinsoku — re-verify before filing.
- Scholarly manual division — maintainer discussion only.

## Release

- **0.3.16** warichū validated.
- **0.3.22** = warichū + ruby coexistence (LEFT ruby adjust; paragraph Text-to-text Base line on apply; bare combine). Smoke OK — publish when ready.
- **0.3.24** = emphasis (黒ゴマ default, menu overrides, doc preference). Smoke pending.
