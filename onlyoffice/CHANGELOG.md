# Changelog — marinaMoji (ONLYOFFICE)

Version history for the ONLYOFFICE Document Editor plugin. Marketplace updates require a new `config.json` `version` and an entry here.

## Unreleased

* Horizontal text: marks sit on the characters' bottom line instead of hanging below them. The picture is lowered by `(bottom line + ink inset) × font size` (`bottom_line_em`, `font_bottom_line_em`, `ink_inset_em` in `mapping.json`); the per-font bottom line is read from the paragraph's font (Songti SC differs). The old fixed `position_hps_per_pt` remains as the fallback. Checked against ONLYOFFICE's converter at 24–48 pt (within 0.012 em) and in ONLYOFFICE Desktop.
* The render fingerprint now includes the paragraph's font, so existing marks redraw when the font changes.
* Known: ONLYOFFICE enforces a minimum picture size of about 10 pt, so marks look larger than the mapping asks for below about 24 pt body text. Writer has no vertical page flow, so there is no vertical rule.
* Release note: bump `config.json` `version` when publishing this to the Marketplace.

## 0.1.14 - 2026-10-16

* Marketplace review: user `README.md`, `translations/langs.json`, remove `group`, `minVersion` 9.3.0.
* Dark theme via `onThemeChanged` (CSS variables + light/dark sidebar logo).
* Clipboard: fall back to hidden textarea + `execCommand("copy")` (no `PasteText`).
* Render: replace mark characters in place when possible so paragraph formatting is kept.
* Licensing headers + AGPL dual-offer note; drop unused store screenshot duplicates.
* Clarify authorship (official marinaMoji plugin) and exportCore origin (plugin repo, not IME BSD tree).

## 0.1.13 - 2026-10-16

* Add approved Desktop screenshot for Plugin Marketplace listing (`screen_1.png`).
* Point `store.screenshots` at the real capture; stop regenerating mock install/uninstall PNGs on build.

## 0.1.12 - 2026-10-16

* Marketplace preparation: `offered` field, store listing descriptions, sidebar slogan.
* Keep GUID and display name unchanged for future Plugin Manager updates.

## 0.1.11

* Inline-image Render / Unrender / Plain text workflow.
* Shared `mapping.json` sync on build; multi-scale light/dark and store icons.
