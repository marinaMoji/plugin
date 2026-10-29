# JLREQ / Unicode — kinsoku and punctuation requirements

**Spec consulted:** [Requirements for Japanese Text Layout (JLREQ)](https://www.w3.org/TR/jlreq/) — W3C WG Note 11 August 2020 (`https://www.w3.org/TR/2020/NOTE-jlreq-20200811/`).  
**Also:** [UAX #14 Unicode Line Breaking Algorithm](https://www.unicode.org/reports/tr14/).

Citations use JLREQ fragment ids (verified by fetching the TR on 2026-10-29). Character classes (`cl-NN`) are JLREQ’s.

## Layer distinction (do not conflate)

| Layer | Role |
|---|---|
| JLREQ | Describes Japanese book-composition conventions (largely JIS X 4051–based); not a programming API |
| UAX #14 | Unicode line-break classes / algorithm for general text; incomplete for JLREQ spacing/kinsoku tables |
| LibreOffice | Implements a **subset** via forbidden-character lists, hanging, autospace, compression options |
| Modern publishing | Often uses **relaxed** line-start rules (JLREQ notes this explicitly) |
| Scholarly / historical | May intentionally violate modern conventions |

## Core JLREQ topics for Stage E

### Line-start prohibition — 行頭禁則

- **Section:** [Characters Not Starting a Line](https://www.w3.org/TR/jlreq/#characters_not_starting_a_line)  
- **Principle (verified quote):** In principle, no line should begin with closing brackets (**cl-02**), hyphens (**cl-03**), dividing punctuation (**cl-04**), middle dots (**cl-05**), full stops (**cl-06**), commas (**cl-07**), iteration marks (**cl-09**), prolonged sound mark (**cl-10**), small kana (**cl-11**), or warichū closing brackets (**cl-29**).  
- **Documented relaxations (JLREQ Note):** many books allow 々 / ー / small kana at line start; some allow `・`; newspapers may allow `？` `！` because lines are short.

### Line-end prohibition — 行末禁則

- **Section:** [Characters Not Ending a Line](https://www.w3.org/TR/jlreq/#characters_not_ending_a_line)  
- **Principle:** No line should end with opening brackets (**cl-01**) or warichū opening brackets (**cl-28**).  
- **Term:** Avoiding these (and related unbreakable / inseparable constraints) is collectively **kinsokushori (禁則処理)**.

### Unbreakable sequences

- **Section:** [Unbreakable Character Sequences](https://www.w3.org/TR/jlreq/#unbreakable_character_sequences)  
- Certain character pairs must not be split; line-head/end wrap can be viewed as a special case of no-break between characters.

### Punctuation spacing — 約物のアキ

- **Section:** [Positioning of Punctuation Marks (Commas, Periods and Brackets)](https://www.w3.org/TR/jlreq/#positioning_of_punctuation_marks)  
- Full stops / commas / brackets / middle dots are treated as **half-em advance** with **added spacing** beside ideograph/kana so they often *appear* full-width.  
- Consecutive punctuation has special solid / half-em rules (aesthetic).  
- Mid-line spacing after full stops is generally **not** removed by compression; other half/quarter-em gaps **may** be reduced during line adjustment (JLREQ principle).  
- Details tabulated via character classes in **§3.9**-family material and appendix **B** ([About Character Classes](https://www.w3.org/TR/jlreq/#about_character_classes); [Spacing between Characters](https://www.w3.org/TR/jlreq/#spacing_between_characters)).

### Hanging punctuation — ぶら下げ組み

- Discussed with kihon-hanmen / line-end processing (JLREQ **Figure 38**: IDEOGRAPHIC COMMA / FULL STOP placed outside the hanmen).  
- Applies to **full stops (cl-06)** and **commas (cl-07)** when they would otherwise wrap to the next line head; they may sit past the line end against the hanmen edge.  
- JLREQ notes hanging is **not** defined in JIS X 4051 proper (JIS commentary 8.1 c) but is common in books.  
- **Do not confuse** hanging with ordinary kinsoku pull-back.

### Line adjustment — 行の調整処理

- **Section:** [Line Adjustment](https://www.w3.org/TR/jlreq/#line_adjustment)  
- Goals: keep line lengths aligned to kihon-hanmen (except last paragraph line).  
- Means: compress allowed gaps; expand allowed gaps; move break opportunities; hanging as a cost-reduction tactic.

### Vertical vs horizontal punctuation

- **Section family:** [Differences in Vertical and Horizontal Composition in Use of Punctuation Marks](https://www.w3.org/TR/jlreq/#differences_in_vertical_and_horizontal_composition_in_use_of_punctuation_marks)  
- Vertical prefers `。` `、`; horizontal may use several period/comma conventions.  
- Bracket glyph orientation vs letter-face position differs; small kana (**cl-11**) position in the frame differs by writing mode.  
- Font metric ≠ layout engine.

### Opening brackets at line head

- **§3.1.5** [Positioning of Opening Brackets at Line Head](https://www.w3.org/TR/jlreq/#positioning_of_opening_brackets_at_line_head) — several methods (full-width indent, tentsuki, etc.).

### Warichū (context only)

- Warichū brackets are **cl-28 / cl-29** — separate from ordinary brackets for spacing/kinsoku.  
- Inner warichū break should follow the same kinsoku spirit as body text (prior marinaMoji Stage B / C6). Writer’s combine path is a **separate** mechanism (see inventory / `02`).

## LibreOffice `ja_JP` lists vs JLREQ (mapping sketch)

| JLREQ idea | LO `ja_JP` default list |
|---|---|
| cl-06/07 not at line start | `、。` (and Western/fullwidth analogues) in begin list |
| cl-02 closing brackets | `〉》」』】〕` etc. in begin list |
| cl-11 small kana | Hiragana/katakana smalls + halfwidth smalls in begin list |
| cl-09/10 々 ー | In begin list (strict default; JLREQ notes many books relax) |
| cl-01 opening brackets not at line end | `〈《「『【〔` etc. in end list |
| Hanging cl-06/07 | `LineBreakHangingCharacters` = `、。，．` |

LO lists are **configurable** (Options / document `ForbiddenCharacters`) and are **not** a full JLREQ character-class table (spacing tables, inseparable pairs, warichū-specific cl-28/29 handling).

## Unicode UAX #14 (role)

- Provides `LB` classes and a default algorithm for where breaks are **allowed**.  
- Does **not** encode JLREQ half-em spacing tables, hanging, or book-vs-newspaper strictness levels.  
- Writer’s CJK path applies forbidden/hanging **on top of** ICU breaks (`BreakIterator_CJK::getLineBreak`).  
- Useful as a secondary reference for mixed-script runs; **insufficient** alone for Japanese scholarly composition diagnostics.

## Implications for marinaMoji

1. Prefer **convention profiles** (strict JLREQ / relaxed book / newspaper / diplomatic) over a single “correct” list.  
2. Treat JLREQ relaxations as first-class—not as Writer bugs.  
3. Separate **textual** issues (mixed half/full-width punct; explicit break before closing punct) from **layout** issues (rendered line head holds `。`).  
4. Warichū-internal diagnostics remain advisory heuristics unless/until upstream U2 exists.
