# Feature and Requirements Inventory

## Classification
- **S** = standards-derived Japanese layout requirement; cite exact JLREQ section and edition before implementing.
- **E** = editorial/scholarly extension, **not** a W3C mandate.
- **H** = host-specific capability or workaround; verify empirically.
- Priority **P0** investigation / minimum warichū editor; **P1** next scholarly features; **P2** advanced research.
- Status for all below: **proposed**, not demonstrated.

| ID | Type | Priority | Capability | Required behaviour / question |
|---|---|---|---|---|
| W01 | S/H | P0 | Native warichū insertion | Selected text becomes an editable two-line annotation; preserve source string. |
| W02 | H | P0 | Existing warichū inspection/editing | Recognize, round-trip, and edit without flattening; determine limitations. |
| W03 | S | P0 | Automatic two-line division | Balance lengths while respecting punctuation and line-break rules; verify host control. |
| W04 | E/H | P0 | Explicit division | Let editor specify break point, but only promise if native rendering supports it. |
| W05 | S/H | P0 | Delimiters | Native bracket styles and their sizing/placement. |
| W06 | S/H | P0 | Horizontal/vertical | Correct placement in both directions, with document reflow. |
| W07 | S/H | P0 | Shorter-line alignment | Compare native beginning/centre/end/distributed outcomes; do not claim arbitrary control. |
| W08 | S/H | P1 | Annotation size and line gap | Test font metrics and spacing; host renderer may own geometry. |
| W09 | S/H | P1 | Multi-line reflow | Annotation spanning main-text line boundaries; editable and stable. |
| W10 | S/H | P1 | Punctuation and kinsoku | JLREQ-informed division, spacing, and no-break constraints. |
| W11 | E | P2 | Scholarly alignment anchors | Align specified upper/lower characters for critical editions; distinct from normal JLREQ. |
| W12 | E | P1 | Styles/presets/batch operations | Consistency, inspectability, explicit user approval for bulk changes. |
| R01 | S/H | P1 | Mono-ruby | Individual readings associated with individual base characters. |
| R02 | S/H | P1 | Group-ruby | Reading associated with base text as a unit. |
| R03 | S/H | P2 | Jukugo-ruby | Compound-aware positioning; preserve semantic association. |
| R04 | S/H | P1 | Ruby alignment, font, size, position | Respect writing mode; test overhang and collisions. |
| R05 | E | P1 | Ruby editing and batch operations | Apply, remove, audit, and preserve original readings. |
| V01 | S/H | P1 | Vertical sections/paragraphs | Use host-native writing modes where available. |
| V02 | S/H | P1 | Tate-chū-yoko | Short horizontal runs in vertical text; user-controlled detection. |
| V03 | S/H | P1 | Orientation and punctuation | Upright/rotated characters, brackets, ellipses, dashes. |
| P01 | S/H | P1 | Kinsoku inspector | Identify likely prohibited start/end characters; configurable conventions. |
| P02 | S/H | P1 | Punctuation spacing | Audit and propose fixes; never rewrite source silently. |
| P03 | S/H | P2 | Hanging punctuation | Detect candidates; native enforcement may be unavailable. |
| C01 | S/H | P1 | Emphasis marks | Apply/remove and choose appropriate position/shape. |
| C02 | S/H | P1 | Jidori | Fit text to specified character-cell count; test actual glyph metrics. |
| C03 | S/H | P2 | Furiwake | Divided annotation layout; clarify distinctions from warichū. |
| E01 | E | P1 | Scholarly profiles | Modern Japanese, classical Japanese, kanbun, diplomatic transcription. |
| E02 | E | P1 | Kaeriten integration | Avoid collisions with existing marinaMoji annotation features. |
| E03 | E | P1 | Typography inspector | Report issues, evidence, suggested fixes; never imply perfect layout analysis. |
| E04 | E | P2 | Interoperable metadata/export | DOCX/ODT, PDF visual check, future TEI/HTML/LaTeX paths. |

## Warichū UI design
- Select text → **Japanese Typography → Warichū**; show source, optional delimiters, native preview if feasible, detected writing mode, style.
- Show **automatic** vs **manual** division only after proving that manual division is faithfully representable in the host. Otherwise provide a clearly labelled advisory preview rather than a nonfunctional control.
- Display **native layout** as default; additional alignment modes must be feature-gated per host and version.
- Editing an existing annotation should be reversible, undoable, and preserve plain-text extraction.
- Preserve source code points, punctuation, and user-selected ranges. Never pad source with invisible or visible spacer characters as a default workaround.

## Profiles
Profiles are **marinaMoji inventions**, not normative JLREQ categories. Each consists of explicit configurable preferences, not irreversible transformations:
- Modern Japanese: standard punctuation/ruby/warichū defaults.
- Classical Japanese: historical kana and traditional forms preserved, annotation conventions configurable.
- Kanbun: compatible with kaeriten and kunten, character-level annotations.
- Diplomatic transcription: prioritize fidelity, disable silent normalization, permit explicit irregularities.

## Source of truth and verification
For each implemented rule record: `rule_id`, exact source URL/section, standard edition, host-specific behaviour, test cases, known deviations. JLREQ is a layout-requirements reference, not an executable universal conformance test. Review related W3C ruby guidance separately.
