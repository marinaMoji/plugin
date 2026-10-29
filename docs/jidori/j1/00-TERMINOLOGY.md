# Stage J1 — Terminology (字取り vs neighbours)

**Sources:** [JLREQ §2.1.3](https://www.w3.org/TR/jlreq/#principles_of_arrangement_of_kanji_and_kana_characters), [JLREQ §3.7.3 Jidori Processing](https://www.w3.org/TR/jlreq/#jidori_processing); marinaMoji inventory C02; OOo Fit Text proposal (i90868).

| Term | Meaning | Relation to this feature |
|---|---|---|
| **字取り (jidori)** | Fit a *specified substring* to a length of **N full-width character cells** by adjusting **inter-character spacing** (JLREQ). | **This feature.** |
| **字間調整** | Generic adjustment of gaps between character frames. | Mechanism used by jidori expand. |
| **字幅調整** | Adjust character advance / apparent width (scale). | Secondary; used when compressing below solid set. |
| **アキ組** | Fixed extra space between frames (JLREQ §2.1.3). | Related pattern; not “fit to N” by itself. |
| **均等割付 / 均等割り** | Distribute across the **line measure** (head–end). | **Furiwake / Distributed** — roadmap #8, **not** jidori. |
| **振り分け (furiwake)** | Editorial divided layout; distinct from warichū. | Out of scope. |
| **縦中横** | Short horizontal run inside vertical text. | Separate tool (`CharRotation` + fit). |
| **割注** | Two-line combine annotation. | Separate tool; refuse overlap. |

## JLREQ core (normative intent)

1. Target length = **integer × full-width em** of the surrounding Asian size.  
2. Prefer **even spacing between characters** so the run’s sides meet that length.  
3. Do **not** open solid clusters (e.g. grouped numerals, Western runs treated as blocks).  
4. **One character:** no inter-gap — leave space after (start-aligned in the block).  
5. Jidori is **allocation of advance**, not optical ink-box tricks and not whole-line justify.

## marinaMoji product wording

> Approximate fit to **N** full-width character cells.

Do **not** claim Word `w:fitText` parity until DOCX is demonstrated.
