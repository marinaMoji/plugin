# Smoke checklist — 0.3.27 tate-chū-yoko (toolbar order: use **0.3.28+**)

Install `plugin/libreoffice/dist/MarinaMojiKaeriten.oxt` → restart Writer.

**0.3.28** bumps the toolbar id to `.v3` (clean order after 0.3.27 scrambled `.v2` layouts).
If icons look mixed: Extension Manager → Remove marinaMoji → restart → Add the new `.oxt` → restart.

Toolbar order: kaeriten | warichū pair | **tate-chū-yoko pair** | emphasis trio | ruby pair | copy

## Must pass

1. Vertical page. Type e.g. `令和12年` → select `12` → **Apply tate-chū-yoko**.
2. Digits sit as a horizontal pair in the vertical line (Fit to line).
3. Caret inside → **Remove** → rotation cleared; text unchanged.
4. Select warichū note → Apply tate → refused.
5. Optional: horizontal page still applies 90°+fit (less useful; confirm no crash).
6. Optional: unzip ODT → look for `style:text-rotation-angle` near `90`.
