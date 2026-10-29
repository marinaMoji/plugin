# Phase 3 — LibreOffice ruby + coexistence

**Extension target:** **0.3.20** (0.3.19 INDENT_BLOCK; 0.3.20 warichū empty-ruby fix + mono CENTER)  
**Scope:** native **group-ruby** apply/remove; coexistence with warichū / kaeriten / vertical.  
**Out of scope:** jukugo-ruby, mono auto-segmentation, ruby size/font UI, Word.

Full investigation: [`docs/ruby/`](../ruby/README.md).

## Product behaviour

| Action | Behaviour |
|---|---|
| Apply ruby | Select base → dialog → `RubyText` + adjust + ABOVE; **group** → INDENT_BLOCK, **mono** (1 char) → CENTER; refuse if selection is warichū |
| Remove ruby | Selection or caret inside ruby span → clear `RubyText`; base unchanged |
| Warichū | Bare `CharCombineIsOn` only; refuse if selection has non-empty ruby (**do not** set `RubyText=""`) |
| Kaeriten / vertical page | Existing toolbar; smoke coexistence manually |

## Host properties

- `RubyText`, `RubyAdjust` (**INDENT_BLOCK** / ODF `distribute-space`), `RubyPosition` (ABOVE)
- ODF: native `text:ruby` on save
- `_RUBY_ADJUST_BLOCK` kept in code for a possible future advanced control (Fig.125)

## Default policy

marinaMoji chooses **Fig.124** (balanced 1:2:1). That is a **product typographic default**, not a claim that JLREQ forbids Fig.125 (`BLOCK`).

## Coexistence

| Combination | Expectation |
|---|---|
| Ruby on body **beside** warichū span | OK |
| Ruby **inside** warichū / warichū on ruby base | **Refused** by toolbar (0.3.18+) |
| Vertical + ruby + warichū | Same UNO; INDENT_BLOCK default |

## Manual smoke (0.3.19)

1. Select `本文` → Apply ruby → `もと` → reading uses balanced distribution (INDENT_BLOCK).  
2. Caret inside → Remove → base `本文` remains.  
3. Nearby note → Apply warichū; toggle vertical; save/reopen ODT.  
4. Optional: Asian Phonetic Guide with distribute-space should match marinaMoji paint.

## Files

- `libreoffice/marinamoji_kaeriten/ruby.py`
- Toolbar: Apply ruby / Remove ruby
- Tests: `libreoffice/tests/test_ruby.py`
- Spike: `libreoffice/spikes/ruby/`
