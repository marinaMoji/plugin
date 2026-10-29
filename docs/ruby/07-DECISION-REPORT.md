# G. Final decision report

Investigation of `本文` + `もと` (+ adjacent warichū `割り注は、良いです。` + `国際`) against JLREQ and LibreOffice 26.8 native ruby.

## Answers

### 1. Is the vertical alignment problem caused by marinaMoji or LibreOffice?

**Primarily a property choice, not a marinaMoji-only renderer bug.**  
marinaMoji and Asian Phonetic Guide use the same UNO path. With `CENTER` correctly set, vertical centering works. The supplied vertical screenshot resembles **start-aligned (LEFT)** appearance and/or field shading + warichū adjacency. Writer is not inventing a separate vertical layout API; `LEFT`/`CENTER`/`BLOCK` all work, with different looks.

### 2. Is `本文` + `もと` represented as group ruby?

**Yes.** One `text:ruby` over the two-character base. That is correct for this reading (not mono, not jukugo).

### 3. Which alignment mode is currently used?

**0.3.19+: `RubyAdjust` INDENT_BLOCK** (`distribute-space`, Fig.124).  
**0.3.18: BLOCK.** **0.3.17: CENTER.**

### 4. Which mode best follows JLREQ for this example?

**Stretch is required in the usual case; two stretch geometries are valid.**  
JIS/JLREQ Fig.124 (1:2:1) ≈ `INDENT_BLOCK`; Fig.125 (edge flush) ≈ `BLOCK`.  
CENTER is a solid-block alternative. See [08-VERTICAL-FRAME-VS-OPTICAL.md](08-VERTICAL-FRAME-VS-OPTICAL.md).  
marinaMoji **chooses Fig.124** (`INDENT_BLOCK`) as its default — a product policy, not a universal JLREQ requirement.

### 5. Can the alignment be corrected through UNO?

**Yes.** Set `RubyAdjust` to INDENT_BLOCK, BLOCK, or CENTER. No custom drawing required.

### 6. Is the apparent ruby-to-base gap actually excessive?

**No evidence of a marinaMoji-induced gap.** Vertical can look more open because of side placement and column metrics; it matches native phonetic guide behaviour. Do not add offsets.

### 7. Does vertical writing change ruby font metrics or positioning?

**Position side changes** (above → right) via the same `RubyPosition ABOVE`. Font size remains host ~½. Alignment enums are interpreted along the block axis (LEFT = toward the start of the base column).

### 8. Does adjacent warichū affect ruby layout?

**It does not rewrite ruby properties.** Visually, warichū’s double mini-lines next to a start-heavy ruby can look confusing. Prefer INDENT_BLOCK (default) and keep spans adjacent, not nested. Plugin refuses nesting from 0.3.18.

### 9. Which improvements can be implemented immediately?

- Default `RubyAdjust` = INDENT_BLOCK (0.3.19; was BLOCK in 0.3.18)  
- Re-assert adjust after `RubyText`  
- Refuse ruby↔warichū nesting; clear conflicting props on apply  
- Documentation under `docs/ruby/`

### 10. Which improvements require upstream LibreOffice changes?

- True **jukugo-ruby** model  
- Cleaner clearing of sticky empty `text:ruby` wrappers (R1)  
- Any fine-grained overhang policy beyond alignment enums  
- Separate scholarly modes beyond UNO (optional future UI for BLOCK vs INDENT_BLOCK)

**Do not file Bugzilla for vertical LEFT-looking CENTER without a reproducer that shows CENTER stored but LEFT painted.**

## Immediate product stance

Use the **best native ruby Writer can provide**: group ruby + **INDENT_BLOCK** (Fig.124) + ABOVE, editable, ODT-native, no hacks. Warichū remains 0.3.16 behaviour beside ruby, not inside it.
