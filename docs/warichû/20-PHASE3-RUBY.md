# Phase 3 — LibreOffice ruby + coexistence

**Extension:** **0.3.22** — **manual smoke passed** (2026-10-29).  
**Scope:** native **group-ruby** apply/remove; coexistence with warichū / kaeriten / vertical.  
**Out of scope:** jukugo-ruby, mono auto-segmentation, ruby size/font UI, Word.

Full investigation: [`docs/ruby/`](../ruby/README.md).

## Product behaviour

| Action | Behaviour |
|---|---|
| Apply ruby | Select base → dialog → `RubyText` + **LEFT** + ABOVE; set paragraph **Text-to-text → Base line** (`ParaVertAlignment=BASELINE`); refuse if selection is warichū |
| Remove ruby | Selection or caret inside ruby span → clear `RubyText`; base unchanged |
| Warichū | Bare `CharCombineIsOn` only; refuse if selection has non-empty ruby (**do not** set `RubyText=""`) |
| Kaeriten / vertical page | Existing toolbar |

## Host properties

- `RubyText`, `RubyAdjust` (**LEFT** / ODF `left`), `RubyPosition` (ABOVE)
- Paragraph: `ParaVertAlignment` = BASELINE on apply
- ODF: native `text:ruby` on save
- `_RUBY_ADJUST_INDENT_BLOCK` / `_RUBY_ADJUST_BLOCK` kept for a possible future stretch UI (Fig.124 / Fig.125)

## Default policy

- **Ruby letter alignment:** LEFT (Writer-native; stable beside vertical warichū).
- **Paragraph Text-to-text:** Base line (user-confirmed for coexistence).
- Fig.124/125 stretch remains available in code, not the toolbar default.

## Coexistence

| Combination | Expectation |
|---|---|
| Ruby on body **beside** warichū span | OK (smoked) |
| Ruby **inside** warichū / warichū on ruby base | **Refused** by toolbar |
| Vertical + ruby + warichū | OK (smoked) |
| Fixed line spacing + ruby | Body pitch unchanged (horizontal measurement) |

## Files

- `libreoffice/marinamoji_kaeriten/ruby.py`
- Toolbar: Apply ruby / Remove ruby
- Tests: `libreoffice/tests/test_ruby.py`
- Spike: `libreoffice/spikes/ruby/`
