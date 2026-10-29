# -*- coding: utf-8 -*-
"""
Native emphasis marks (圏点・傍点) for LibreOffice Writer.

Semantic style ids (host-independent) map to CharEmphasis / FontEmphasis.
Document default lives in typography_prefs (ODT UserDefinedProperties).
Passage formatting is ordinary CharEmphasis — independent of the default.

Toolbar:
  - Apply emphasis → document default on the selection
  - Emphasis menu → pick a mark / remove / set default
"""

from __future__ import annotations

try:
    import typography_prefs as _prefs
except ImportError:
    _prefs = None

# com.sun.star.text.FontEmphasis
_EMPHASIS_NONE = 0
_EMPHASIS_DOT_ABOVE = 1
_EMPHASIS_CIRCLE_ABOVE = 2
_EMPHASIS_DISK_ABOVE = 3
_EMPHASIS_ACCENT_ABOVE = 4

# Semantic → UNO (ABOVE = above H / right V)
_STYLE_TO_UNO = {
    "BLACK_SESAME": _EMPHASIS_ACCENT_ABOVE,  # ODF accent — labeled 黒ゴマ
    "BLACK_DOT": _EMPHASIS_DISK_ABOVE,  # ODF disc — 黒丸
    "WHITE_CIRCLE": _EMPHASIS_CIRCLE_ABOVE,  # ODF circle — 白丸
    "DOT": _EMPHASIS_DOT_ABOVE,  # ODF dot — 点 (not sesame)
}

_UNO_TO_STYLE = {v: k for k, v in _STYLE_TO_UNO.items()}

# Menu / dialog labels: (style_id, preview, en, ja, fr)
_STYLE_LABELS = (
    ("BLACK_SESAME", "﹅", "Black sesame", "黒ゴマ", "Points sésame noirs"),
    ("BLACK_DOT", "•", "Filled disc", "黒丸", "Disque plein"),
    ("WHITE_CIRCLE", "◦", "Open circle", "白丸", "Cercle vide"),
    ("DOT", "・", "Dot", "点", "Point"),
)

_BUILTIN_DEFAULT = "BLACK_SESAME"


def style_ids():
    return tuple(s[0] for s in _STYLE_LABELS)


def style_to_uno(style_id):
    if _prefs is not None:
        style_id = _prefs.normalize_emphasis_style_id(style_id) or style_id
    return _STYLE_TO_UNO.get(style_id)


def uno_to_style(value):
    try:
        code = int(value)
    except (TypeError, ValueError):
        return None
    if code == _EMPHASIS_NONE:
        return None
    return _UNO_TO_STYLE.get(code)


def label_for_style(style_id, lang="en"):
    for sid, preview, en, ja, fr in _STYLE_LABELS:
        if sid == style_id:
            if lang.startswith("ja"):
                return "%s  %s" % (preview, ja)
            if lang.startswith("fr"):
                return "%s  %s" % (preview, fr)
            return "%s  %s" % (preview, en)
    return style_id or ""


def short_name(style_id, lang="en"):
    for sid, _preview, en, ja, fr in _STYLE_LABELS:
        if sid == style_id:
            if lang.startswith("ja"):
                return ja
            if lang.startswith("fr"):
                return fr
            return en
    return style_id or ""


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


def _emphasis_of(cursor):
    val = _get(cursor, "CharEmphasis", _EMPHASIS_NONE)
    if val is None:
        return _EMPHASIS_NONE
    if isinstance(val, dict) and "error" in val:
        return _EMPHASIS_NONE
    try:
        return int(val)
    except (TypeError, ValueError):
        return _EMPHASIS_NONE


def _has_emphasis(cursor):
    return _emphasis_of(cursor) != _EMPHASIS_NONE


def selection_has_emphasis(selection):
    return _has_emphasis(selection)


def expand_emphasis_span_indices(flags, index):
    """Pure helper: flags[i] True means character i has CharEmphasis != NONE."""
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


def text_unchanged_after_emphasis_change(before, after):
    return before == after


def document_default_style(doc):
    if _prefs is None:
        return _BUILTIN_DEFAULT
    return _prefs.get_emphasis_default(doc)


def apply_style_tooltip(doc, lang="en"):
    style = document_default_style(doc)
    name = short_name(style, lang)
    if lang.startswith("ja"):
        return "圏点を付ける — %s" % name
    if lang.startswith("fr"):
        return "Appliquer des points d'emphase — %s" % name
    return "Apply emphasis marks — %s" % name


def _anchor_inside_emphasis(text, text_range):
    cursor = text.createTextCursorByRange(text_range.getStart())
    cursor.collapseToStart()

    right = text.createTextCursorByRange(cursor.getStart())
    if right.goRight(1, True) and _has_emphasis(right):
        right.collapseToStart()
        return right

    left = text.createTextCursorByRange(cursor.getStart())
    if left.goLeft(1, True) and _has_emphasis(left):
        left.collapseToStart()
        return left

    if not _is_collapsed(text_range) and _has_emphasis(text_range):
        mid = text.createTextCursorByRange(text_range.getStart())
        mid.collapseToStart()
        return mid
    return None


def expand_to_emphasis_span(text, text_range):
    if text_range is None:
        return None
    anchor = _anchor_inside_emphasis(text, text_range)
    if anchor is None:
        return None

    start = text.createTextCursorByRange(anchor.getStart())
    start.collapseToStart()
    while True:
        probe = text.createTextCursorByRange(start.getStart())
        if not probe.goLeft(1, False):
            break
        check = text.createTextCursorByRange(probe.getStart())
        if not check.goRight(1, True) or not _has_emphasis(check):
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
        if not check.goRight(1, True) or not _has_emphasis(check):
            break
        included += 1
    if included == 0:
        return None
    span.goRight(included, True)
    return span


def _apply_emphasis_uno(cursor, uno_value):
    return _set(cursor, "CharEmphasis", int(uno_value))


def _clear_emphasis(cursor):
    return _set(cursor, "CharEmphasis", _EMPHASIS_NONE)


def _apply_style_to_selection(doc, style_id):
    """Apply a semantic style to the current non-empty selection. Returns True if done."""
    uno_value = style_to_uno(style_id)
    if uno_value is None:
        _message(
            doc,
            "marinaMoji emphasis",
            "Unsupported emphasis style.",
            kind="error",
        )
        return False

    selection = _get_selection_range(doc, allow_collapsed=False)
    if selection is None:
        _message(
            doc,
            "marinaMoji emphasis",
            "Select the text that should receive emphasis marks (圏点).",
            kind="info",
        )
        return False

    base = _range_text(selection)
    if not base.strip():
        _message(
            doc,
            "marinaMoji emphasis",
            "The selection is empty.",
            kind="info",
        )
        return False

    text = doc.Text
    cursor = text.createTextCursorByRange(selection)
    before = _range_text(cursor)
    if not _apply_emphasis_uno(cursor, uno_value):
        _message(
            doc,
            "marinaMoji emphasis",
            "Could not set CharEmphasis on this selection.\n"
            "Enable Asian language support if it is off.",
            kind="error",
        )
        return False
    after = _range_text(cursor)
    if after != before:
        _message(
            doc,
            "marinaMoji emphasis",
            "Apply changed the underlying text unexpectedly. "
            "Please undo and report this.",
            kind="error",
        )
        return False
    try:
        doc.getCurrentController().select(cursor)
    except Exception:
        pass
    return True


def apply_emphasis(*_args):
    """Toolbar main button: apply the document default (never toggles off)."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    style = document_default_style(doc)
    _apply_style_to_selection(doc, style)


def apply_emphasis_style(style_id):
    """Apply a specific semantic style (passage override; does not change default)."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    _apply_style_to_selection(doc, style_id)


def remove_emphasis(*_args):
    """Remove CharEmphasis only; preserve text and unrelated formatting."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    selection = _get_selection_range(doc, allow_collapsed=True)
    if selection is None:
        _message(
            doc,
            "marinaMoji emphasis",
            "Place the cursor inside emphasised text, or select it, then remove.",
            kind="info",
        )
        return

    text = doc.Text
    span = expand_to_emphasis_span(text, selection)
    if span is None:
        if not _is_collapsed(selection) and selection_has_emphasis(selection):
            span = text.createTextCursorByRange(selection)
        else:
            _message(
                doc,
                "marinaMoji emphasis",
                "No emphasis marks found at the cursor.",
                kind="info",
            )
            return

    before = _range_text(span)
    _clear_emphasis(span)
    after = _range_text(span)
    if after != before:
        _message(
            doc,
            "marinaMoji emphasis",
            "Remove changed the underlying text unexpectedly. "
            "Please undo and report this.",
            kind="error",
        )
        return
    try:
        doc.getCurrentController().select(span)
    except Exception:
        pass


def _ask_default_style(doc, current):
    """Compact dialog: choose document default. Returns style id or None."""
    import uno

    try:
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        dialog_model = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControlDialogModel", ctx
        )
        dialog_model.Title = "Set default emphasis mark"
        dialog_model.Width = 200
        dialog_model.Height = 95
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
            PositionY=6,
            Width=180,
            Height=12,
            Label="Document default (既存の圏点は変えません):",
        )
        items = tuple(
            "%s  %s / %s" % (preview, ja, en)
            for _sid, preview, en, ja, _fr in _STYLE_LABELS
        )
        selected = 0
        for i, sid in enumerate(style_ids()):
            if sid == current:
                selected = i
                break
        _insert(
            "list",
            "ListBox",
            PositionX=10,
            PositionY=22,
            Width=180,
            Height=40,
            Dropdown=True,
            StringItemList=items,
        )
        dialog_model.getByName("list").SelectedItems = (selected,)
        _insert(
            "ok",
            "Button",
            PositionX=90,
            PositionY=70,
            Width=45,
            Height=14,
            Label="OK",
            PushButtonType=1,
            DefaultButton=True,
        )
        _insert(
            "cancel",
            "Button",
            PositionX=140,
            PositionY=70,
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
        result = control.execute()
        idx = 0
        try:
            sel = tuple(dialog_model.getByName("list").SelectedItems)
            if sel:
                idx = int(sel[0])
        except Exception:
            idx = selected
        control.dispose()
        if result != 1:
            return None
        ids = style_ids()
        if idx < 0 or idx >= len(ids):
            return None
        return ids[idx]
    except Exception as exc:
        _message(
            doc,
            "marinaMoji emphasis",
            "Could not open the default dialog (%s)." % type(exc).__name__,
            kind="error",
        )
        return None


def set_emphasis_default(*_args):
    """Explicitly change the document default; leave existing marks alone."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    current = document_default_style(doc)
    chosen = _ask_default_style(doc, current)
    if chosen is None:
        return
    if _prefs is None:
        _message(
            doc,
            "marinaMoji emphasis",
            "Preference module unavailable.",
            kind="error",
        )
        return
    ok, detail = _prefs.set_emphasis_default(doc, chosen)
    if not ok:
        _message(
            doc,
            "marinaMoji emphasis",
            "Could not save the document default (%s)." % detail,
            kind="error",
        )
        return
    _message(
        doc,
        "marinaMoji emphasis",
        "Document default is now %s.\n"
        "Existing emphasis marks were not changed."
        % short_name(chosen, "en"),
        kind="info",
    )


def _popup_rectangle(doc):
    """UNO Rectangle for XPopupMenu.execute (Point causes CannotConvertException)."""
    import uno

    rect = uno.createUnoStruct("com.sun.star.awt.Rectangle")
    try:
        frame = doc.getCurrentController().getFrame()
        window = frame.getContainerWindow()
        ps = window.getPosSize()
        rect.X = int(ps.X + max(8, ps.Width // 3))
        rect.Y = int(ps.Y + max(40, ps.Height // 5))
    except Exception:
        rect.X = 200
        rect.Y = 200
    rect.Width = 0
    rect.Height = 0
    return rect


def _choose_emphasis_action_dialog(doc):
    """Fallback menu as a compact dialog if PopupMenu cannot run."""
    import uno

    default = document_default_style(doc)
    try:
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        dialog_model = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControlDialogModel", ctx
        )
        dialog_model.Title = "Emphasis marks"
        dialog_model.Width = 210
        dialog_model.Height = 110
        dialog_model.Closeable = True

        def _insert(name, service, **props):
            m = dialog_model.createInstance(
                "com.sun.star.awt.UnoControl%sModel" % service
            )
            m.Name = name
            for k, v in props.items():
                setattr(m, k, v)
            dialog_model.insertByName(name, m)

        actions = [
            ("APPLY_DEFAULT", "Apply default — %s" % short_name(default, "en")),
        ]
        for sid, preview, en, ja, _fr in _STYLE_LABELS:
            actions.append((sid, "%s  %s  %s" % (preview, en, ja)))
        actions.append(("REMOVE", "Remove emphasis  圏点を外す"))
        actions.append(("SET_DEFAULT", "Set default emphasis mark…"))

        _insert(
            "lbl",
            "FixedText",
            PositionX=10,
            PositionY=6,
            Width=190,
            Height=12,
            Label="Choose an emphasis action:",
        )
        _insert(
            "list",
            "ListBox",
            PositionX=10,
            PositionY=22,
            Width=190,
            Height=55,
            Dropdown=False,
            StringItemList=tuple(a[1] for a in actions),
        )
        dialog_model.getByName("list").SelectedItems = (0,)
        _insert(
            "ok",
            "Button",
            PositionX=100,
            PositionY=85,
            Width=45,
            Height=14,
            Label="OK",
            PushButtonType=1,
            DefaultButton=True,
        )
        _insert(
            "cancel",
            "Button",
            PositionX=150,
            PositionY=85,
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
        result = control.execute()
        idx = 0
        try:
            sel = tuple(dialog_model.getByName("list").SelectedItems)
            if sel:
                idx = int(sel[0])
        except Exception:
            idx = 0
        control.dispose()
        if result != 1 or idx < 0 or idx >= len(actions):
            return None
        return actions[idx][0]
    except Exception:
        return None


def _dispatch_emphasis_action(action):
    if action is None:
        return
    if action == "APPLY_DEFAULT":
        apply_emphasis()
        return
    if action == "REMOVE":
        remove_emphasis()
        return
    if action == "SET_DEFAULT":
        set_emphasis_default()
        return
    if action in style_ids():
        apply_emphasis_style(action)


def show_emphasis_menu(*_args):
    """Toolbar dropdown: apply mark / remove / set default.

    Uses XPopupMenu with a Rectangle (not Point). Falls back to a dialog
    if the popup cannot be shown on this platform/build.
    """
    try:
        doc = _get_document()
    except RuntimeError:
        return
    import uno

    try:
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        popup = smgr.createInstanceWithContext("com.sun.star.awt.PopupMenu", ctx)

        ID_APPLY_DEFAULT = 1
        ID_REMOVE = 50
        ID_SET_DEFAULT = 60
        style_item_ids = {}

        default = document_default_style(doc)
        popup.insertItem(
            ID_APPLY_DEFAULT,
            "Apply default — %s" % short_name(default, "en"),
            0,
            0,
        )
        popup.insertSeparator(1)
        pos = 2
        for sid, preview, en, ja, _fr in _STYLE_LABELS:
            item_id = 10 + pos
            style_item_ids[item_id] = sid
            mark = "* " if sid == default else "  "
            popup.insertItem(
                item_id,
                "%s%s  %s  %s" % (mark, preview, en, ja),
                0,
                pos,
            )
            pos += 1
        popup.insertSeparator(pos)
        pos += 1
        popup.insertItem(ID_REMOVE, "Remove emphasis", 0, pos)
        pos += 1
        popup.insertSeparator(pos)
        pos += 1
        popup.insertItem(ID_SET_DEFAULT, "Set default emphasis mark...", 0, pos)

        frame = doc.getCurrentController().getFrame()
        window = frame.getContainerWindow()
        rect = _popup_rectangle(doc)
        chosen = popup.execute(window, rect, 0)
        if not chosen:
            return
        if chosen == ID_APPLY_DEFAULT:
            apply_emphasis()
            return
        if chosen == ID_REMOVE:
            remove_emphasis()
            return
        if chosen == ID_SET_DEFAULT:
            set_emphasis_default()
            return
        if chosen in style_item_ids:
            apply_emphasis_style(style_item_ids[chosen])
            return
    except Exception:
        action = _choose_emphasis_action_dialog(doc)
        if action is None:
            _message(
                doc,
                "marinaMoji emphasis",
                "Could not open the emphasis menu.",
                kind="error",
            )
            return
        _dispatch_emphasis_action(action)
