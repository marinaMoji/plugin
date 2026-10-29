# Jidori 字取り

**Status:** implemented in LibreOffice extension **0.3.33** (toolbar `.v6`).  
**Roadmap:** [`../warichû/NEXT-LO.md`](../warichû/NEXT-LO.md) #7 · inventory **C02**.

## Product

Select a short Japanese run → **Apply jidori** → enter **N** → Confirm.  
**Remove jidori** restores prior Scale width / Spacing when marinaMoji identity is present.

Approximate fit to N full-width cells — **not** Word Fit Text.

| Writing | Expand | Compress |
|---|---|---|
| Horizontal | Spacing | Scale width |
| Vertical | Spacing | **Refused** |

## Docs

| Path | Role |
|---|---|
| [`j1/`](j1/) | Native feasibility + vertical gate |
| [`j2/00-REVERSIBILITY-DESIGN.md`](j2/00-REVERSIBILITY-DESIGN.md) | Bookmark + UDP restore |
| [`99-IMPLEMENTATION-REPORT.md`](99-IMPLEMENTATION-REPORT.md) | Working implementation |
| [`RELEASE-0.3.33-SMOKE.md`](RELEASE-0.3.33-SMOKE.md) | Manual smoke |

## Code

`libreoffice/marinamoji_kaeriten/jidori.py` · `jidori_math.py`
