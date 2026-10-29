# Warichū spike (LibreOffice) — throwaway

Phase 1 feasibility experiments for native two-line text (`CharCombine*`).  
**Not** product UI. Do not wire into the `.oxt` until Gate 1.

Planning: [`docs/warichû/`](../../../docs/warichû/) · Phase 0: [`00-LO-PHASE0.md`](../../../docs/warichû/00-LO-PHASE0.md).

## Results so far (LibreOffice 26.8.0.3, 2026-10-29)

| Check | Result |
|---|---|
| Apply bare `CharCombineIsOn` (span) | **Pass** (Stage B corpus) |
| Apply + UNO Prefix/Suffix brackets | **Fail paint** (horizontal); ODF still stores chars |
| Source Unicode unchanged | **Verified** (incl. VS16) |
| Save / reopen ODT | **Verified** |
| ODF `style:text-combine="lines"` | **Verified** |
| DOCX `w:eastAsianLayout combine` | **Exported**; Word paint **untested** |
| Unequal-line stretch (`CalcNewBlock`) | **Observed** (e.g. B06) |
| Vertical combine | **Works**; some kinsoku-bad breaks (B19/B20) |
| Manual break | **Unsupported** in model |

Stage B: `./run_stage_b_corpus.sh` → [`artifacts/stage_b/`](artifacts/stage_b/). Docs `10`–`15`.

## How to re-run

```bash
cd libreoffice/spikes/warichu
./run_stage_b_corpus.sh
# PDF (UNO storeAsURL may fail; headless works):
# soffice --headless --convert-to pdf --outdir artifacts/stage_b artifacts/stage_b/warichu_stage_b_horizontal.odt
```

Legacy spike:

```bash
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
