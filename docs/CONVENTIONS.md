# Typing conventions (for reliable formatting)

The extension parser assumes marks belong to the **kanji immediately before** the mark run in the text stream.

## Basic rule

Type base kanji, then one or more kaeriten shortcuts without spaces:

```
說 ;1 ;r   →   說㆒㆑
```

Then run **Render kaeriten** on the selection or paragraph.

## Compound kaeriten

A **contiguous run** of U+3190–U+319F immediately after one base character forms **one annotation cluster** attached to that character.

| Source | Meaning | One frame stacks |
|--------|---------|------------------|
| `說㆒㆑者` | 說 with 一二点 + レ | 一 / レ (top → bottom per typing order) |
| `說㆑者` | 說 with レ only | レ |

- Do **not** put spaces or other characters between marks in the same cluster.
- To mark two kanji, put marks after each: `…說㆑…者㆑…` → two clusters.

Stack order inside the frame follows **source order** (first typed mark = top or outer position per [mapping.json](../mapping.json) `stack_order`).

## Do

- Draft in **source form** (`說㆒㆑者`) when editing with marinaMoji; render when the sentence is stable.
- Use **Refresh rendering** after changing marks or paragraph font size.
- Use **Copy as plain text** when pasting into gedit, email, or OnlyOffice.
- Keep a `.txt` sidecar with Unicode marks for git if the ODT hides marks after render.

## Avoid

- Putting ㆑ **before** the kanji it marks.
- Expecting normal copy/paste to preserve frames outside LibreOffice.
- Searching for `說者` when a frame sits between 說 and 者 — search `說` or switch **Show source**.
- Mixing hand-typed subscript レ and Unicode ㆑ without re-rendering the paragraph.

## Vertical vs horizontal

Test **縦書き** early; frame offset may need axis-specific tuning (see [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md)).

## Collaboration

- **Inside LibreOffice:** rendered document for print/teaching.
- **Outside LibreOffice:** canonical Unicode string (`說㆒㆑者`) — interoperable without the extension.
- Collaborators without marinaMoji can edit rendered ODT; scholars with marinaMoji can edit source marks then refresh.
