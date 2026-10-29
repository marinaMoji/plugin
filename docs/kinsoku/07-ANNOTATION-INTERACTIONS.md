# Annotation interactions — ruby, warichū, emphasis, tate-chū-yoko

**Constraint:** do not modify existing feature implementations. Reuse prior corpora.

## Ruby

| Question | Working answer | Confidence |
|---|---|---|
| Body kinsoku still applies around ruby bases? | Yes for ordinary paragraph breaks; ruby is multiportion layout | Hypothesis → Pending K11 |
| Hanging inside ruby multiportion? | **Disabled** (`!IsMulti()` in `guess.cxx`) | Confirmed source |
| Group ruby split across lines? | Host-dependent; JLREQ allows complex cases | Prior ruby docs; not re-litigated here |
| Diagnostic | Prefer textual adjacency checks; avoid claiming ruby “line head” without geometry | |

## Warichū

Reuse Stage B B11 / B19 / B20 and [`../warichû/upstream/18-KINSOKU-NOTES.md`](../warichû/upstream/18-KINSOKU-NOTES.md).

| Question | Answer | Confidence |
|---|---|---|
| Same ICU / forbidden-list path as body? | **Partially yes** — `BuildMultiPortion` → `BuildPortions` → `SwTextGuess::Guess` → `getLineBreak` with document lists when forbidden rules are on ([source report](190ad1df-601b-474c-b576-18ca1a274421)) | Confirmed |
| Why B11/B19/B20 still fail? | Width-driven inner fill + **`IsFirstMulti`** cut rules; **no post-pass** forbidding not-start at head of inner line 2; hanging **off** (`IsMulti`) | Confirmed |
| Do paragraph toggles alone “fix” inner breaks? | **No guarantee** — engine shared, warichū-specific post-filter absent | Confirmed Stage B |
| Detectable via UNO? | Combine flag yes; **inner break index no** | Confirmed |
| Diagnostic type | Advisory `WARICHU_INTERNAL_BREAK` heuristic (text pattern / known fixtures), not confirmed layout defect API | |

Do **not** file upstream U2 without approval. Do **not** patch LO.

## Emphasis marks

| Question | Plan |
|---|---|
| Affect line height / column width? | Corpus K13 ± emphasis on identical string |
| Affect kinsoku decisions? | Unlikely (character formatting); verify no break change |
| Action if regression | Document only unless formatting broken |

## Tate-chū-yoko

| Question | Plan |
|---|---|
| Combined run indivisible at wrap? | Expected for combine; corpus K12 (`12。`, `「12`) |
| Interaction with forbidden start/end | Combined digits + punct near measure edge |
| Action | Do not change `tatechuyoko.py` |

## Diagnostic labelling rule

Every finding that involves annotations must name the **mechanism**:

- `body_line_break` vs `warichu_internal` vs `ruby_multiportion` vs `tate_combine`.
