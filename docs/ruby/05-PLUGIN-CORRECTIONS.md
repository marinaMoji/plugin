# E. Plugin corrections

## Extension **0.3.22**

### Paragraph Text-to-text → Base line on Apply ruby

**UI:** Format → Paragraph → Alignment → Text-to-text → **Base line**  
**UNO:** `ParaVertAlignment = ParagraphVertAlign.BASELINE` (1)

User-confirmed: this (not `RubyAdjust`) stabilises ruby beside vertical warichū. Apply ruby now sets it on the containing paragraph.

Also: spike + measurements for whether ruby inflates **fixed** line pitch (`docs/ruby/09-PARA-VERT-AND-LINE-SPACING.md`). Horizontal FIX spacing: **ruby does not change line pitch** (Δ≈0). Single/100% spacing does inflate — use Fixed line spacing for scholarly layout.

## Extension **0.3.21**

### Default `RubyAdjust` → LEFT

Writer-native `SvxRubyItem` default. Stretch modes kept as internal alternatives.  
*(Earlier note wrongly equated user “baseline” with LEFT — that referred to paragraph Text-to-text; see 0.3.22.)*

## Extension **0.3.20**

### Warichū regression: do not clear `RubyText` on combine apply

**Cause:** In 0.3.18–0.3.19, `_apply_combine` called `RubyText=""` before `CharCombineIsOn=True` to “avoid nesting.” Writer still attaches an empty `text:ruby` wrapper when clearing ruby on a span that never had a reading. That wrapper can suppress `text-combine=lines` painting — **even if warichū is applied before any ruby** (user sequence).

**Fix:** Bare `CharCombineIsOn` only again. Nesting remains refused when `RubyText` is non-empty.

### Mono vs group adjust

- Single-character base → `CENTER` (solid; avoids false gaps on e.g. `文` + `ほん`)
- Multi-character base → `INDENT_BLOCK` (Fig.124 product default)

## Extension **0.3.19**

### Default alignment → INDENT_BLOCK

**File:** `libreoffice/marinamoji_kaeriten/ruby.py`

- Was (0.3.18): `RubyAdjust` BLOCK (3) → ODF `distribute-letter` (JLREQ Fig.125)  
- Now: `RubyAdjust` INDENT_BLOCK (4) → ODF `distribute-space` (JLREQ Fig.124 / JIS 1:2:1)

**Why:** marinaMoji’s chosen typographic default for shorter group-ruby — balanced lead/inter/trail spacing. This is **not** a claim that JLREQ requires Fig.124 exclusively; Fig.125 (`BLOCK`) remains valid and is kept as `_RUBY_ADJUST_BLOCK` for possible future advanced controls.

No change to ruby text, no inserted spaces, no optical positioning.

## Extension **0.3.18** (prior)

### 1. Default alignment → BLOCK (superseded by 0.3.19)

CENTER → BLOCK for stretch vs solid centre.

### 2. Re-assert `RubyAdjust` after `RubyText`

Some Writer paths appear to reset alignment when `RubyText` is first assigned. Apply sets adjust after text and sets it again.

### 3. Refuse nesting with warichū

- **Apply ruby** refuses if the selection has `CharCombineIsOn`.  
- **Apply warichū** refuses if the selection has non-empty `RubyText`.  
- Apply ruby clears combine props on the span before setting ruby.  
- Apply warichū clears `RubyText` on the note span when combine is applied (after the refuse check for non-empty ruby).

### 4. No visual hacks

No inserted spaces, ZWSP, text boxes, or images for alignment.

## Tests

`libreoffice/tests/test_ruby.py` — span expand helpers + asserts default adjust is INDENT_BLOCK; BLOCK constant still defined.

## Spike

`libreoffice/spikes/ruby/ruby_align_spike.py` — labels for 0.3.19+ INDENT_BLOCK default vs BLOCK alternative.
