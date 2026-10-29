# Phase E2-A — Live UNO verification notes

IDL and Stage E1 source mapping confirmed the property names before coding.

| Property | Verified via | Production use |
|---|---|---|
| `ParaIsForbiddenRules` | ParagraphPropertiesAsian IDL + Help Asian Typography | Effective bool + PropertyState when available |
| `ParaIsHangingPunctuation` | same | same |
| `ParaIsCharacterDistance` | same | same |
| `CharacterCompressionType` | document.Settings IDL | 0/1/2 → labels |
| `IsKernAsianPunctuation` | document.Settings IDL | bool |
| `ForbiddenCharacters` | XForbiddenCharacters + LocaleData fallback | begin/end strings for `ja` |

**Effective vs direct:** inspector displays the boolean Writer returns on the paragraph cursor (effective). If `getPropertyValue` fails → **Unavailable** (never shown as Disabled). Mixed multi-paragraph selections → **Mixed**.

**Soft breaks:** Shift+Enter expected as `\n` (or related) inside `XTextRange.getString()` for a paragraph; paragraph boundaries are separate snapshots.

Manual confirmation on installed 0.3.31 remains part of smoke testing (`05-TEST-CORPUS.md`).
