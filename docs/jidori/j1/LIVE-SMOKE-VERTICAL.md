# Live smoke — vertical jidori gate

Do this in Writer before we build the toolbar. No marinaMoji button required.

## Setup

1. New Writer document.  
2. Page or paragraph: **vertical** writing (縦書き).  
3. Font: Japanese Mincho, **10.5 pt** (then repeat with Gothic).  
4. Type:

```text
あいうえお
あいう
あいうえお
```

## V1 — Spacing expand

1. Select the middle `あいう`.  
2. Format → Character → **Position** → Spacing ≈ **10 pt** (≈ 1 em).  
3. **Pass** if the column length looks about as long as five solid kana above/below, glyphs stay upright, no sideways squash.

## V2 — Scale shrink

1. Undo. Select a five-kana line.  
2. Scale width **55%** or **60%**.  
3. **Pass** if length ≈ three cells **and** glyphs remain upright/legible (not flattened on the physical X axis in a broken way).

## V3–V5 (quick)

- Adjacent ruby / tate-chū-yoko unchanged.  
- With and without Asian document grid: jidori run still roughly N cells.

## Result (2026-10-29)

| Check | Result |
|---|---|
| V1 Spacing expand | **Pass** |
| V2 Scale 60% @ 9 pt | **Fail** — thin glyphs; run shoved to line head |

Product: vertical **expand only**; vertical compress refused. See `03-VERTICAL-GATE.md`.
