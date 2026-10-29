# Emphasis marks (圏点・傍点) — overview

Native Writer property: `CharEmphasis` (`com.sun.star.text.FontEmphasis`).

See also: [`02-NATIVE-CAPABILITY.md`](02-NATIVE-CAPABILITY.md).

## Product (0.3.24+)

| Control | Behaviour |
|---|---|
| **Apply emphasis** (main) | Applies the **document default** to the selection (never toggles off) |
| **Emphasis menu** (▾) | Passage override / Remove / Set default… |
| **Remove** (in menu) | Clears `CharEmphasis` only; text + ruby/warichū untouched |
| **Set default…** | Writes `marinaMoji.Typography.EmphasisDefault`; **does not** rewrite passages |

Requires an explicit selection (same policy as warichū/ruby apply).

## Exposed styles

| Id | UNO | Japanese | English |
|---|---|---|---|
| `BLACK_SESAME` **(default)** | `ACCENT_ABOVE` (4) | 黒ゴマ | Black sesame (ODF *accent*) |
| `BLACK_DOT` | `DISK_ABOVE` (3) | 黒丸 | Filled disc |
| `WHITE_CIRCLE` | `CIRCLE_ABOVE` (2) | 白丸 | Open circle |
| `DOT` | `DOT_ABOVE` (1) | 点 | Dot |

Not exposed (no native ODF/UNO): 白ゴマ, 二重丸, 蛇の目, triangles.

## Document preference

- Property: `marinaMoji.Typography.EmphasisDefault`
- Container: ODT `DocumentProperties` / UserDefinedProperties
- Written only when the user chooses **Set default…**
- Missing → built-in `BLACK_SESAME`
- Changing default never silently rewrites existing marks

## Architecture

- Semantic ids live in `emphasis.py` / `typography_prefs.py` (Word can map later).
- Toolbar order: warichū → emphasis (apply + menu) → ruby → copy.
- True LO Addons split-button is unavailable; adjacent apply + menu is the clean equivalent.
