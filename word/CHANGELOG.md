# Changelog — marinaMoji (Word)

Version history for the Microsoft Word add-in (Kaeriten pane).

## Unreleased

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
