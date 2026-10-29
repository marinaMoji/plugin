# What to look for (JP retest)

Document: `warichu_retest_jp.odt` (left open).
Font requested: **Hiragino Mincho ProN**

## Sections
- **A** — plain Japanese text (sanity: must look normal).
- **B** — combine on, default line spacing (same as first spike conditions, but JP font/locale).
- **C** — combine on, **200%% line spacing** (tests “overlap because the line box is too short”).

## Pass / fail
- **Pass:** each combined run shows two readable mini-rows inside one line, with brackets if requested.
- **Fail:** glyphs still stacked on top of each other / double-printed (as in first spike).
- Note whether **C** is better than **B**.

Optional: Format → Character → Position on one combined word; screenshot that dialog too.
