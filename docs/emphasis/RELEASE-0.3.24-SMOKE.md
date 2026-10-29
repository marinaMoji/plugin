# Smoke checklist — 0.3.25 emphasis

Install `plugin/libreoffice/dist/MarinaMojiKaeriten.oxt` → **restart Writer**.

If icons look mixed with warichū: Extension Manager → Remove marinaMoji → restart → Add the new `.oxt` → restart. (Old toolbar customizations can keep stale button order.)

## Toolbar

Expected groups: **warichū (2)** | **emphasis apply + menu + remove (3)** | **ruby (2)** | copy

1. Emphasis sits **after warichū**, before ruby — three emphasis icons together.
2. Main button shows the **sesame / 圏点 icon** (not the title text).
3. Menu button opens a popup (or a small dialog fallback).
4. Remove emphasis is back on the toolbar.

## Apply / override / default

1. Select `マリナさん` → main Apply → **黒ゴマ** (accent) marks.
2. Select `愛している` → menu → **白丸** → open circles; document default still 黒ゴマ.
3. Main Apply on new text still uses 黒ゴマ.
4. Menu → **Set default…** → choose 黒丸 → OK. Existing marks on (1)(2) **unchanged**.
5. New selection → main Apply → 黒丸.
6. Menu → **Remove emphasis** → marks gone; characters unchanged.
7. Optional: adjacent to ruby and warichū; H and V page.

## ODT

Save / reopen: passage marks remain; after Set default, preference survives (UserDefinedProperties).
