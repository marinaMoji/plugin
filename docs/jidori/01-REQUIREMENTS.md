# Jidori — typographic requirements (working definition)

## Editorial behaviour (Japanese DTP / Word)

Typical user intent:

1. Select a short string (often 2–8 graphemes).  
2. Choose a target width of **N fullwidth cells** (e.g. “fit into 5 字”).  
3. The host **expands** inter-character space if the natural width is smaller than N cells, or **compresses** glyphs/spacing if larger, so the run occupies approximately N ems.

Microsoft Word exposes this as run property **Fit Text** (`w:fitText`): target width in twips; optional `w:id` to scale several runs together ([OOXML fitText](https://ooxml.org/wordml/w-fittext/)).

## Related but distinct: 均等割り付け

Distributed / justified-last-line alignment spreads characters across the **line measure**. That is closer to roadmap **Furiwake 振り分け** (#8), not jidori’s fixed cell-count fit on an arbitrary run.

## Scholarly notes

- Critical editions rarely need aggressive jidori; forms, headings, and bilingual templates do.  
- Never implement by inserting visible spacer characters or ZWSP by default (same rule as warichū inventory).  
- Diplomatic profiles should be able to refuse auto-fit.

## Success criteria for a future marinaMoji command

- Uses **native** character formatting only (undoable; survives ODT).  
- Target expressed as **N cells** (and/or absolute width) relative to the Asian font size.  
- Remove restores prior Scale width / Spacing (or clears to defaults).  
- Refuses whole-paragraph abuse and nested warichū if unsafe (policy TBD after spike).  
- Does **not** claim Word `fitText` round-trip until DOCX import/export is tested.
