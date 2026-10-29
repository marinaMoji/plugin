# Stage J1 report — Native feasibility

**Date:** 2026-10-29  
**Toolbar:** not implemented (per brief).

## Answers so far

### 1. Can Writer compose across N cells without unacceptable distortion?

**Yes for horizontal Japanese expand**, using **Spacing (`CharKerning`)** — JLREQ-aligned; live match at 10.5 pt (~10 pt ≈ 1 em/gap).

**Yes for horizontal compress**, using **Scale width (`CharScaleWidth`)** (~55–60% for 5→3). Mild metric drift vs pure em math; acceptable as approximation.

**Spacing alone does not suffice for strong shrink**; combined policy (A expand / B shrink) matches OOo Fit Text and live results.

### 2. Horizontal and vertical?

**Horizontal:** expand (Spacing) + compress (Scale) validated.  
**Vertical:** **expand Pass** (Spacing). **Compress Fail** — Scale width 60% at 9 pt thins glyphs and shoves the run to the line head (`03-VERTICAL-GATE.md`).  

**MVP scope:** full expand in H+V; compress **horizontal only**; refuse vertical compress with an explicit message.

### 3. Remove without destroying prior formatting?

**Not solved in J1.** Existing marinaMoji Remove tools clear *feature* props (combine, ruby text, rotation, emphasis). They do **not** restore arbitrary prior scale/spacing.

Jidori **cannot** use “reset to 100% / 0” as Remove — that would erase user formatting. **Stage J2** must prove a reversible identity + restore path (or stop).

## Mechanism choice (after V gate)

| Situation | Channel |
|---|---|
| Expand N > n ≥ 2 (H or V) | `CharKerning` only |
| Shrink N < n (horizontal) | `CharScaleWidth` only |
| Shrink N < n (vertical) | **Refuse** (Scale distorts / shoves) |
| N = n | noop |
| n = 1, N > 1 | refuse (JLREQ trailing space; Writer gap model weak) |
| Latin / mixed | refuse MVP |

## UNO unit correction

`CharKerning` is **twips** (×20 from pt), not “pt×100”. Spike formula updated accordingly.

## Stop conditions before J3/J4

1. ~~Vertical smoke~~ → scoped (expand OK; shrink V refused).  
2. Stage J2 cannot identify marinaMoji jidori after ODT reopen and restore prior scale/spacing.
