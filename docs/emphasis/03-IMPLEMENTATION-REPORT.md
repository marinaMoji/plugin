# Emphasis marks — implementation report (0.3.24)

## 1. Which native marks are supported?

ODF/UNO: `accent`, `dot`, `circle`, `disc` × above|below. No sesame-white, double-circle, bullseye, or triangles.

## 2. Exposed in the UI?

`BLACK_SESAME` (accent), `BLACK_DOT` (disc), `WHITE_CIRCLE` (circle), `DOT` (dot). ABOVE only.

## 3. Default?

`BLACK_SESAME` → `ACCENT_ABOVE`. Labeled 黒ゴマ; ODF name remains *accent*.

## 4. Where is the document preference stored?

`DocumentProperties.UserDefinedProperties` key `marinaMoji.Typography.EmphasisDefault` via `typography_prefs.py`.

## 5. Survives ODT save/reopen?

Passage `CharEmphasis`: yes (native). Preference: yes (user-defined doc property), written only on **Set default…**.

## 6. Different passages, different marks?

Yes — menu applies a specific style without changing the document default.

## 7. Changing the default preserve existing marks?

Yes — preference write only; no document scan/rewrite.

## 8. Removal preserve unrelated formatting?

Yes — sets `CharEmphasis=NONE` only.

## 9. Horizontal / vertical?

Uses ABOVE variants (above H / right V per UNO). Manual smoke required.

## 10. Unresolved limitations?

- No true Addons split-button → apply + menu pair.
- No 白ゴマ / decorative shapes without host support.
- Dynamic toolbar tooltip for current default not wired (menu shows “Apply default — …”).
- Visual/PDF proof of accent≒sesame shape is a manual smoke item.
- Preference undo may not enter Writer’s undo stack (metadata API).
