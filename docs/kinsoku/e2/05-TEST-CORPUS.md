# Stage E2 — Test corpus notes

## Automated (no LO)

`libreoffice/tests/test_typography_inspector.py` — settings, mixed width, explicit soft breaks, false-positive suppressions (URL, Latin quote, paragraph boundary).

## Manual smoke (after install 0.3.31)

1. New JP paragraph, Asian Typography defaults → inspect → settings Enabled, no issues.  
2. Disable forbidden rules on paragraph → informational finding.  
3. Soft break (Shift+Enter) before `、` → advisory.  
4. `。` + `｡` in Japanese prose → advisory; URL with `.` → no mixed-width.  
5. Paragraph with ruby / warichū / emphasis / tate / kaeriten → inspect → document unchanged (`isModified` false if previously clean).  
6. Vertical page paragraph → settings still readable.  
7. Multi-paragraph selection with mixed kinsoku on/off → Mixed settings.
