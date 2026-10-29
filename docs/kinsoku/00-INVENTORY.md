# Stage E1 inventory — existing marinaMoji material

## Typography features already shipped (LibreOffice)

| Feature | Docs | Code | Notes for Stage E |
|---|---|---|---|
| Warichū | `docs/warichû/` | `warichu.py` | Inner break ≠ body kinsoku; U2 notes exist; **do not modify** |
| Ruby | `docs/ruby/` | `ruby.py` | Group-ruby; JLREQ alignment notes; **do not modify** |
| Emphasis | `docs/emphasis/` | `emphasis.py` | `CharEmphasis`; **do not modify** |
| Tate-chū-yoko | `docs/tatechuyoko/` | `tatechuyoko.py` | Rotation+fit; **do not modify** |

## Prior kinsoku / punctuation findings (warichū track)

| Source | Finding |
|---|---|
| [`upstream/18-KINSOKU-NOTES.md`](../warichû/upstream/18-KINSOKU-NOTES.md) | `BuildMultiPortion` / double-line path does **not** post-filter not-start characters; body BreakIterator / `ForbiddenCharacters` reuse is a **feasible** post-adjust, **not coded** |
| [`upstream/BUG-U2-KINSOKU-BREAK.md`](../warichû/upstream/BUG-U2-KINSOKU-BREAK.md) | Draft upstream issue for JLREQ-aware warichū division — **not filed** without approval |
| Stage B corpus B11 / B19 / B20 | Demonstrated kinsoku-unsafe **internal** warichū breaks (H: `）` starts lower; V: `、` / `」` start lower) |
| [`08-LO-SOURCE-NOTES.md`](../warichû/08-LO-SOURCE-NOTES.md) | Inner split = ordinary portion fill into guessed width, not an explicit midpoint index |
| [`11-JLREQ-CONFORMANCE.md`](../warichû/11-JLREQ-CONFORMANCE.md) | C6: same kinsoku as body — **questionable** for combine |

## Distinction to preserve

**Ordinary paragraph line breaking** (this Stage E1 topic) is a separate code path from **warichū annotation-internal division** (`SwDoubleLinePortion` / `BuildMultiPortion`). Diagnostics must label which mechanism is involved.

## Reusable corpora

- `libreoffice/spikes/warichu/` Stage B fixtures (esp. punct / vertical cases).  
- New Stage E1 corpus: `libreoffice/spikes/kinsoku/` (body text only at first).

## Gaps before Stage E1 (now addressed in this folder)

- No production “typography inspector” — **E2 candidate** after review.  
- Capability matrix + JLREQ mapping — see `01`/`02`/`99`.  
- Rendered line starts — **Partial** live-view APIs only (`08`); not E2 default.  
- Scholarly profiles — sketched in `06`; UI deferred.  

Inventory cross-check ([warichū/docs inventory](854b1f60-9750-4e63-874d-a6773a674d4b)): ShareDocs folder has no kinsoku planning notes; reuse Stage B ODTs + `analyze_division_heuristics.py` for warichū advisory.
