# LibreOffice next steps (post Stage C plugin polish)

**User priority:** LibreOffice perfect before Word.

## Done (Stage C plugin — 0.3.16)

- Caret-aware **Remove warichū** (expand to CharCombine span).
- Unit/smoke helper tests (`tests/test_warichu.py`) + optional in-Writer `warichu_smoke_macro.py`.
- JA/FR toolbar labels; Help text notes host owns split/size; no UNO brackets.
- Extension build target: `libreoffice/dist/MarinaMojiKaeriten.oxt`.

## Immediate remaining (manual in Writer)

1. Install 0.3.16 → smoke: apply, caret-remove, save/reopen ODT, undo, kaeriten adjacent.
2. Optional soft kinsoku **warnings** (predicted only) — still deferred.

## Upstream (no submit without approval)

| ID | Status |
|---|---|
| U1 delimiter paint | Confirmed; **no LO build** — see `upstream/17`, `BUG-U1-*` |
| U2 kinsoku break | Feasible small post-adjust; not coded — `upstream/18`, `BUG-U2-*` |
| U3 scholarly manual division | Proposal only — `upstream/19` |

**Build env:** not present locally (`16-LO-BUILD-ENVIRONMENT.md`). Need VM/disk before compiling patches.

## Blocked / unsupported

- Alignment / size / manual-division **product** UI until upstream exists.
- UNO Prefix/Suffix delimiters until U1 fixed.
- Spaces / images as warichū.

## Docs

A `05`–`09` · B `10`–`15` · C `16` + `upstream/*`
