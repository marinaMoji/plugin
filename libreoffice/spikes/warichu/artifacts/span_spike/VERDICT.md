# Span spike v4 verdict (2026-10-29)

**Host:** LibreOffice Writer 26.8.0.3 · Hiragino Mincho ProN · Japanese  
**Screenshot:** `screenshots/v4_A_pass_B_brackets_fail.png`

| Method | Result |
|---|---|
| **A** `CharCombineIsOn` only on a note **span** (body uncombined) | **Pass** — readable two mini-rows (short and long notes) |
| **B** same + `CharCombinePrefix`/`Suffix` `（）` | **Fail** — glyphs collapse/overlap |

## Required apply recipe (LO)
1. Keep at least some non-combined text in the paragraph (typical: body + note), **or** clear sticky combine before the next insert.
2. On the note range only: set `CharCombineIsOn = True`.
3. Do **not** set `CharCombinePrefix` / `CharCombineSuffix` for MVP (UNO bracket props break paint here).
4. Never put `text-combine="lines"` on the paragraph style.

ODF for working runs: `style:family="text"` + `style:text-combine="lines"` only (no start/end-char).

## MVP implication
marinaMoji can ship span-based warichū apply/remove on LO. Delimiters: insert real bracket characters in the string if needed, or revisit UNO brackets later / upstream. Alignment still host-native.
