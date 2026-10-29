# -*- coding: utf-8 -*-
"""
Native warichū (割注) for LibreOffice Writer — character-span CharCombine.

Gate 1 recipe (Writer 26.8 evidence):
  - Apply CharCombineIsOn on the *selected note* only (creates a text span).
  - Never set CharCombinePrefix / CharCombineSuffix (UNO brackets break paint).
  - Never leave combine on the whole paragraph (paints badly).
  - Clear sticky combine on surrounding runs when needed.

Toolbar: Apply warichū / Remove warichū.
Remove is caret-aware: a collapsed cursor inside a combine span clears the whole span.
"""

from __future__ import annotations


def _get_document():
    try:
        doc = XSCRIPTCONTEXT.getDocument()  # noqa: F821 — macro / protocol context
        if doc is not None and hasattr(doc, "Text"):
            return doc
    except NameError:
        pass
    import uno

    ctx = uno.getComponentContext()
    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )
    doc = desktop.getCurrentComponent()
    if doc is None or not hasattr(doc, "Text"):
        raise RuntimeError("Open a Writer document first.")
    return doc


def _range_text(text_range):
    if text_range is None:
        return ""
    try:
        return text_range.getString()
    except AttributeError:
        return ""


def _is_collapsed(text_range):
    if text_range is None:
        return True
    try:
        if hasattr(text_range, "isCollapsed"):
            return bool(text_range.isCollapsed())
    except Exception:
        pass
    return len(_range_text(text_range)) == 0


def _get_selection_range(doc, *, allow_collapsed=False):
    """Writer selection is XIndexAccess of XTextRange(s), not always a single range.

    When allow_collapsed is True, a caret (empty selection) is returned so callers
    can expand to a surrounding warichū span.
    """
    controller = doc.getCurrentController()
    if controller is None:
        return None
    sel = controller.getSelection()
    if sel is None:
        return None
    if hasattr(sel, "getString"):
        if len(_range_text(sel)) == 0 and not allow_collapsed:
            return None
        return sel
    try:
        count = sel.getCount()
    except AttributeError:
        return None
    if count < 1:
        return None
    first = sel.getByIndex(0)
    if count == 1:
        if len(_range_text(first)) == 0 and not allow_collapsed:
            return None
        return first
    last = sel.getByIndex(count - 1)
    text = doc.Text
    merged = text.createTextCursorByRange(first.getStart())
    merged.gotoRange(last.getEnd(), True)
    if len(_range_text(merged)) == 0 and not allow_collapsed:
        return None
    return merged


def _message(doc, title, text, kind="warning"):
    try:
        from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
        from com.sun.star.awt.MessageBoxType import ERRORBOX, INFOBOX, WARNINGBOX

        box_type = {"info": INFOBOX, "error": ERRORBOX}.get(kind, WARNINGBOX)
        frame = doc.getCurrentController().getFrame()
        window = frame.getContainerWindow()
        toolkit = window.getToolkit()
        box = toolkit.createMessageBox(window, box_type, BUTTONS_OK, title, text)
        box.execute()
    except Exception:
        pass


def _set(cursor, name, value):
    try:
        cursor.setPropertyValue(name, value)
        return True
    except Exception:
        return False


def _get(cursor, name, default=None):
    try:
        return cursor.getPropertyValue(name)
    except Exception:
        return default


def _combine_on(cursor):
    return _get(cursor, "CharCombineIsOn", False) is True


def _paragraph_cursor_covering(text, text_range):
    """Cursor selecting the full paragraph that contains text_range's start."""
    para = text.createTextCursorByRange(text_range.getStart())
    para.gotoStartOfParagraph(False)
    para.gotoEndOfParagraph(True)
    return para


def selection_covers_whole_paragraph_text(sel_text, para_text):
    """Pure helper: True if sel_text is the entire paragraph string (testable)."""
    if not sel_text or not para_text:
        return False
    if sel_text == para_text:
        return True
    sel_s = sel_text.strip("\r\n")
    para_s = para_text.strip("\r\n")
    return bool(sel_s) and sel_s == para_s


def _selection_is_whole_paragraph(text, selection):
    """True if selection is the entire paragraph (combine would become paragraph-level)."""
    sel = _range_text(selection)
    if not sel:
        return False
    para = _paragraph_cursor_covering(text, selection)
    return selection_covers_whole_paragraph_text(sel, _range_text(para))


def _clear_combine(cursor):
    """Turn warichū off; also clear UNO bracket props if present."""
    _set(cursor, "CharCombineIsOn", False)
    # Clearing empty brackets is safe on remove; do not set them on apply.
    _set(cursor, "CharCombinePrefix", "")
    _set(cursor, "CharCombineSuffix", "")


def _selection_has_ruby(cursor):
    val = _get(cursor, "RubyText", "")
    if val is None:
        return False
    if isinstance(val, dict) and "error" in val:
        return False
    return bool(str(val))


def _apply_combine(cursor):
    """Bare CharCombineIsOn only — never Prefix/Suffix.

    Do **not** set RubyText="" here. Clearing ruby on a span that never had a
    reading still attaches an empty text:ruby wrapper in Writer, which can
    suppress text-combine=lines painting. Nesting is refused before apply when
    RubyText is non-empty.
    """
    return _set(cursor, "CharCombineIsOn", True)


def selection_has_warichu(selection):
    """True if the selection (or its start) reports CharCombineIsOn."""
    if selection is None:
        return False
    flag = _get(selection, "CharCombineIsOn", False)
    return flag is True


def expand_combine_span_indices(flags, index):
    """Pure helper: given per-character CharCombineIsOn flags and a caret/index,
    return (start, end) half-open span covering the contiguous True run, or None.

    index may be len(flags) (caret after last character); then the character to
    the left is used if it is combined.
    """
    n = len(flags)
    if n == 0:
        return None
    if index < 0 or index > n:
        return None
    pos = index
    if pos == n:
        pos = n - 1
    elif pos < n and not flags[pos]:
        # Caret between characters: prefer the character to the left if combined,
        # else the character to the right.
        if pos > 0 and flags[pos - 1]:
            pos = pos - 1
        elif not flags[pos]:
            return None
    if not flags[pos]:
        return None
    start = pos
    while start > 0 and flags[start - 1]:
        start -= 1
    end = pos + 1
    while end < n and flags[end]:
        end += 1
    return (start, end)


def text_unchanged_after_clear(before, after):
    """Pure helper: removal must not alter characters."""
    return before == after


def _anchor_inside_combine(text, text_range):
    """Return a collapsed cursor on a character that has CharCombineIsOn, or None."""
    cursor = text.createTextCursorByRange(text_range.getStart())
    cursor.collapseToStart()

    # Prefer character to the right of the caret (typical insertion point).
    right = text.createTextCursorByRange(cursor.getStart())
    if right.goRight(1, True) and _combine_on(right):
        right.collapseToStart()
        return right

    # Else character to the left.
    left = text.createTextCursorByRange(cursor.getStart())
    if left.goLeft(1, True) and _combine_on(left):
        left.collapseToStart()
        return left

    # Non-collapsed selection may already sit on a combine run.
    if not _is_collapsed(text_range) and _combine_on(text_range):
        mid = text.createTextCursorByRange(text_range.getStart())
        mid.collapseToStart()
        return mid

    return None


def expand_to_warichu_span(text, text_range):
    """Expand text_range to the contiguous CharCombineIsOn character run.

    Returns an XTextCursor covering the span, or None if not inside warichū.
    """
    if text_range is None:
        return None

    # Still expand a partial selection so Remove clears the whole annotation.
    anchor = _anchor_inside_combine(text, text_range)
    if anchor is None:
        return None

    start = text.createTextCursorByRange(anchor.getStart())
    start.collapseToStart()
    while True:
        probe = text.createTextCursorByRange(start.getStart())
        if not probe.goLeft(1, False):
            break
        check = text.createTextCursorByRange(probe.getStart())
        if not check.goRight(1, True) or not _combine_on(check):
            break
        start.gotoRange(probe.getStart(), False)
        start.collapseToStart()

    span = text.createTextCursorByRange(start.getStart())
    span.collapseToStart()
    included = 0
    while True:
        check = text.createTextCursorByRange(start.getStart())
        if included:
            check.goRight(included, False)
        if not check.goRight(1, True) or not _combine_on(check):
            break
        included += 1
    if included == 0:
        return None
    span.goRight(included, True)
    return span


def apply_warichu(*_args):
    """Toolbar: format the current selection as native warichū (two-line span)."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    selection = _get_selection_range(doc, allow_collapsed=False)
    if selection is None:
        _message(
            doc,
            "marinaMoji warichū",
            "Select the annotation text to format as warichū "
            "(leave some body text outside the selection).",
            kind="info",
        )
        return
    text = doc.Text
    if _selection_is_whole_paragraph(text, selection):
        _message(
            doc,
            "marinaMoji warichū",
            "The whole paragraph is selected. Warichū must be a character span "
            "inside the paragraph (for example: 本文 + selected note).\n\n"
            "Select only the note text, then try again.",
            kind="warning",
        )
        return

    # Work on a cursor over the selection so property changes stick to a span.
    cursor = text.createTextCursorByRange(selection)
    if _selection_has_ruby(cursor):
        _message(
            doc,
            "marinaMoji warichū",
            "This selection already has ruby. "
            "Remove ruby first, or apply warichū to a separate note span.\n\n"
            "Nesting warichū on ruby base characters is unreliable in Writer.",
            kind="warning",
        )
        return
    before = _range_text(cursor)
    if not _apply_combine(cursor):
        _message(
            doc,
            "marinaMoji warichū",
            "Could not set CharCombineIsOn on this selection.",
            kind="error",
        )
        return
    after = _range_text(cursor)
    if after != before:
        # Should never happen; surface loudly if the host rewrites text.
        _message(
            doc,
            "marinaMoji warichū",
            "Apply changed the underlying text unexpectedly. "
            "Please undo and report this.",
            kind="error",
        )
        return
    # Re-select the span for feedback
    try:
        doc.getCurrentController().select(cursor)
    except Exception:
        pass


def remove_warichu(*_args):
    """Toolbar: remove native warichū from the selection or caret-inside span."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    selection = _get_selection_range(doc, allow_collapsed=True)
    if selection is None:
        _message(
            doc,
            "marinaMoji warichū",
            "Place the cursor inside a warichū annotation, or select it, "
            "then remove.",
            kind="info",
        )
        return

    text = doc.Text
    span = expand_to_warichu_span(text, selection)
    if span is None:
        # Fallback: non-empty selection that already reports combine
        if not _is_collapsed(selection) and selection_has_warichu(selection):
            span = text.createTextCursorByRange(selection)
        else:
            _message(
                doc,
                "marinaMoji warichū",
                "No warichū formatting found at the cursor. "
                "Click inside a two-line annotation, or select it.",
                kind="info",
            )
            return

    before = _range_text(span)
    _clear_combine(span)
    after = _range_text(span)
    if after != before:
        _message(
            doc,
            "marinaMoji warichū",
            "Remove changed the underlying text unexpectedly. "
            "Please undo and report this.",
            kind="error",
        )
        return
    try:
        doc.getCurrentController().select(span)
    except Exception:
        pass
