# Changelog — marinaMoji (Word)

Version history for the Microsoft Word add-in (Kaeriten pane).

## Unreleased

## 0.1.7 - 2026-10-29

* **Task-pane redesign:** single compact panel (no tabs). Inputs sit beside
  Apply/Remove (emphasis mark, ruby reading, jidori cells, compound checkbox).
  marinaMoji brand tokens, ⓘ help, scope line, status strip. Dev spike removed
  from the UI (underlying spike code still in the package for now).

## 0.1.6 - 2026-10-29

* **Japanese typography toolkit (Word):** task-pane Apply/Remove for warichū
  (`w:eastAsianLayout` combine), tate-chū-yoko (`vert`), emphasis (`w:em`),
  group ruby (`w:ruby`), and jidori / Fit Text (`w:fitText`). Selection policies
  follow the LibreOffice extension (whole-paragraph warichū refuse; tate length
  gates; ruby/warichū nesting refuse).
* Unit tests: `tests/test_typography.mjs`.

## 0.1.5 - 2026-10-29

* **Emphasis marks (圏点・傍点):** Apply / Remove on the selection via OOXML `w:em`.
  Styles: black sesame (`comma`, default), open circle, dot. LibreOffice’s filled
  disc has no Word twin, so it is not listed. Optional “remember as document default”
  uses Word document settings (`marinaMoji.Typography.EmphasisDefault`).
* Task pane section **Emphasis (圏点)** under Format / before Copy.

## 0.1.4 - 2026-10-29

* Composed drawings are sized to 1.0 × the font size (was 0.94, which looked small
  next to Mincho text) and lowered 0.19 em so they sit on the baseline. Same rule as
  the LibreOffice and ONLYOFFICE plugins and the composer's direct insert.
* **Render** now also resizes the drawings the composer inserted (tagged
  `MARINAMOJI:ids=…`), so a change of font or size is followed; it covers the body,
  headers and footers, and footnotes and endnotes.
* The pane has a **paste box** for when Word refuses clipboard access (it does, in
  its add-in webview): paste the composer's drawing there to insert it.
* macOS: Insert in the marinaMoji composer (v0.0.19+) can put the drawing straight into
  Word at the cursor through AppleScript, tagged so Render can resize it. Allow the
  composer to control Word the first time macOS asks. Awaiting a full test (#11).
* Install on Mac: macOS blocks Terminal from writing into Word's `wef` folder, so the
  install scripts and the Mac installer now stage the manifest on the Desktop and open
  Finder for a drag when the copy is refused; the instructions in the README, the release
  `INSTALL.txt` and the docs say so, and warn that `manifest.xml` is the dev manifest
  (`127.0.0.1:3000`) that shows "Erreur relative au complément".
* Windows: untested (#12).

### Insert composed character (SVG from the marinaMoji composer)

Desktop Word can insert a vector drawing for IDS structures that have no
Unicode code point. Flow: open the **character composer** from the marinaMoji
toolbar → build an unencoded layout → **Insert** (SVG on the clipboard) →
Kaeriten pane **Insert composed character**. Uses `Office.CoercionType.XmlSvg`
(ImageCoercion 1.2; Mac/Windows desktop, not Word on the web). Sized to the
selection font; alt text `MARINAMOJI:ids=…`. A hard-coded `⿰言某` control
remains under **Dev spike** for API smoke tests.

XmlSvg insert verified on Word for Mac; composer-side SVG needs a rebuilt
Character Composer app. LibreOffice / ONLYOFFICE paths not started.
