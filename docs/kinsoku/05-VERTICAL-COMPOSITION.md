# Vertical composition — punctuation and kinsoku

**Status:** requirements + LO mechanism notes; dedicated vertical corpus (K09) **Pending**.

## JLREQ expectations

- Vertical Japanese typically uses `。` `、` ([differences in vertical and horizontal composition](https://www.w3.org/TR/jlreq/#differences_in_vertical_and_horizontal_composition_in_use_of_punctuation_marks)).
- Bracket letter-faces rotate with writing mode; small kana sit differently in the character frame.
- Kinsoku principles (not-start / not-end) apply in both writing modes; hanging still targets commas/periods at the “line end” (bottom of a vertical line in common description).

## LibreOffice behaviour (mechanism)

- Paragraph Asian toggles are **not** split H/V in UI or UNO.
- `BreakIterator_CJK` works on Unicode string indices; writing mode is applied later in frame layout.
- Font vertical metrics and `TextWritingMode` affect glyph orientation independently of forbidden lists.
- Document grid (`style:layout-grid-*`) changes alignment geometry; whether it changes kinsoku decisions needs corpus (K10).

## What Stage E1 must still observe

1. Hanging with `ParaIsHangingPunctuation` on a vertical page style.  
2. Forbidden begin/end with narrow vertical measure (automatic breaks only).  
3. Same paragraph toggled H vs V — compare ODF + screenshots, not rotated bitmaps.  
4. Grid on/off for one hanging and one forbidden-start case.

## Fonts

Record Mincho and Gothic substitutions. Attribute orientation quirks to the font before blaming Writer.
