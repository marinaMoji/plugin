# Stage J1 — Vertical writing gate

**Status:** **Decided from live smoke (2026-10-29).**

## Critical question

Does `CharScaleWidth` scale along the **inline progression** in vertical Japanese, or along the **physical horizontal** axis (distorting upright CJK)?

## Live results (Mincho-style face)

| # | Action | Result |
|---|---|---|
| **V1** | `あいう` + Spacing ≈ 1 em/gap | **Pass.** Column length ≈ five solid kana; glyphs upright. |
| **V2** | `あいうえお` + Scale width **60%** at **9 pt** | **Fail for jidori.** Glyphs go thin (physical width squash); run packs to the **line head** (“shoved up”) with empty advance below — not a clean N-cell allocation next to solid `あいう`. |

Screenshot evidence: spaced three-kana column matches five-kana height; 60% five-kana column is short, thin, and top-heavy.

## Outcome → product scope

| Channel | Horizontal | Vertical |
|---|---|---|
| Expand (`CharKerning`) | Yes | **Yes** |
| Shrink (`CharScaleWidth`) | Yes (approx.) | **No** — refuse |

**Do not** ship unrestricted “jidori” that silently applies Scale width in 縦書き.

### Apply policy (MVP)

1. Always prefer Spacing for expand.  
2. If `N < n` (compress):  
   - Horizontal → Scale width.  
   - Vertical → **refuse** with a clear message (see below).  
3. Optional later experiment: negative `CharKerning` for mild vertical compress (not validated; may collide glyphs). Out of MVP unless smoked.

### User-facing message (vertical compress)

> Compression into fewer cells is not supported in vertical writing yet.  
> Expanding into more cells works. For fewer cells, use horizontal writing or set Scale width manually (glyphs may distort).

## Explicit alternative rejected

“Horizontal-only jidori” is **unnecessary**: vertical **expand** works. Scope is **asymmetric by writing mode**, not “H only.”
