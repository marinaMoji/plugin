# Implementation Roadmap and Handoff to Local

## Phase 0 — Repository reconnaissance (mandatory)
**Deliverables:** architecture map, existing plugin capabilities, dependency/version inventory, integration points, risks. Identify the Word and LibreOffice code paths, UI design conventions, tests, release processes, and existing kaeriten behaviour. **No broad refactor.**

## Phase 1 — Warichū feasibility spikes (mandatory)
Follow [warichu-investigation-marinamoji.md](warichu-investigation-marinamoji.md). Build minimal throwaway prototypes in both hosts. Collect native document samples, XML, screenshots, versioned results, and failure cases. Distinguish API limitations from renderer limitations. Deliver a capability matrix and a recommendation before building product UI.

**LibreOffice progress (2026-10-29):** Writer **26.8.0.3** Gate 1 passed (span + bare `CharCombineIsOn`). Phase 2 MVP in extension **0.3.15**: toolbar **Apply warichū** / **Remove warichū** (`warichu.py`; refuses whole-paragraph selection; no UNO brackets).

**Stage A audit (same day):** JLREQ extract + LO source + capability matrix in docs `05`–`09`. Key finding: scholarly warichū is `SvxTwoLinesItem` → `SwDoubleLinePortion` with **hard-coded 50%** scale and **width-search** line split (`BuildMultiPortion`); shorter line stretched via `CalcNewBlock`. Manual division / alignment modes / size are **core** gaps — not plugin formatting. `SwCombinedPortion` (≤6) is a different feature.

**Stage B (same day):** Corpus executed on LO **26.8.0.3** (docs `10`–`15`). Bare combine is a credible JLREQ baseline; **UNO brackets paint collapse confirmed**; kinsoku-unsafe inner breaks demonstrated (B11 H; B19/B20 V). Next: plugin smoke/polish ([NEXT-LO.md](NEXT-LO.md)); upstream prep **U1** then **U2** (no Bugzilla/PR without approval); Word still deferred.

**Gate 1:** At least native insertion, inspection, edit/remove, save/reopen, and vertical/horizontal behaviour have evidence or explicitly documented blockers. If manual division/alignment cannot be demonstrated, omit those controls from MVP.

## Phase 2 — Minimum viable warichū editor
Integrate into existing marinaMoji plugin UI with a single discoverable typography entry point. Features: apply/remove native warichū, edit supported settings, delimiters, native style preset, helpful warnings, undo, and source fidelity. Reuse existing styles and localization patterns. Feature-gate unsupported operations per host/version.

**Acceptance:** A colleague can select text, insert native warichū, save/reopen, edit the annotation, and continue normal document editing without data loss. Document all unsupported alignment requirements visibly.

## Phase 3 — Shared core and ruby
Only after Phase 2 clarifies host constraints, extract reusable character classification, segmentation, rule metadata, and diagnostics. Add mono/group ruby editing, size/font/position controls supported by each host; investigate jukugo-ruby separately. Test with kaeriten and vertical text. Keep text and semantic readings recoverable.

## Phase 4 — Composition tools and inspector
Tate-chū-yoko, emphasis marks, jidori, punctuation/kinsoku diagnostics, styles, batch inspection. Prefer user-reviewed fixes. Distinguish actual rendered-line analysis from purely textual heuristics; label findings appropriately.

## Phase 5 — Advanced scholarly features and upstream work
Investigate furiwake, scholarly character alignment anchors, more demanding ruby, diplomatic transcription, metadata portability, and TEI/LaTeX export. If LibreOffice native warichū layout is insufficient, prepare a narrowly scoped upstream Writer/UNO proposal with source references, failing tests, and a minimal patch design. Do not promise corresponding Word engine modifications.

## Parallel quality work
- Automated unit tests for pure rules and Unicode preservation.
- Integration tests for document insertion and save/reopen.
- Golden documents/screenshots for fonts, horizontal/vertical, and DOCX/ODT/PDF output.
- Compatibility matrix: Word macOS/Windows versions and LibreOffice versions actually tested.
- Accessibility, keyboard navigation, undo/redo, copy/paste, tracked changes, localization.
- Privacy: manuscript text stays local unless user explicitly invokes a service.

## Decision records to create
- ADR-001: Native formatting vs visual workaround.
- ADR-002: Shared code vs shared schema across plugin languages.
- ADR-003: Metadata persistence and round-trip strategy.
- ADR-004: Scope and semantics of JLREQ conformance claims.
- ADR-005: Word/LibreOffice capability negotiation and feature gating.

## Instructions to local — first working session
1. Read all five documents, then inspect the repositories rather than guessing their structure.
2. Report findings as **confirmed**, **inferred**, or **unverified** with references.
3. Identify the smallest executable warichū prototype for each host; ask for test machines if required.
4. Do not implement speculative per-character alignment controls.
5. Add test fixtures and a capability report; stop at Gate 1 and propose the product implementation based on evidence.
6. Preserve existing marinaMoji functionality, style, and release process.

## Definition of done for the investigation
- Reproducible prototype(s), or precise blockers.
- XML/ODF samples and rendered screenshots with versions and fonts.
- Verified feature matrix with evidence.
- Source-level LibreOffice rendering findings **if accessible**, or a clearly bounded follow-up task.
- Written MVP scope, risks, and recommended next implementation PRs.
