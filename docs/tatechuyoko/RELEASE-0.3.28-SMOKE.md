# Smoke — 0.3.28+ tate-chū-yoko validation

Install OXT (**0.3.30+** for toolbar order) → restart Writer → vertical page.

Toolbar must read left→right: kaeriten | warichū | tate-chū-yoko | emphasis | ruby | copy.
(0.3.30 fixes LO `LengthContentsCompare` scramble from unequal `iNN_…` node names.)

## Must pass

1. `令和12年` — select only `12` → Apply → horizontal pair (as before).
2. Select whole `令和12年` → Apply → **refused** with guidance (selection unchanged).
3. Caret inside `12` (no selection) → Apply → only `12` formatted.
4. Caret inside `2026` → Apply → **no** auto slice; asks for selection / refuses.
5. Select `123` → Apply → confirmation; Cancel leaves text alone; Yes applies.
6. Horizontal page → Apply → refused (“intended for vertical writing”).
7. Remove still works on an existing span (any direction).
