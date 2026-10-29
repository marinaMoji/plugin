# -*- coding: utf-8 -*-
"""
Native ruby (振り仮名 / phonetic guide) for LibreOffice Writer.

Phase 3:
  - Apply group-ruby on the selected base text (reading via dialog).
  - Remove ruby from selection or caret-inside ruby span.
  - Preserve base characters exactly; only clear/set Ruby* properties.
  - Default RubyAdjust: LEFT (ODF left) — same as Writer’s native SvxRubyItem
    default. Stretch modes (INDENT_BLOCK / BLOCK) can corrupt adjacent vertical
    warichū multiportions in current LibreOffice; LEFT keeps coexistence stable
    (user-confirmed “baseline” / start alignment). Fig.124/125 remain available
    as internal alternatives for future advanced controls.
  - RubyPosition ABOVE (right side in vertical writing).
  - Refuses apply when the selection already has CharCombineIsOn (warichū).
  - No jukugo auto-split; no size/font UI yet (host/char-style owns metrics).

Does not replace kaeriten rendering. Prefer adjacent spans, not nested ruby⊂warichū.
"""

from __future__ import annotations

# com.sun.star.text.RubyAdjust
_RUBY_ADJUST_LEFT = 0  # native LO default; stable beside warichū
_RUBY_ADJUST_CENTER = 1
_RUBY_ADJUST_RIGHT = 2
_RUBY_ADJUST_BLOCK = 3  # Fig.125 / distribute-letter — future controls
_RUBY_ADJUST_INDENT_BLOCK = 4  # Fig.124 / distribute-space — future controls
# Product default: coexistence with warichū over Fig.124 stretch (for now).
_RUBY_ADJUST_DEFAULT = _RUBY_ADJUST_LEFT
# com.sun.star.text.RubyPosition (LO 6.1+)
_RUBY_POSITION_ABOVE = 0
# com.sun.star.text.ParagraphVertAlign — Paragraph dialog → Alignment →
# Text-to-text → Base line (user-confirmed; helps ruby/warichū layout).
_PARA_VERT_BASELINE = 1


def _adjust_for_base(base):
    """RubyAdjust for apply. Currently LEFT for all bases (LO-native / warichū-safe).

    INDENT_BLOCK / BLOCK / CENTER remain module constants for a future UI.
    ``base`` is accepted for API stability with callers.
    """
    return _RUBY_ADJUST_DEFAULT


def _ensure_para_text_to_text_baseline(text, selection):
    """Set paragraph Text-to-text alignment to Base line (ParaVertAlignment).

    Does not change RubyAdjust. Uses a *separate* paragraph cursor so the
    caller's selection/range cursor is not expanded.
    """
    try:
        para = text.createTextCursorByRange(selection.getStart())
        para.gotoStartOfParagraph(False)
        para.gotoEndOfParagraph(True)
        _set(para, "ParaVertAlignment", _PARA_VERT_BASELINE)
    except Exception:
        pass


def _get_document():
    try:
        doc = XSCRIPTCONTEXT.getDocument()  # noqa: F821
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


def _text_of(doc, text_range):
    """XText that contains text_range (table cell, footnote, frame, header…).

    ``doc.Text`` is the body text only; a cursor made from it cannot cover a
    range that lives in another text.
    """
    try:
        text = text_range.getText()
        if text is not None:
            return text
    except Exception:
        pass
    return doc.Text


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
    text = _text_of(doc, first)
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


def _ruby_text_of(cursor):
    val = _get(cursor, "RubyText", "")
    if val is None:
        return ""
    if isinstance(val, dict) and "error" in val:
        return ""
    return str(val)


def selection_has_ruby(selection):
    return bool(_ruby_text_of(selection))


def expand_ruby_span_indices(flags, index):
    """Pure helper: flags[i] True means character i has non-empty RubyText.

    Same caret rules as warichū expand_combine_span_indices.
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


def text_unchanged_after_ruby_change(before, after):
    return before == after


def _anchor_inside_ruby(text, text_range):
    cursor = text.createTextCursorByRange(text_range.getStart())
    cursor.collapseToStart()

    right = text.createTextCursorByRange(cursor.getStart())
    if right.goRight(1, True) and _ruby_text_of(right):
        right.collapseToStart()
        return right

    left = text.createTextCursorByRange(cursor.getStart())
    if left.goLeft(1, True) and _ruby_text_of(left):
        left.collapseToStart()
        return left

    if not _is_collapsed(text_range) and selection_has_ruby(text_range):
        mid = text.createTextCursorByRange(text_range.getStart())
        mid.collapseToStart()
        return mid
    return None


def expand_to_ruby_span(text, text_range):
    """Expand to contiguous non-empty RubyText run."""
    if text_range is None:
        return None
    anchor = _anchor_inside_ruby(text, text_range)
    if anchor is None:
        return None

    start = text.createTextCursorByRange(anchor.getStart())
    start.collapseToStart()
    while True:
        probe = text.createTextCursorByRange(start.getStart())
        if not probe.goLeft(1, False):
            break
        check = text.createTextCursorByRange(probe.getStart())
        if not check.goRight(1, True) or not _ruby_text_of(check):
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
        if not check.goRight(1, True) or not _ruby_text_of(check):
            break
        included += 1
    if included == 0:
        return None
    span.goRight(included, True)
    return span


def _clear_ruby(cursor):
    _set(cursor, "RubyText", "")
    # Leave adjust/position alone after clear; empty RubyText removes the guide.


def _selection_has_tate(cursor):
    try:
        rot = int(_get(cursor, "CharRotation", 0) or 0)
    except (TypeError, ValueError):
        rot = 0
    return rot == 900 and _get(cursor, "CharRotationIsFitToLine", False) is True


def _selection_has_warichu(cursor):
    return _get(cursor, "CharCombineIsOn", False) is True


def _apply_ruby(cursor, reading, adjust=_RUBY_ADJUST_DEFAULT):
    # Never nest under warichū combine on the same characters.
    _set(cursor, "CharCombineIsOn", False)
    _set(cursor, "CharCombinePrefix", "")
    _set(cursor, "CharCombineSuffix", "")
    ok = _set(cursor, "RubyText", reading)
    # Set alignment after text so Writer associates it with the ruby attr.
    _set(cursor, "RubyAdjust", int(adjust))
    # ABOVE = above in horizontal, right side in vertical (JLREQ conventional).
    _set(cursor, "RubyPosition", _RUBY_POSITION_ABOVE)
    # Re-assert adjust (some LO paths reset defaults when RubyText is first set).
    _set(cursor, "RubyAdjust", int(adjust))
    return ok


def _ask_ruby_reading(doc, default=""):
    """Modal dialog: reading string. Returns None if cancelled."""
    import uno

    try:
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        dialog_model = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControlDialogModel", ctx
        )
        dialog_model.Title = "marinaMoji ruby"
        dialog_model.Width = 180
        dialog_model.Height = 70
        dialog_model.Closeable = True

        def _insert(name, service, **props):
            m = dialog_model.createInstance(
                "com.sun.star.awt.UnoControl%sModel" % service
            )
            m.Name = name
            for k, v in props.items():
                setattr(m, k, v)
            dialog_model.insertByName(name, m)

        _insert(
            "lbl",
            "FixedText",
            PositionX=10,
            PositionY=8,
            Width=160,
            Height=12,
            Label="Ruby reading (振り仮名) for the selection:",
        )
        _insert(
            "edit",
            "Edit",
            PositionX=10,
            PositionY=24,
            Width=160,
            Height=14,
            Text=default or "",
        )
        _insert(
            "ok",
            "Button",
            PositionX=70,
            PositionY=46,
            Width=45,
            Height=14,
            Label="OK",
            PushButtonType=1,
            DefaultButton=True,
        )
        _insert(
            "cancel",
            "Button",
            PositionX=120,
            PositionY=46,
            Width=45,
            Height=14,
            Label="Cancel",
            PushButtonType=2,
        )

        control = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControlDialog", ctx
        )
        control.setModel(dialog_model)
        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
        control.createPeer(toolkit, None)
        control.setVisible(True)
        try:
            control.getControl("edit").setFocus()
        except Exception:
            pass
        result = control.execute()
        text = ""
        try:
            text = dialog_model.getByName("edit").Text
        except Exception:
            text = ""
        control.dispose()
        if result != 1:
            return None
        text = (text or "").strip()
        return text if text else None
    except Exception as exc:
        _message(
            doc,
            "marinaMoji ruby",
            "Could not open the ruby dialog (%s).\n"
            "Select the base text and try again." % type(exc).__name__,
            kind="error",
        )
        return None


def apply_ruby(*_args):
    """Toolbar: apply group-ruby to the current selection."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    selection = _get_selection_range(doc, allow_collapsed=False)
    if selection is None:
        _message(
            doc,
            "marinaMoji ruby",
            "Select the base text that should receive a ruby reading.",
            kind="info",
        )
        return

    base = _range_text(selection)
    if not base.strip():
        _message(
            doc,
            "marinaMoji ruby",
            "The selection is empty.",
            kind="info",
        )
        return

    text = _text_of(doc, selection)
    cursor = text.createTextCursorByRange(selection)
    if _selection_has_warichu(cursor):
        _message(
            doc,
            "marinaMoji ruby",
            "This selection is warichū (combined). "
            "Remove warichū first, or apply ruby to a separate base span.\n\n"
            "Nesting ruby inside warichū is unreliable in Writer.",
            kind="warning",
        )
        return

    if _selection_has_tate(cursor):
        _message(
            doc,
            "marinaMoji ruby",
            "This selection is tate-chū-yoko. Remove it first, or apply ruby "
            "to a separate base span.",
            kind="warning",
        )
        return
    if "\n" in base or "\r" in base:
        _message(
            doc,
            "marinaMoji ruby",
            "A ruby reading belongs to one base run. "
            "Select text within a single paragraph.",
            kind="warning",
        )
        return

    reading = _ask_ruby_reading(doc, default="")
    if reading is None:
        return

    before = _range_text(cursor)
    adjust = _adjust_for_base(before)
    if not _apply_ruby(cursor, reading, adjust):
        _message(
            doc,
            "marinaMoji ruby",
            "Could not set RubyText on this selection.\n"
            "Enable Asian language support if it is off.",
            kind="error",
        )
        return
    # Paragraph Text-to-text → Base line (not RubyAdjust). Stabilises layout
    # beside warichū; ruby should then sit in the line gap under fixed pitch.
    _ensure_para_text_to_text_baseline(text, cursor)
    after = _range_text(cursor)
    if after != before:
        _message(
            doc,
            "marinaMoji ruby",
            "Apply changed the underlying base text unexpectedly. "
            "Please undo and report this.",
            kind="error",
        )
        return
    try:
        doc.getCurrentController().select(cursor)
    except Exception:
        pass


def remove_ruby(*_args):
    """Toolbar: remove ruby from selection or caret-inside ruby span."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    selection = _get_selection_range(doc, allow_collapsed=True)
    if selection is None:
        _message(
            doc,
            "marinaMoji ruby",
            "Place the cursor inside ruby text, or select it, then remove.",
            kind="info",
        )
        return

    text = _text_of(doc, selection)
    span = expand_to_ruby_span(text, selection)
    if span is None:
        if not _is_collapsed(selection) and selection_has_ruby(selection):
            span = text.createTextCursorByRange(selection)
        else:
            _message(
                doc,
                "marinaMoji ruby",
                "No ruby found at the cursor.",
                kind="info",
            )
            return

    before = _range_text(span)
    _clear_ruby(span)
    after = _range_text(span)
    if after != before:
        _message(
            doc,
            "marinaMoji ruby",
            "Remove changed the underlying base text unexpectedly. "
            "Please undo and report this.",
            kind="error",
        )
        return
    try:
        doc.getCurrentController().select(span)
    except Exception:
        pass
