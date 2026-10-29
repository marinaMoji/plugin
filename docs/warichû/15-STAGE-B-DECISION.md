# Stage B — Final decision report

**Host:** LibreOffice Writer **26.8.0.3** · Hiragino Mincho ProN · corpus 2026-10-29  
**Docs:** `10`–`14` + Stage A `05`–`09`

## Answers

### 1. Does LO warichū conform reasonably well to JLREQ?

**Mostly yes for the basic case:** two-line reduced annotation, ~50% scale, tight inner gap, vertical centering that may jut into the line gap, readable equal-length CJK notes (B01).  
**Not fully:** delimiter paint broken; some inner breaks violate conventional kinsoku (B11 horizontal; B19/B20 vertical).

### 2. What demonstrable typographic defects exist?

1. **UNO/ODF combine brackets collapse** (horizontal B16–B17; span_spike B) — illegible.  
2. **Kinsoku-unsafe inner breaks** (e.g. lower/second line starting with `）` / `、` / `」`).  
3. **No manual division / size / alignment API** — capability gaps, not paint bugs.  
4. Stretch on unequal lines — **observed**, usually acceptable; sometimes masks bad breaks.

### 3. What matters most for scholarly editing?

1. Text integrity & native editability — **OK** on bare combine.  
2. Legible, trustworthy layout — **OK** without delimiters.  
3. Delimiters when desired — **blocked** by U1.  
4. Intentional division in critical editions — **blocked** by missing U3.  
5. Avoiding prohibited breaks — **partially failing** (U2).

### 4. Can marinaMoji alone correct them?

| Defect | Plugin alone? |
|---|---|
| Bracket paint | **No** (do not set Prefix/Suffix) |
| Kinsoku breaks | **No** force; soft **warnings** only |
| Manual division | **No** without text mutation (refused) |
| Size / alignment modes | **No** |
| Apply/remove UX, docs, diagnostics | **Yes** |

### 5. Which require LibreOffice changes?

U1 brackets · U2 smarter division · U3 manual break · (optional) U5 size · U4 alignment modes.

### 6. Is the bracket defect reproducible?

**Yes** (horizontal). Vertical B21 inconclusive in thumbnail. Draft bug report ready; **not filed**.

### 7. Is improving automatic division a realistic upstream contribution?

**Yes**, as a behavioural improvement inside `BuildMultiPortion` / double-line break selection, with fixtures. Medium complexity; discuss kinsoku table choice. Strong Stage B motivation (B11/B19/B20).

### 8. What would manual division require?

Extend `SvxTwoLinesItem` + UNO + ODF attribute (or LO namespace); edit-stable index handling; DOCX degrades to auto. See `14-UPSTREAM-FEASIBILITY.md`. **Not** for immediate implementation.

### 9. Smallest useful next implementation step?

**Plugin:** finish Phase 2 smoke + caret-aware remove + document host limits (NEXT-LO).  
**Upstream prep (no submit yet):** root-cause U1 in a LO debug build using B16 ODT.  
**Optional spike:** soft kinsoku warning in marinaMoji (heuristic only).

### 10. What to defer?

- Alignment-mode / size UI  
- Manual division product UI  
- Word-first work  
- Ruby / full typography toolkit expansion  
- Filing Bugzilla/Gerrit until approved  
- Multi-font matrix completion (Noto Serif CJK / IPAex missing here)  
- Claiming full JLREQ conformance  

## Priority ranking

| Priority | Work | Benefit | Effort | Risk |
|---|---|---|---|---|
| 1 | Plugin smoke + polish | Stability | Low | Low |
| 2 | U1 bracket fix (upstream) | Delimiters | Med | Low–med |
| 3 | Soft division diagnostics (plugin) | Scholar awareness | Low | Low |
| 4 | U2 auto division (upstream) | Typography | Med–high | Med |
| 5 | U3 design discussion | Editions | High | High |
| 6 | U5 / U4 | Polish | Med–high | Med |

## Bottom line

LibreOffice’s **bare** warichū is a credible scholarly baseline. Perfection is blocked by **renderer and model limits**, not by marinaMoji apply/remove. Next value is honest plugin polish plus a **small upstream bracket fix**, then division quality—not new misleading controls.
