# Smoke checklist — 0.3.23 emphasis (圏点)

Install `plugin/libreoffice/dist/MarinaMojiKaeriten.oxt` → restart Writer.

## Must pass

1. Select a few characters (e.g. `重要`) → **Apply emphasis** → dots appear above (right side if vertical page).
2. Undo works; re-apply.
3. Caret inside marked span → **Remove emphasis** → dots gone; base text unchanged.
4. Horizontal and vertical page both look correct.
5. Optional: emphasised span next to ruby and/or warichū — no paint collapse.

## Optional ODF peek

Unzip `.odt` → `content.xml` / styles: look for `style:text-emphasize` (not `none`) on a text style.
