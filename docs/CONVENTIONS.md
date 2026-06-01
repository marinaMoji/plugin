# Typing conventions (for reliable formatting)

The extension parser assumes marks belong to the **kanji immediately before** the mark run in the text stream.

## Basic rule

Type base kanji, then one or more kaeriten shortcuts without spaces:

```
說 ;1 ;r   →   說㆒㆑
```

When the passage is stable, run **Format kaeriten** on the selection or paragraph (manual command — not automatic while typing).

## Compound kaeriten

A **contiguous run** of U+3190–U+319F immediately after one base character forms **one annotation cluster** attached to that character.

| Source | Meaning | One view stacks |
|--------|---------|-----------------|
| `說㆒㆑者` | 說 with 一二点 + レ | 一 / レ (top → bottom per typing order) |
| `說㆑者` | 說 with レ only | レ |

- Do **not** put spaces or other characters between marks in the same cluster.
- To mark two kanji, put marks after each: `…說㆑…者㆑…` → two clusters.

Stack order inside the frame/textbox follows **source order** (first typed mark = top or outer position per [mapping.json](../mapping.json) `stack_order`).

## Editing workflow

**Edit source, not the box.**

| Do this | Not this |
|---------|----------|
| Change `說㆒㆑者` in the document (or **Show source**) | Click inside the frame/textbox to “fix” kaeriten |
| **Format kaeriten** after drafting a section | Expect layout to update on every keypress (v1) |
| **Refresh rendering** after mark or font changes | Manually resize each annotation object |

Rendered frames (LibreOffice) and textboxes (Word) are **read-only views**. The plugin rebuilds them from Unicode source.

## Do

- Draft in **source form** (`說㆒㆑者`) with marinaMoji; run **Format kaeriten** when the sentence is stable.
- Use **Refresh rendering** after changing marks or paragraph font size.
- Use **Copy as plain text** when pasting into gedit, email, or OnlyOffice.
- Keep a `.txt` sidecar with Unicode marks for git if the ODT/DOCX hides marks after format.

## Avoid

- Putting ㆑ **before** the kanji it marks.
- Editing inside annotation frames/textboxes.
- Expecting normal copy/paste to preserve views outside the host app.
- Searching for `說者` when a view sits between 說 and 者 — search `說` or switch **Show source**.
- Mixing hand-typed subscript レ and Unicode ㆑ without re-formatting the paragraph.
- Relying on hidden document metadata instead of visible `㆒㆑` for meaning or export.

## Vertical vs horizontal

Test **縦書き** early; frame/textbox offset may need axis-specific tuning (see [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md)).

## Collaboration

- **Inside LibreOffice or Word (with extension):** formatted document for print/teaching.
- **Outside those apps:** canonical Unicode string (`說㆒㆑者`) — interoperable without the extension.
- Collaborators without marinaMoji can work on rendered files; scholars with marinaMoji should edit source marks, then **Refresh rendering**.

## Related

- [ARCHITECTURE.md](ARCHITECTURE.md) — source vs view; metadata policy
- [WORD_FINDINGS.md](WORD_FINDINGS.md) — Word textbox UX
