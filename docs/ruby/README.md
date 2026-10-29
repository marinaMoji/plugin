# marinaMoji — LibreOffice ruby investigation

Native phonetic guide (振り仮名 / ruby) for Writer. Companion to warichū docs under `docs/warichû/`.

| Doc | Purpose |
|---|---|
| [01-NATIVE-CAPABILITY-MATRIX.md](01-NATIVE-CAPABILITY-MATRIX.md) | UNO / ODF what Writer supports |
| [02-JLREQ-COMPARISON.md](02-JLREQ-COMPARISON.md) | JLREQ vs observed behaviour |
| [03-HORIZONTAL-VERTICAL.md](03-HORIZONTAL-VERTICAL.md) | H/V screenshots, measurements, marinaMoji vs native |
| [04-GROUP-MONO-JUKUGO.md](04-GROUP-MONO-JUKUGO.md) | What is representable |
| [05-PLUGIN-CORRECTIONS.md](05-PLUGIN-CORRECTIONS.md) | Changes shipped in the extension |
| [06-UPSTREAM-ISSUES.md](06-UPSTREAM-ISSUES.md) | Host limitations (no Bugzilla yet) |
| [07-DECISION-REPORT.md](07-DECISION-REPORT.md) | Answers to the ten investigation questions |
| [08-VERTICAL-FRAME-VS-OPTICAL.md](08-VERTICAL-FRAME-VS-OPTICAL.md) | Vertical BLOCK “misalignment”: frames vs ink; JLREQ Fig.124/125 |
| [09-PARA-VERT-AND-LINE-SPACING.md](09-PARA-VERT-AND-LINE-SPACING.md) | Text-to-text Base line; fixed line pitch vs ruby |

**Spike artifacts:** `libreoffice/spikes/ruby/artifacts/align_spike/`, `…/vertical_geometry/`, `…/line_spacing/`  
**Code:** `libreoffice/marinamoji_kaeriten/ruby.py`  
**Extension:** **0.3.22** (ParaVertAlignment BASELINE on apply; RubyAdjust LEFT)

Keep ruby upstream issues separate from warichū `tdf#174224`.
