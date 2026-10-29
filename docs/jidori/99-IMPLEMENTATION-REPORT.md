# Jidori — implementation report (0.3.33)

## 1. UNO properties

| Role | Property |
|---|---|
| Expand | `CharKerning` (twips; Position → Spacing) |
| Shrink (horizontal) | `CharScaleWidth` (%) |
| Identity | Bookmark `marinaMoji_jidori_<id>` |
| Restore payload | `UserDefinedProperties` key `marinaMoji.Typography.Jidori.<id>` (JSON) |

## 2. N-cell math

- Assume CJK grapheme ≈ 1 em.  
- Expand: `extra_em = (N−n)/(n−1)` → twips = `round(extra_em × em_pt × 20)`.  
- Shrink: `scale% = round(100×N/n)`.  
- Vertical shrink: **invalid** (live gate).

## 3–5. Composition

| Mode | Horizontal | Vertical |
|---|---|---|
| Expand (spacing) | Yes | Yes |
| Shrink (scale) | Yes (approx.) | **No** — refuse |

Accuracy: ~10 pt Spacing ≈ 1 em at 10.5 pt; ~55–60% scale for 5→3.

## 6–10. Reversibility

On Apply, snapshot prior scale/kern/style (+ PropertyState). Store with N in UDP; wrap run in bookmark.  
Remove restores snapshot; deletes bookmark + UDP.  
Reapply restores baseline first, then new N (no compounding).  
Without bookmark/payload: Remove does **not** reset to 100/0.

## 11–12. Styles / annotations

Character style name restored when it was direct.  
Refuse apply on warichū, ruby, or tate-chū-yoko on the same span. Emphasis/kaeriten left alone if present on other formatting.

## 13–15. Undo / ODT / DOCX

Undo: ordinary Writer property + bookmark edits (one logical user action may still be multi-step in the undo stack — smoke).  
ODT: bookmarks + UserDefinedProperties must round-trip (manual smoke).  
DOCX: scale/spacing may export; marinaMoji identity likely **lost** — documented limitation; not Fit Text.

## 16. Unsupported (MVP)

- Latin / Western digits / mixed script  
- Vertical compression  
- Single-character expand  
- Multi-paragraph / table-cell-crossing selections  
- Whole-line 均等割付 (furiwake)  
- Word `w:fitText` parity  

## 17–18. Tests / readiness

- Unit: `tests/test_jidori_math.py`, `tests/test_jidori.py`  
- Manual: [`RELEASE-0.3.33-SMOKE.md`](RELEASE-0.3.33-SMOKE.md)  
- Extension: **0.3.33** toolbar `.v6` — ready for install + manual smoke
