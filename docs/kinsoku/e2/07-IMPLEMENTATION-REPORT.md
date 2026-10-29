# Stage E2 — Implementation report

**Version:** LibreOffice extension **0.3.31**  
**Date:** 2026-10-29

## Delivered

- Read-only **Inspect Japanese Typography** command + toolbar button (`.v5` / `m18`).  
- Composition settings report (paragraph + document).  
- Rules: `PARA_FORBIDDEN_RULES_OFF`, `PUNCTUATION_MIXED_WIDTH`, `EXPLICIT_BREAK_BEFORE_NOTSTART`.  
- Shared analysis module without UNO.  
- EN / JA / FR strings.  
- Unit tests passing.  
- `.oxt` built via `libreoffice/build.sh`.

## UNO answers

1. Paragraph `ParaIs*` — read successfully (effective booleans).  
2. Document compression / kerning / ForbiddenCharacters — read with LocaleData fallback.  
3. Inheritance: effective values + optional PropertyState; unavailable ≠ disabled.  
4. Unavailable properties display **Unavailable**.  
5. ODT persistence: relies on Stage E1 ODF mapping; manual reopen smoke pending install.

## Diagnostics

6. Three rules above.  
7. Deferred: layout kinsoku, warichū inner break, profiles, corrections.  
8. False positives: JP-context gate, URL skip, Latin window for half-width, no paragraph-boundary-as-break.  
9. Explicit soft breaks: yes when present in paragraph string.  
10. Ranges: paragraph index + offsets in extracted string (session-valid).  
11. Ruby/warichū/tate: presence flags; no false warichū warnings; kaeriten not treated as JP punct parser.

## UI

12. Toolbar after ruby, before copy.  
13. Compact read-only dialog.  
14. JA/FR/EN.  
15. Settings vs issues separated.  
16. Limited-coverage disclaimer; no JLREQ-complete claim.

## Integrity

17–20. Designed read-only with `isModified` restore; manual annotation regression required after install.

## Release

21. Unit tests: all green.  
22. Live Writer integration / dirty-flag smoke: **manual**.  
23. `.oxt` built: `libreoffice/dist/MarinaMojiKaeriten.oxt`.  
24. `validate-extension.sh` / build pipeline used.  
25. Manual: install, restart Writer, run smoke in `05-TEST-CORPUS.md`.

## Next steps

26. Highest value: complete live smoke + soft-break confirmation on LO 26.8.  
27. Prefer scholarly profiles after more textual rules prove stable—not composition-control UI first.  
28. Blocking for deeper kinsoku: lack of authoritative headless line geometry (Stage E1).
