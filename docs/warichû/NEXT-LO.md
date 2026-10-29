# LibreOffice next steps

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
