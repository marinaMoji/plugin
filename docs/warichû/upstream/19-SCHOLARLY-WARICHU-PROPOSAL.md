# Proposal — Optional Advanced Warichū Layout (manual division)

**Working names**

| Layer | Name |
|---|---|
| LibreOffice feature | **Advanced Warichū Layout** |
| marinaMoji preset | **Scholarly / Historical Composition** |

**Principle:** Existing Writer warichū defaults stay the default. Advanced mode is opt-in.  
**Stage C:** Architecture only — **not implemented.** Discuss upstream before coding.

## First advanced capability: manual division

Editors of critical / diplomatic editions may need an **intentional** break between the two annotation lines that automatic width-search must not override.

Underlying text remains one continuous, editable string (no split into two fields; no inserted spaces).

## Technical sketch

### 1. `SvxTwoLinesItem` extension

Add optional break index:

- `sal_Int32 m_nBreakPos` — Unicode character index into the combined run where the **second** line starts; `-1` = automatic (default).

Preserve existing `bOn`, `cStartBracket`, `cEndBracket`.

### 2. UNO

New optional property, e.g. `CharCombineBreak` (`long`, default `-1`).  
marinaMoji would set it only under the Scholarly preset.

### 3. ODF persistence

Today: `style:text-combine="lines"` (+ optional start/end chars).  
Needed: an attribute for break position, e.g.:

- Prefer an OASIS-standardized attribute after discussion, **or**
- Temporary `loext:text-combine-break` (LO namespace) with documented ignore-on-unknown.

Older LO: ignore unknown attribute → automatic division (**graceful degrade**).

### 4. Editing behaviour

| Edit | Behaviour |
|---|---|
| Insert/delete **before** break | Break index shifts by delta (bookmark-like) |
| Edit that invalidates index | Clamp to `[1, len-1]` or fall back to `-1` (auto) |
| Clear advanced mode | Set break to `-1` |

Implementation detail: store as item value updated by `SwpHints` edit notifications — same difficulty class as other positional char attrs; needs careful design with Writer maintainers.

### 5. Renderer

In `BuildMultiPortion` double-line branch:

- If `m_nBreakPos >= 0`, force first line length to that index (after validating kinsoku or allowing scholarly override flag).  
- Else keep current width-search.

No change to 50% default scale in v1 of this proposal.

### 6. DOCX

OOXML `w:eastAsianLayout` has `combine` / `combineBrackets` only.  
**Fallback:** export as combine without break; Word shows automatic split. Import from Word → always `-1`.

### 7. Backward compatibility

| Consumer | Result |
|---|---|
| Old LO | Auto layout; text intact |
| New LO, no break set | Identical to today |
| New LO, break set | Honours index |
| marinaMoji without scholarly preset | Never sets break |

### 8. Likely maintainer objections

1. ODF extension / standardization burden.  
2. Break index vs grapheme / surrogates / VS sequences.  
3. Edit-stability of indices (fragile UX).  
4. Interaction with fields, ruby nesting, bidi.  
5. “Scholarly” features belong in specialized tools, not Writer core.  
6. DOCX round-trip loss.

**Mitigations:** default off; LO-namespace first; thorough tests; marinaMoji owns UX warnings; accept DOCX loss.

## Discussion ask (upstream)

Before implementation: short design mail — “optional break index on two-line attribute; default unchanged; ODF strategy?”

## Out of scope for this proposal

Alignment modes, configurable size, replacing automatic defaults.
