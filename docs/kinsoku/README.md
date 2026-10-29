# Stage E1 — Japanese punctuation, kinsoku, scholarly composition

**Status:** investigation / planning (no production inspector yet).  
**Host focus:** LibreOffice Writer **26.8.0.3** (`bce0998afefdbc355585ca324285661a2170ba77`).  
**Restriction:** do not change released formatting behaviour; prototypes stay under `libreoffice/spikes/kinsoku/`.

## Goal

Understand Writer’s native Japanese composition (禁則・約物・ぶら下げ・詰め・行調整), map it to [JLREQ](https://www.w3.org/TR/jlreq/), and decide what a **read-only** marinaMoji inspector can reliably detect—without replacing Writer’s layout engine.

## Documents

| Doc | Contents |
|---|---|
| [`00-INVENTORY.md`](00-INVENTORY.md) | Prior marinaMoji work to reuse (warichū U2, Stage B corpus) |
| [`01-JLREQ-KINSOKU-REQUIREMENTS.md`](01-JLREQ-KINSOKU-REQUIREMENTS.md) | JLREQ / Unicode rules vs conventions (verified refs) |
| [`02-LIBREOFFICE-NATIVE-CAPABILITIES.md`](02-LIBREOFFICE-NATIVE-CAPABILITIES.md) | UI, UNO, ODF, scopes, Writer source paths |
| [`03-KINSOKU-TEST-CORPUS.md`](03-KINSOKU-TEST-CORPUS.md) | Planned / executed minimal ODTs |
| [`04-PUNCTUATION-AND-LINE-ADJUSTMENT.md`](04-PUNCTUATION-AND-LINE-ADJUSTMENT.md) | Spacing, compression, hanging, adjustment |
| [`05-VERTICAL-COMPOSITION.md`](05-VERTICAL-COMPOSITION.md) | Vertical punctuation / grid notes |
| [`06-SCHOLARLY-USE-CASES.md`](06-SCHOLARLY-USE-CASES.md) | Classical / kanbun / diplomatic profiles |
| [`07-ANNOTATION-INTERACTIONS.md`](07-ANNOTATION-INTERACTIONS.md) | Ruby, warichū, emphasis, tate |
| [`08-UNO-LAYOUT-INSPECTION.md`](08-UNO-LAYOUT-INSPECTION.md) | Rendered-line geometry feasibility |
| [`09-INSPECTOR-ARCHITECTURE.md`](09-INSPECTOR-ARCHITECTURE.md) | Diagnostic model sketch |
| [`10-IMPLEMENTATION-RECOMMENDATIONS.md`](10-IMPLEMENTATION-RECOMMENDATIONS.md) | Stage E2 proposal |
| [`99-DECISION-REPORT.md`](99-DECISION-REPORT.md) | Answers to the Stage E1 question list |

## Decision (one line)

**E2 (0.3.31):** read-only Inspect Japanese Typography shipped — see [`e2/`](e2/). **Defer** rendered-line kinsoku diagnostics.

## Spikes

`libreoffice/spikes/kinsoku/` — scripts + regenerable artifacts (gitignored binaries).

## Related prior work

- Warichū kinsoku-unsafe inner breaks: [`../warichû/upstream/18-KINSOKU-NOTES.md`](../warichû/upstream/18-KINSOKU-NOTES.md), Stage B B11/B19/B20  
- Roadmap item: [`../warichû/NEXT-LO.md`](../warichû/NEXT-LO.md) #4  
