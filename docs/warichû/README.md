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

**LO spike (throwaway):** [`libreoffice/spikes/warichu/`](../../libreoffice/spikes/warichu/).

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
