# Tate-chū-yoko — implementation report (0.3.28)

1. **Native mechanism?** `CharRotation=900` + `CharRotationIsFitToLine=True` (not `CharCombineIsOn`).
2. **Suitable for tate-chū-yoko?** Yes as LO’s approximation; confirmed vertical smoke for `12`.
3. **vs kumimoji?** Different concept; we do not implement kumimoji.
4. **`12` in vertical?** Yes (user screenshot).
5. **Max technical length?** No hard UNO max discovered; Fit compresses long runs. Policy caps auto at 2, confirm 3–4, refuse 5+.
6. **Auto-accepted?** Exact 2-grapheme digits or Latin in vertical writing.
7. **Override?** 3–4 digit/Latin/numeric via Yes/No confirm.
8. **Refused?** Japanese prose, mixed with kanji/kana, length 1 or 5+, horizontal apply, warichū/ruby overlap.
9. **Caret detection?** Yes for exact 2-digit/Latin runs; not for substrings of longer numbers.
10. **Preserve text?** Yes — properties only.
11. **Remove preserves unrelated?** Clears only rotation + fit.
12. **ODT?** Rotation is ordinary character formatting (survives save/reopen).
13. **DOCX?** Not validated; rotation may round-trip imperfectly — known risk.
14. **Remaining LO defects?** No first-class 縦中横; compression on long fits; not Word-parity.
15. **Ready for manual testing?** Yes — rebuild OXT 0.3.28.
