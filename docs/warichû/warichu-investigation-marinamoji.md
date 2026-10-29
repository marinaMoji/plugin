# Focused Warichū Investigation — Experimental Protocol

**Status:** NOT YET EXECUTED. Earlier research identified likely mechanisms but did not run live host tests or trace Writer's precise renderer. Do not present hypotheses below as verified outcomes.

## Questions to resolve
1. Can existing marinaMoji plugins create a *native, editable* warichū annotation in each host?
2. Can they recognize, inspect, edit, and remove one reliably?
3. How does each renderer divide and align lines when lengths differ?
4. Can manual division be forced *without modifying the text*?
5. Do character spacing, font choice, delimiters, and writing mode affect internal alignment?
6. What survives DOCX/ODT save, reload, cross-format conversion, and PDF export?
7. Which limitations are in public APIs, file formats, or layout engines?

## Known starting points — verify against primary sources
### Word
- Candidate OOXML: `w:eastAsianLayout` with `w:combine="on"` and optional `w:combineBrackets`.
- OOXML combination attributes do **not obviously** provide explicit manual division or arbitrary per-character alignment controls.
- Candidate Office.js entry points: `Range.getOoxml()` / `Range.insertOoxml()`; validate actual version support and edit/retrieval workflows.
- A successful OOXML insertion does **not** prove editable round-trip or JLREQ alignment.

### LibreOffice
- Candidate UNO properties: `CharCombineIsOn`, `CharCombinePrefix`, `CharCombineSuffix`.
- Candidate ODF property: `style:text-combine="lines"` (distinguish `letters`).
- These interfaces do **not obviously** expose explicit upper/lower glyph positioning.
- Investigate Writer source for layout calculation and import/export mapping; do not assume the relevant functions without a source trace.

## Minimum test fixtures
Create a **versioned test corpus** with exact Unicode source strings, expected source extraction, font names, writing mode, and screenshots. Include:
- Short even-length CJK annotation; odd-length annotation; strongly unequal potential splits.
- Japanese comma/period and opening/closing brackets near proposed split.
- Annotation beginning/ending with punctuation.
- Mixed kanji/kana, Latin letters, digits, iteration marks, variation selectors.
- Horizontal and vertical paragraphs.
- Different CJK fonts, with/without explicit bracket styles.
- Adjacent ruby and existing marinaMoji kaeriten.
- Warichū near line boundaries, across reflow, in tables, and under tracked changes where supported.
- Multiple adjacent warichū spans and formatting run boundaries.

## Experiments and required artifacts
| ID | Experiment | Evidence required | Pass condition |
|---|---|---|---|
| T01 | Insert native warichū | Reproducible code, screenshot, DOCX/ODT, extracted XML | Native two-line formatting, text selectable/editable |
| T02 | Inspect existing warichū | API response, XML, round-trip log | Reconstruct selected text and detectable settings |
| T03 | Edit/remove | Before/after file and screenshot | Source preserved, undo works, no surrounding corruption |
| T04 | Unequal line lengths | Multiple strings, screenshots, host/version/font | Actual alignment algorithm documented empirically |
| T05 | Manual break attempts | Variants: runs/ranges/possible controls | Either demonstrated stable manual break or explicitly unsupported |
| T06 | Spacing attempts | Native spacing properties, screenshots, XML | Determine whether spacing affects internal lines |
| T07 | Vertical composition | Native files, screenshots, PDF | Stable placement, orientation and text reflow |
| T08 | Save/reopen and edit | Files before/after, XML diff | No text loss; formatting persistence characterized |
| T09 | DOCX↔ODT | Cross-host files, screenshots, XML | Record precise fidelity losses; no invented parity |
| T10 | Copy/paste, search, accessibility | Reproduction steps | Identify whether text remains usable |
| T11 | Cross-platform Word | macOS and Windows, versions recorded | Document renderer and API differences |
| T12 | LibreOffice source trace | Source paths, commits, relevant functions | Locate actual layout/import/export code and possible patch point |

## Controls
- Record exact application versions, OS, locale, UI language, document mode, CJK font versions, and plugin commit.
- Use same text, font size, page geometry, writing mode across comparisons where possible.
- Do not infer a font-independent layout rule from one screenshot.
- Keep test files and screenshots under a predictable test-artifact directory in the existing repo (after reconnaissance).
- Mark each result **Verified**, **Partially verified**, **Unsupported**, or **Unknown**, with evidence links.

## Specific technical hypotheses to falsify
- H1: Word's OOXML combination has no stable, exposed manual two-line division control.
- H2: LibreOffice's UNO combination properties cannot individually align upper/lower characters.
- H3: Adjacent runs do not create a reliable single annotation with explicit split.
- H4: Character spacing changes glyph distribution in the annotation, or has no useful effect.
- H5: DOCX↔ODT conversion loses at least some annotation details.

## Exit criteria / decision gate
Produce a capability report with: host/version, insertion, inspection, editing, division, alignment, delimiters, vertical writing, round-trip fidelity, reproducible artifacts, and limitations. Then recommend:
A. Native warichū editor with proven controls;
B. Native editor plus diagnostics/preview only for unsupported controls;
C. Separate LibreOffice core enhancement proposal for precise alignment.

Do **not** commit to a full custom alignment UI or rewrite the shared typography engine before this gate.
