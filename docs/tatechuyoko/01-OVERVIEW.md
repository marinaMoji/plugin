# Tate-chū-yoko (縦中横) — overview

See also: [`02-NATIVE-AND-JLREQ.md`](02-NATIVE-AND-JLREQ.md), [`03-IMPLEMENTATION-REPORT.md`](03-IMPLEMENTATION-REPORT.md).

## Product (0.3.28+)

| Action | Behaviour |
|---|---|
| **Apply** | Validates selection or caret; then `CharRotation=900` + fit |
| **Remove** | Clears rotation + fit; caret-aware; any writing direction |

### Selection policy (marinaMoji)

| Class | Examples | Behaviour |
|---|---|---|
| Recommended | `12`, `AB`, `１２` | Apply in vertical writing |
| Extended | `123`, `2026`, `3.5` | Confirm (“Apply anyway?”) |
| Inappropriate | `令和`, `令和12年`, `12年` | Refuse — **no silent shrink** |
| Unsafe | warichū/ruby overlap, breaks | Refuse |

### Caret (no selection)

Only an **exact** 2-grapheme digit or Latin run at the caret (e.g. `12` in `令和12年`).
Never slices two digits out of `2026`.

### Writing direction

New apply: **vertical only**. Remove: always allowed.
