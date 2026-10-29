# Paragraph Text-to-text + ruby line pitch

## Correction

The control that fixed adjacent vertical warichū was **not** `RubyAdjust`.

It is **Format → Paragraph → Alignment → Text-to-text → Alignment → Base line**.

| UI | UNO |
|---|---|
| Text-to-text → Base line | `ParaVertAlignment` = `ParagraphVertAlign.BASELINE` (**1**) |
| Text-to-text → Automatic | `AUTOMATIC` (0) |
| Text-to-text → Center | `CENTER` (3) |

`RubyAdjust=LEFT` remains Writer’s native phonetic-guide default and marinaMoji’s current ruby-letter alignment; it is a separate property.

## Product behaviour (0.3.22+)

On **Apply ruby**, marinaMoji sets `ParaVertAlignment=BASELINE` on the **paragraph** that contains the selection (without widening the character selection).

## Line pitch test (scholarly requirement)

With a **fixed** line distance, ruby should sit in the inter-line gap and **not** increase the pitch between body lines.

Spike: `libreoffice/spikes/ruby/ruby_line_spacing_spike.py`  
Artifacts: `libreoffice/spikes/ruby/artifacts/line_spacing/`

### Horizontal result (LO 26.8, Hiragino Mincho, `ParaLineSpacing` Mode=FIX)

| Text-to-text | Plain mean gap | Ruby mean gap | Ruby inflates? |
|---|---|---|---|
| BASELINE | same | same | **No** (Δ ≈ 0) |
| AUTOMATIC | same | same | **No** |
| CENTER | same | same | **No** |

Under true **fixed** line height, Writer kept body-line pitch unchanged with group-ruby on the line — ruby is not adding to the measured pitch (PDF glyph-centre gaps). That matches the scholarly expectation: ruby lives in the gap / reserved space, not as extra leading.

**Caveat:** If spacing is only “single” / 100% (`fo:line-height="100%"`), ruby **does** inflate pitch (earlier mis-set Mode showed ~+9 pt). Fixed distance must be set explicitly (Paragraph → Indents & Spacing → Line spacing → **Fixed**).

Vertical PDF measurement of column pitch is still rough in the spike; ODF still carries `fo:line-height` + `style:vertical-align`.

### Warichū note

Text-to-text **Base line** remains the setting that stabilised ruby beside vertical warichū in manual testing. Line-pitch behaviour is a separate axis from that multiportion glitch.
