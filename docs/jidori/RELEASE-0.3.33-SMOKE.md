# Jidori smoke — 0.3.33

Install `libreoffice/dist/MarinaMojiKaeriten.oxt`, restart Writer, show marinaMoji toolbar `.v6`.

## Happy path (horizontal)

1. Type `あいう` / `あいうえお` (Mincho 10.5 pt).  
2. Select `あいう` → **Apply jidori** → N=`5` → Apply.  
3. Width ≈ five solid kana.  
4. **Remove jidori** → spacing back to normal.  
5. Select `あいうえお` → Apply → N=`3` → visibly compressed.  
6. Remove → restored.

## Prior formatting

1. Set Scale width 90% on `日本`.  
2. Apply jidori N=`4`.  
3. Remove → Scale width should be **90%** again (not 100%).

## Vertical

1. Vertical page: expand `あいう` → N=`5` OK.  
2. Compress five kana → N=`3` → clear refuse message (no thin shoved glyphs).

## Safety

- No selection → instruction.  
- `ABC` → refused.  
- Ordinary Spacing (not ours) → Remove → “No marinaMoji jidori…”.  
- Save ODT → reopen → Remove still restores.  
- Undo after Apply.

## Pass when

All of the above behave as described; text code points never change.
