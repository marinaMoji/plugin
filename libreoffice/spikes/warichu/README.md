# Warichū spike (LibreOffice) — throwaway

Phase 1 feasibility experiments for native two-line text (`CharCombine*`).  
**Not** product UI. Do not wire into the `.oxt` until Gate 1.

Planning: [`docs/warichû/`](../../../docs/warichû/) · Phase 0: [`00-LO-PHASE0.md`](../../../docs/warichû/00-LO-PHASE0.md).

## Results so far (LibreOffice 26.8.0.3, 2026-10-29)

| Check | Result |
|---|---|
| Apply `CharCombineIsOn` + brackets | **Verified** |
| Source Unicode unchanged | **Verified** |
| Save / reopen ODT with combine still on | **Verified** |
| ODF `style:text-combine="lines"` (+ start/end chars) | **Verified** |
| Write DOCX from Writer | **Verified** (fidelity vs Word not judged yet) |
| Unequal-line alignment (T04) | **Unknown** — look at open ODT |
| Vertical (T07) | **Unknown** — use **Toggle vertical page** |
| Manual break (T05) | **Unknown** |

Artifacts: [`artifacts/`](artifacts/) (`spike_report.json`, `warichu_spike.odt`, matrix).

## How to re-run

```bash
cd libreoffice/spikes/warichu
./run.sh
```

That copies the macro into LibreOffice’s user Scripts folder and launches:

`vnd.sun.star.script:warichu_spike_macro.py$run_spike?language=Python&location=user`

Or: **Tools → Macros → Run Macro → My Macros → warichu_spike_macro → run_spike**.

## macOS note

On this machine, `/Applications/LibreOffice.app/.../LibreOfficePython` is **SIGKILL’d** when started as a subprocess (`Code Signature Invalid` / launch constraint), including from Terminal. Spikes therefore run **as a user macro inside soffice**, not via the external UNO socket client (`run_spike.py` is kept for environments where LO Python works).

## After the automated pass (your eyes)

1. Look at the Writer document the spike left open — unequal lines, brackets, odd lengths.  
2. Toolbar **Toggle vertical page** → note whether combine still looks right.  
3. Optionally open `artifacts/warichu_spike.docx` in Word later (T09 fidelity).  
4. Do **not** add a toolbar warichū button until those visuals are recorded.

## Controlled JP retest (after overlap failure)

First spike overlapped under Songti SC / Chinese locale. Re-test with Hiragino + `ja-JP` + optional 200% line spacing:

```bash
./run_retest_jp.sh
```

Compare labeled blocks **A** (plain) / **B** (combine) / **C** (combine + roomy lines) in the open document. Notes: `artifacts/retest_jp/WHAT_TO_LOOK_FOR.md`.

## Span-based spike (correct ODF shape)

Paragraph-level combine paints badly. UI success uses a **character span**. Rebuild:

```bash
./run_span_spike.sh
```

Expect ODF like `本文<text:span>割注…</text:span>` with `style:family="text"` + `text-combine="lines"`. Artifacts: `artifacts/span_spike/`.
