# Design summary for LibreOffice maintainers  
## Optional Advanced Warichū Layout (manual division only)

**Status:** Draft for our internal discussion → later mailing-list post.  
**Do not submit upstream until we agree on wording and timing.**  
**Full sketch:** [`19-SCHOLARLY-WARICHU-PROPOSAL.md`](19-SCHOLARLY-WARICHU-PROPOSAL.md)

---

### Problem

Writer’s Asian double-line / `text-combine="lines"` layout (warichū) always chooses the internal break automatically. For critical editions, an editor may need a **stable, intentional** break between the two annotation lines without rewriting the annotation string (no spaces, no split fields).

### Proposal (high level)

Keep today’s behaviour as the **default**.

Add an **optional** “Advanced Warichū Layout” capability whose first feature is a **manual division index** on the existing two-line character attribute (`SvxTwoLinesItem`), exposed via UNO (e.g. `CharCombineBreak`, default `-1` = automatic).

marinaMoji would offer this only under a **Scholarly / Historical Composition** preset; ordinary users never see it.

### Compatibility

| Concern | Approach |
|---|---|
| Existing documents | Unchanged (break unset → current algorithm) |
| Older LibreOffice | Ignore unknown ODF attribute → automatic layout; text intact |
| ODF | Prefer standardized attribute after discussion, or temporary `loext:` with documented ignore-on-unknown |
| DOCX | `w:eastAsianLayout` has no break index → export/import as automatic combine |
| Editing | Break index must move with inserts/deletes (bookmark-like); invalid index → clamp or fall back to auto |

### Renderer

In `BuildMultiPortion`’s double-line path only: if break ≥ 0, honour it; else keep width-search. No change to default 50% scaling in this proposal. **No** replacement of the current defaults.

### What we are not asking for (in this step)

- Making scholarly mode the default  
- Alignment-mode or font-size APIs as prerequisites  
- A marinaMoji-specific fork of Writer  

### Ask for maintainers (when we post)

Is an optional break index on `SvxTwoLinesItem` + ODF/`loext` persistence acceptable in principle? Should ODF standardization precede any LO-namespace experiment?
