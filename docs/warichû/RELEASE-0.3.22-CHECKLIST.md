# marinaMoji LibreOffice **0.3.22** — release validation

**Status:** **Manual smoke passed** (2026-10-29). Ready to publish when you choose.  
**Package:** `plugin/libreoffice/dist/MarinaMojiKaeriten.oxt` (`./build.sh` in `plugin/libreoffice/`).  
**Host:** LibreOffice Writer **26.8** (macOS) during development.

## What 0.3.22 includes

- Warichū (from 0.3.16): bare `CharCombineIsOn` span; caret-aware remove; no UNO brackets.
- Ruby: Apply / Remove; `RubyAdjust` LEFT; paragraph Text-to-text Base line on apply.
- Nesting ruby ↔ warichū on the same span refused.
- Kaeriten / vertical page unchanged.

## Smoke (confirmed)

- Warichū alone  
- Ruby alone (mono + group)  
- Ruby then warichū adjacent in vertical  
- Text-to-text Base line / Fixed line spacing behaviour as documented  
- Save/reopen ODT usable without marinaMoji for native attrs  

## Publish (when you want)

1. Commit remaining docs + code if not already committed.  
2. Tag e.g. `libreoffice-v0.3.22` (must match `description.xml`) or run **Release LibreOffice extension** in Actions.  
3. Sync update feed / GitHub Pages when you normally do.
