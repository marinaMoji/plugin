# Stage J1 — Cell calculator

## Inputs

- Selection string → grapheme count `n` (skip VS U+FE00–FE0F).  
- Target cells `N` (integer ≥ 1).  
- Asian font size `em_pt` (`CharHeightAsian` else `CharHeight`).

## Target advance

`target_em = N` (fullwidth cells).  
`current_em ≈ n` under CJK-fullwidth assumption.

## Expand (`N > n`, `n ≥ 2`)

```
extra_per_gap_em = (N − n) / (n − 1)
CharScaleWidth = 100
CharKerning_twips = round(extra_per_gap_em * em_pt * 20)
```

Twips: 1 pt = 20 twips (Writer `CONVERT_TWIPS` for `CharKerning`).

**Calibration:** 10.5 pt × 1.0 em → 210 twips ≈ **10.5 pt** Spacing; live match used ~10 pt.

## Shrink (`N < n`)

```
CharScaleWidth = max(1, round(100 * N / n))
CharKerning = 0   # do not mix channels on first apply
```

Prefer scale for shrink: negative spacing alone often cannot reach strong compression without collision.

## Noop / invalid

- `N == n` → noop (scale 100, kern 0) — still may attach jidori identity if re-applied for metadata; product may skip write.  
- `N < 1` → invalid.  
- `n == 1` and `N > 1` → JLREQ: space *after* the character. Writer cannot express “trailing only” cleanly with inter-gap kerning; **MVP: refuse single-character expand** or document scale-up as unsupported distortion. Prefer refuse.

## Reapply

Always recompute from **baseline** `n` and stored prior props — never from already scaled/spaced visual width.
