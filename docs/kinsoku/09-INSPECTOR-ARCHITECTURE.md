# Inspector architecture sketch (Stage E1 — design only)

No production UI. No toolbar. Shared-engine sketch only.

## Separation of concerns

```text
┌─────────────────────────────────────────┐
│  Shared Japanese typography rules       │
│  (host-independent text + conventions)  │
└─────────────────┬───────────────────────┘
                  │ diagnostics
        ┌─────────┴─────────┐
        ▼                   ▼
 LibreOffice adapter    Word adapter (later)
 (UNO read-only)        (Office.js / OOXML)
```

- Shared engine must **not** import UNO types.
- LO adapter extracts text, ranges, paragraph Asian props, document settings; optionally experimental layout hints.
- Do **not** over-build before E2 validation.

## Diagnostic record (host-independent)

```text
TypographyDiagnostic
    rule_id          # stable string, e.g. KINSOKU_LINE_START
    category         # settings | punctuation | kinsoku_text | annotation | layout
    severity         # info | advisory | warning | confirmed
    message          # human, non-prescriptive for scholarly profiles
    document_range   # host-neutral start/end offsets or opaque handle
    evidence         # chars, convention, paragraph settings, optional geometry
    suggested_action # optional; never auto-apply in E2 default
    confidence       # confirmed | heuristic
    mechanism        # body_line_break | warichu_internal | …
    profile_tags     # which profiles enable this rule
```

## Rule id backlog (not all for E2)

| rule_id | Needs layout? | E2 candidate? |
|---|---|---|
| `PARA_FORBIDDEN_RULES_OFF` | No | **Yes** |
| `PARA_HANGING_OFF` | No | Yes (info) |
| `DOC_COMPRESSION` | No | Yes (info) |
| `PUNCTUATION_MIXED_WIDTH` | No | **Yes** |
| `EXPLICIT_BREAK_BEFORE_NOTSTART` | No (textual) | **Yes** |
| `KINSOKU_LINE_START` | **Yes** | Defer |
| `KINSOKU_LINE_END` | **Yes** | Defer |
| `WARICHU_INTERNAL_BREAK` | Soft heuristic | Optional advisory |
| `PUNCTUATION_SPACING` | Mostly yes | Defer |

## Severity policy

- Editorial / profile differences → **info** or **advisory**.  
- Disabled composition settings the user may not notice → **advisory**.  
- Confirmed host defect (rare; needs strong evidence) → **warning** / **confirmed**.  
- Never label diplomatic punctuation as **error**.

## Selection scope

First version: **current selection or current paragraph** only. No whole-document walk in E2.
