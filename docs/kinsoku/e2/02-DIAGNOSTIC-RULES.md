# Stage E2 — Diagnostic rules

| rule_id | Severity | Trigger | Exclusions |
|---|---|---|---|
| `PARA_FORBIDDEN_RULES_OFF` | Information | Effective `ParaIsForbiddenRules` is false | Non-Japanese context; property unavailable |
| `PUNCTUATION_MIXED_WIDTH` | Advisory | **Each** Western (`.` `,` …) or halfwidth-JP (`｡` `､`) occurrence in JP-dominant text; labels distinguish variants | URLs for Western marks; decimals `1.2`; Latin-heavy local windows; low CJK ratio; cap 80 |
| `EXPLICIT_BREAK_BEFORE_NOTSTART` | Advisory | Soft line break (`\n` / `\v` / U+2028) followed by not-start char from locale list | Paragraph boundaries; unknown forbidden list; non-JP context |

## Deferred

- `KINSOKU_LINE_START` / `KINSOKU_LINE_END` (automatic wrap)
- Warichū internal-break warnings
- Rendered hanging / aki measurements
- Profile-dependent severity

## Explicit breaks

Soft breaks are taken from characters inside a **single paragraph** string (`getString()`). New paragraphs are separate snapshots and are **not** treated as soft breaks.
