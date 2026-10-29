# marinaMoji Japanese Typography — Planning Index

**Status:** Planning / investigation. **Audience:** local development agent and maintainers. **Do not interpret feasibility estimates as verified implementation results.**

## Objective
Extend marinaMoji's existing Microsoft Word and LibreOffice integrations with a coherent scholarly Japanese typography toolkit informed by W3C *Requirements for Japanese Text Layout* (JLREQ). The immediate user problem is unreliable or insufficiently controllable **warichū (割注) character alignment** in Word. Preserve editable, searchable, semantically meaningful text and ordinary document behaviour.

## Documents
0. [00-LO-PHASE0.md](00-LO-PHASE0.md) — LibreOffice repository reconnaissance (completed for LO first).
1. [01-JLREQ-FEATURES.md](01-JLREQ-FEATURES.md) — requirements inventory and priorities.
2. [02-ARCHITECTURE.md](02-ARCHITECTURE.md) — proposed shared engine, adapters, persistence, and host constraints.
3. [warichu-investigation-marinamoji.md](warichu-investigation-marinamoji.md) — concrete experiments and evidence required before implementation (doc “03”).
4. [04-IMPLEMENTATION-ROADMAP.md](04-IMPLEMENTATION-ROADMAP.md) — phases, milestones, deliverables, and acceptance gates.

### Stage A — JLREQ / LO rendering audit (2026-10-29)
5. [05-JLREQ-WARICHU-REFERENCE.md](05-JLREQ-WARICHU-REFERENCE.md) — JLREQ warichū requirements vs LO/plugin influence.
6. [06-LO-RENDERING-ANALYSIS.md](06-LO-RENDERING-ANALYSIS.md) — baseline example, environment, open measurements.
7. [07-NATIVE-CAPABILITY-MATRIX.md](07-NATIVE-CAPABILITY-MATRIX.md) — N/L/U/W/C/X for each desired feature.
8. [08-LO-SOURCE-NOTES.md](08-LO-SOURCE-NOTES.md) — `SwDoubleLinePortion` vs `SwCombinedPortion`; `BuildMultiPortion`.
9. [09-PRIORITIZED-CORRECTIONS.md](09-PRIORITIZED-CORRECTIONS.md) — plugin vs upstream ranking (no big impl yet).

### Stage B — Empirical validation / upstream feasibility (2026-10-29)
10. [10-TEST-CORPUS-AND-METHODOLOGY.md](10-TEST-CORPUS-AND-METHODOLOGY.md) — corpus, fonts, LO version, procedures.
11. [11-JLREQ-CONFORMANCE.md](11-JLREQ-CONFORMANCE.md) — rule-by-rule assessment with evidence.
12. [12-RENDERER-ANALYSIS-STAGE-B.md](12-RENDERER-ANALYSIS-STAGE-B.md) — division, `CalcNewBlock`, vertical.
13. [13-BRACKET-RENDERING-INVESTIGATION.md](13-BRACKET-RENDERING-INVESTIGATION.md) — confirmed horizontal delimiter collapse.
14. [14-UPSTREAM-FEASIBILITY.md](14-UPSTREAM-FEASIBILITY.md) — U1–U5, manual division architecture.
15. [15-STAGE-B-DECISION.md](15-STAGE-B-DECISION.md) — ten decision questions.
16. [NEXT-LO.md](NEXT-LO.md) — plugin vs upstream next steps.

### Stage C — Implementation / upstream prep (2026-10-29)
17. [16-LO-BUILD-ENVIRONMENT.md](16-LO-BUILD-ENVIRONMENT.md) — no local LO source build; cost estimate.
18. [upstream/](upstream/) — U1/U2 notes, scholarly proposal, draft bug reports (do not file yet).

### Release / upstream contribution prep
19. [RELEASE-0.3.16-CHECKLIST.md](RELEASE-0.3.16-CHECKLIST.md) — install + manual test (do not publish until signed off).
20. [upstream/U1-BUGZILLA-REVIEW.md](upstream/U1-BUGZILLA-REVIEW.md) — final U1 report for review before filing.
21. [upstream/lo-build-vm/](upstream/lo-build-vm/) — Ubuntu VM build scripts (no provision until approved).
22. [upstream/SCHOLARLY-MAINTAINER-SUMMARY.md](upstream/SCHOLARLY-MAINTAINER-SUMMARY.md) — short design summary (do not post yet).

**LO spike (throwaway):** [`libreoffice/spikes/warichu/`](../../libreoffice/spikes/warichu/) · Stage B: [`artifacts/stage_b/`](../../libreoffice/spikes/warichu/artifacts/stage_b/).

## Non-negotiable principles
- **Inspect the existing marinaMoji repositories and plugins first.** Reuse architecture, conventions, UI, release/test pipelines; do not create parallel plugins or assume directory names.
- **Native and editable first.** Avoid raster images, arbitrary inserted whitespace, or layout tables as primary warichū solutions.
- **No false claims of JLREQ conformance.** Distinguish standards-derived rules from scholarly extensions, host defaults, and proposed heuristics.
- **Never silently alter historical source text.** Normalize only with explicit user approval; retain original code points and annotation boundaries.
- **Shared logic, separate host adapters.** Word Office.js/OOXML and LibreOffice UNO/ODF have different capabilities and constraints.
- **Evidence before architecture lock-in.** The ability to insert two-line text does not prove manual line-break or per-glyph alignment control.
- **Accessible, restrained interface.** Fit marinaMoji's established editorial design and avoid a proliferation of toolbar icons.

## Immediate assignment to local
1. Map existing Word and LibreOffice plugin architectures, languages, test setup, and build constraints.
2. Read the references and inspect actual source/API definitions; record precise links, version numbers, and limitations.
3. Implement **throwaway experiments** for native warichū insertion, inspection, editability, persistence, and rendering (see document 03).
4. Produce a capability matrix with **Verified / Partially verified / Unsupported / Unknown** and reproducible evidence.
5. Propose a smallest viable warichū editor **only after** the experiments. Do not begin full JLREQ engine implementation before the feasibility gate.

## Reference starting points
- W3C JLREQ: https://www.w3.org/TR/jlreq/
- W3C Simple Ruby: https://www.w3.org/TR/simple-ruby/
- W3C Japanese typography resources: https://www.w3.org/TR/jpan-lreq/
- OOXML `w:eastAsianLayout`: https://c-rex.net/samples/ooxml/e1/Part4/OOXML_P4_DOCX_eastAsianLayout_topic_ID0EWHJO.html
- Microsoft Word Office.js Range API: https://learn.microsoft.com/en-us/javascript/api/word/word.range
- Microsoft OOXML add-in guidance: https://learn.microsoft.com/en-us/office/dev/add-ins/word/create-better-add-ins-for-word-with-office-open-xml
- LibreOffice UNO API: https://api.libreoffice.org/docs/idl/ref/
- ODF specifications: https://docs.oasis-open.org/office/
- LibreOffice core source: https://github.com/LibreOffice/core

**Research caution:** Earlier discussion established likely format/API entry points but did **not** constitute live compatibility tests or a traced source-level audit of LibreOffice's warichū renderer. Confirm all assumptions against current primary documentation and executable tests.
