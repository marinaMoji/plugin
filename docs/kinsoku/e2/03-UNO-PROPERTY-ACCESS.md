# Stage E2 — UNO property access

**Environment:** LibreOffice 26.8.0.3 (same as Stage E1).

## Paragraph (effective via text cursor)

| Property | Meaning | PropertyState |
|---|---|---|
| `ParaIsForbiddenRules` | Apply forbidden begin/end lists | `direct` / `default` / `ambiguous` recorded when available |
| `ParaIsHangingPunctuation` | Hanging punctuation | same |
| `ParaIsCharacterDistance` | Asian–Western autospace | same |

Returned booleans are **effective** values Writer applies (style + direct merge). State hints distinguish direct vs default when `getPropertyState` works; the UI still shows Enabled/Disabled/Unavailable/Mixed from the boolean, never inventing a default when the get fails.

## Document

| Property | Access |
|---|---|
| `CharacterCompressionType` | `document.Settings` or document property (0/1/2) |
| `IsKernAsianPunctuation` | same |
| `ForbiddenCharacters` | `XForbiddenCharacters.getForbiddenCharacters(Locale)`; fallback `i18n.LocaleData` |

Locale preference: paragraph `CharLocaleAsian`, then `ja-JP` document/locale defaults. Analysis falls back to bundled `ja_JP` begin/end strings only when host lists are empty.

## Persistence

Paragraph Asian toggles map to ODF `style:line-break`, `style:punctuation-wrap`, `style:text-autospace` (Stage E1). Live save/reopen confirmation remains a manual smoke step after install.
