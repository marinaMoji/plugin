# Jidori spike (experimental)

Pure math: `jidori_math.py`  
Writer macro: `jidori_spike_macro.py` (APSO / user Scripts — **not** in the released OXT toolbar)

## Manual Stage A

1. Confirm **Format → Character → Position → Scale width** 75% visibly condenses text (J1).  
2. Select `あいう`, run `apply_jidori_spike(5)` → should expand toward 5 cells (J3).  
3. Select `あいうえお`, run `apply_jidori_spike(3)` → should compress (J4).  
4. Save/reopen ODT; check Position tab values.  
5. `remove_jidori_spike()`; text code points unchanged (J6).

### Live calibration (2026-10-29, 10.5 pt)

| Case | Hand Position values that matched visually |
|---|---|
| 3 kana → 5 cells | Spacing ≈ **10 pt** (~1 em/gap; formula 10.5) |
| 5 kana → 3 cells | Scale width ≈ **55%** (formula 60%) |

UNO `CharKerning` unit must still be mapped so the macro’s Spacing equals ~`extra_em × font_pt` in the Position dialog.

See [`docs/jidori/03-FEASIBILITY-VERDICT.md`](../../../docs/jidori/03-FEASIBILITY-VERDICT.md).
