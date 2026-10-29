# Proposed Architecture and Data Model

## First action: repository reconnaissance
Local must locate the existing marinaMoji Word and LibreOffice implementations and document their languages, UI framework, manifests, build/release processes, supported versions, existing kaeriten code, and test harnesses. The architecture below is a **proposal**, not an instruction to replace existing patterns.

## Logical components
```text
existing marinaMoji plugins
  ├─ shared Japanese typography core (pure, testable logic)
  │   ├─ JLREQ character classes / line-break advisory logic
  │   ├─ warichū text segmentation and diagnostics
  │   ├─ ruby semantic model
  │   ├─ punctuation and spacing checks
  │   ├─ profile definitions
  │   └─ validation / capability negotiation
  ├─ Word adapter: Office.js selections + OOXML serialization
  └─ LibreOffice adapter: UNO ranges + ODF/formatting properties
```

**Critical boundary:** the core computes intent and diagnostics; the **host renderer** decides final glyph positions. Never confuse a mathematically correct division proposal with actual host rendering. If existing plugins use different languages, evaluate sharing data schemas and conformance fixtures rather than introducing a disruptive cross-language runtime.

## Draft canonical model (subject to change)
```json
{
  "schemaVersion": 1,
  "kind": "warichu",
  "sourceText": "ここに割注を入れる",
  "writingMode": "inherit",
  "division": { "mode": "automatic", "offset": null },
  "presentation": {
    "brackets": "round",
    "alignment": "host-native",
    "fontScale": null
  },
  "profile": "modern-japanese"
}
```
`offset` should be specified in a documented index unit (prefer Unicode grapheme-cluster boundaries; verify treatment of combining sequences and variation selectors). **Never store only visual line strings if it destroys the original text.** Schema must be extensible to explicit scholarly alignment anchors, but do not expose unsupported features.

## Persistence decision record required
Evaluate, per host:
1. Native formatting only (simplest, may not preserve plugin-specific intentions).
2. Host-native metadata or custom XML (may be stripped by conversions or editing).
3. Sidecar metadata (fragile if detached from document).

Select after save/reopen, copy/paste, undo/redo, export, and cross-application round-trip tests. Define failure modes and graceful degradation. Never silently replace text with an image or flattened object.

## Word adapter investigation
- Confirm `Range.getOoxml()` and `Range.insertOoxml()` support on targeted Word desktop versions and supported API requirement sets.
- Inspect `w:eastAsianLayout` with `w:combine` and `w:combineBrackets` in actual DOCX samples; test interaction with runs, character properties, and paragraph direction.
- Determine whether Office.js can reliably identify/reopen an existing combined-text range, not merely insert one.
- Beware that OOXML insertion can replace content and affect surrounding runs, styles, bookmarks, revisions, and selection. Test undo and tracked changes.
- Avoid assuming Word Windows, macOS, and web share identical rendering.

## LibreOffice adapter investigation
- Inspect UNO `CharCombineIsOn`, `CharCombinePrefix`, `CharCombineSuffix` and the precise range/property interfaces.
- Inspect ODF `style:text-combine="lines"` and related formatting semantics in current ODF specification.
- Test actual Writer save/reopen and DOCX export; distinguish format capability from renderer implementation.
- If native controls are insufficient, trace LibreOffice Writer layout source in `sw` and document smallest feasible upstream change; do not fork prematurely.

## API sketch (not committed)
```text
inspectSelection() -> SelectionInfo
inspectWarichu(range) -> WarichuModel | Unsupported | Unknown
createWarichu(range, intent) -> ApplyResult
updateWarichu(range, intent) -> ApplyResult
removeWarichu(range) -> ApplyResult
getCapabilities(hostVersion) -> CapabilityReport
validateDocument(scope, profile) -> Diagnostic[]
```
Every operation should report what was actually applied versus requested, with warnings and reversible changes. Unsupported controls must not be silently ignored.

## Quality and safety
- Source text fidelity, including Unicode variation selectors, combining marks, historical forms, and punctuation.
- Editability and copy/paste/search/accessibility before visual perfection.
- No remote service needed for core typesetting; preserve privacy of unpublished manuscripts.
- Test mixed fonts, vertical writing, nested formatting, tracked changes, and ordinary Word/Writer editing.
- Use consistent semantic terminology across UI, code, and docs; keep implementation notes linked to reproducible fixtures.
