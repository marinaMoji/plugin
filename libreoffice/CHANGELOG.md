# Changelog — marinaMoji (LibreOffice)

Version history for the Writer extension (`MarinaMojiKaeriten.oxt`).
Version numbers match `marinamoji_kaeriten/description.xml`.

## Unreleased

## 0.3.32 - 2026-10-29

* Typography inspector: list **each** Western / halfwidth-JP punctuation
  occurrence (distinguish `｡` from `.`); clearer inspect toolbar icon; taller report dialog.

## 0.3.31 - 2026-10-29

* **Japanese Typography Inspector (Stage E2):** read-only Inspect command.
  Reports paragraph/document Asian composition settings; conservative diagnostics
  (`PARA_FORBIDDEN_RULES_OFF`, `PUNCTUATION_MIXED_WIDTH`,
  `EXPLICIT_BREAK_BEFORE_NOTSTART`). EN/JA/FR. Toolbar `.v5` (`m18` inspect).
* Docs: [`docs/kinsoku/e2/`](../docs/kinsoku/e2/).

## 0.3.30 - 2026-10-29

* **Tate-chū-yoko (縦中横):** Apply / Remove via native `CharRotation` 90° + fit-to-line.
  Vertical-only apply; selection policy (2-grapheme auto, 3–4 confirm, refuse mixed/CJK /
  warichū overlap); caret detection for exact 2-digit/Latin runs only.
* **Toolbar order fix:** LibreOffice configmgr sorts Addon toolbar item names with
  `LengthContentsCompare` (shorter names first). Unequal-length ids such as
  `i01_render` / `i18_copy_plain` scrambled the button order. Items are now equal-length
  `m01`…`m18`; toolbar id bumped to `.v4`.
* Docs: [`docs/tatechuyoko/`](../docs/tatechuyoko/).

## 0.3.26 - 2026-10-29

* **Emphasis marks (圏点・傍点):** native `CharEmphasis` Apply / menu / Remove.
  Document default preference (`marinaMoji.Typography.EmphasisDefault`); 黒ゴマ default;
  menu offers 黒丸 / 白丸 / 点. Toolbar `.v2`.

## 0.3.22 - 2026-10-29

* Ruby + warichū coexistence: paragraph Text-to-text → Base line on ruby apply.

## 0.3.16 - 2026-10-29

* Warichū Apply / Remove validated (caret-aware remove; span `CharCombine`).
