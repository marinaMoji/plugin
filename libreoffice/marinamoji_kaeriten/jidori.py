# -*- coding: utf-8 -*-
"""
Jidori (字取り) — approximate fit of a short CJK run to N full-width cells.

Native Writer only:
  Expand → CharKerning (twips; Spacing)
  Shrink → CharScaleWidth (horizontal writing only)

Identity / restore (survives ODT):
  Bookmark name marinaMoji_jidori_<id>
  UserDefinedProperties marinaMoji.Typography.Jidori.<id> → JSON restore payload

Remove restores prior CharScaleWidth / CharKerning / CharStyleName when known.
Never resets unrelated hand-set spacing that lacks a marinaMoji bookmark.
"""

from __future__ import annotations

import json
import uuid

import jidori_math as _math

try:
    import tatechuyoko as _tate
except ImportError:
    _tate = None

# --- limits -----------------------------------------------------------------
_N_MIN = 1
_N_MAX = 40
_CONFIRM_LEN = 9  # graphemes: ask before apply
_REFUSE_LEN = 17  # graphemes: refuse
_BOOKMARK_PREFIX = "marinaMoji_jidori_"
_UDP_PREFIX = "marinaMoji.Typography.Jidori."

# Session UX
_session_last_n = None  # type: ignore

# PropertyState names we serialize
_STATE_DIRECT = "direct"
_STATE_DEFAULT = "default"
_STATE_AMBIGUOUS = "ambiguous"
_STATE_UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested)
# ---------------------------------------------------------------------------


def is_cjk_jidori_text(text):
    """True if every grapheme is suitable for fullwidth-cell jidori MVP."""
    if not text or not str(text).strip():
        return False
    # Reject newlines / paragraph breaks early
    if "\n" in text or "\r" in text:
        return False
    n = 0
    i = 0
    s = str(text)
    while i < len(s):
        o = ord(s[i])
        if 0xFE00 <= o <= 0xFE0F:
            i += 1
            continue
        if not _codepoint_ok_for_jidori(o):
            return False
        n += 1
        i += 1
        while i < len(s) and 0xFE00 <= ord(s[i]) <= 0xFE0F:
            i += 1
        # skip common combining marks attached to base
        while i < len(s) and _is_combining(ord(s[i])):
            i += 1
    return n >= 1


def _is_combining(o):
    # Mn/Mc rough: combining diacritical blocks used with CJK
    return (0x0300 <= o <= 0x036F) or (0x1AB0 <= o <= 0x1AFF) or (0x20D0 <= o <= 0x20FF)


def _codepoint_ok_for_jidori(o):
    """CJK ideographs / kana / select fullwidth punctuation; not Latin/digits."""
    # Hiragana, Katakana, CJK Unified + extensions (BMP samples)
    if 0x3040 <= o <= 0x309F:  # Hiragana
        return True
    if 0x30A0 <= o <= 0x30FF:  # Katakana
        return True
    if 0x31F0 <= o <= 0x31FF:  # Katakana phonetic ext
        return True
    if 0x3400 <= o <= 0x4DBF:  # CJK Ext A
        return True
    if 0x4E00 <= o <= 0x9FFF:  # CJK Unified
        return True
    if 0xF900 <= o <= 0xFAFF:  # Compatibility ideographs
        return True
    if 0xFF66 <= o <= 0xFF9D:  # Halfwidth katakana (treat as kana)
        return True
    # Ideographic space — allow but rare in short jidori
    if o == 0x3000:
        return True
    # Common CJK punctuation (fullwidth-ish frames)
    if o in (
        0x3001,
        0x3002,
        0x300C,
        0x300D,
        0x300E,
        0x300F,
        0x3010,
        0x3011,
        0x30FB,
        0xFF01,
        0xFF08,
        0xFF09,
        0xFF0C,
        0xFF0E,
        0xFF1A,
        0xFF1B,
        0xFF1F,
    ):
        return True
    # SIP / TIP ideographs (e.g. 𠮷 U+20BB7)
    if 0x20000 <= o <= 0x2CEAF:
        return True
    if 0x2F800 <= o <= 0x2FA1F:
        return True
    return False


def initial_n(grapheme_count, last_n=None):
    """Dialog default: last session N, but never surprise-compress."""
    n = int(grapheme_count or 0)
    if last_n is not None:
        try:
            cand = int(last_n)
        except (TypeError, ValueError):
            cand = None
        if cand is not None and _N_MIN <= cand <= _N_MAX:
            if cand < n:
                return n  # avoid default compression
            return cand
    if n <= 0:
        return 5
    return max(n, 5) if n < 5 else n


def classify_jidori_length(grapheme_count):
    """Return ('ok'|'confirm'|'refuse', message_or_None)."""
    n = int(grapheme_count or 0)
    if n < 1:
        return "refuse", "empty"
    if n >= _REFUSE_LEN:
        return (
            "refuse",
            "Selection is too long for jidori (maximum %d characters)." % (_REFUSE_LEN - 1),
        )
    if n >= _CONFIRM_LEN:
        return (
            "confirm",
            "Fit %d characters into a fixed cell count?\n"
            "Long selections can look uneven." % n,
        )
    return "ok", None


def encode_restore_payload(payload):
    """Serialize restore dict to a compact JSON string."""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def decode_restore_payload(raw):
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    try:
        data = json.loads(str(raw))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return data


def new_jidori_id():
    return uuid.uuid4().hex[:12]


def bookmark_name_for_id(jid):
    return _BOOKMARK_PREFIX + str(jid)


def id_from_bookmark_name(name):
    if not name or not str(name).startswith(_BOOKMARK_PREFIX):
        return None
    return str(name)[len(_BOOKMARK_PREFIX) :]


def udp_key_for_id(jid):
    return _UDP_PREFIX + str(jid)


# ---------------------------------------------------------------------------
# UNO helpers
# ---------------------------------------------------------------------------


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
        return text_range.getString() or ""
    except Exception:
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
    if hasattr(sel, "getString") and not hasattr(sel, "getCount"):
        if len(_range_text(sel)) == 0 and not allow_collapsed:
            return None
        return sel
    try:
        count = sel.getCount()
    except Exception:
        return None
    if count < 1:
        return None
    first = sel.getByIndex(0)
    if count == 1:
        if len(_range_text(first)) == 0 and not allow_collapsed:
            return None
        return first
    # Merge multi-range into one cursor when possible
    try:
        text = doc.Text
        cursor = text.createTextCursorByRange(first)
        for i in range(1, count):
            cursor.gotoRange(sel.getByIndex(i).getEnd(), True)
        if len(_range_text(cursor)) == 0 and not allow_collapsed:
            return None
        return cursor
    except Exception:
        if len(_range_text(first)) == 0 and not allow_collapsed:
            return None
        return first


def _message(doc, title, text, kind="info"):
    try:
        import uno
        from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
        from com.sun.star.awt.MessageBoxType import ERRORBOX, INFOBOX, WARNINGBOX

        box_type = INFOBOX
        if kind == "error":
            box_type = ERRORBOX
        elif kind == "warning":
            box_type = WARNINGBOX
        ctx = uno.getComponentContext()
        toolkit = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.Toolkit", ctx
        )
        window = doc.getCurrentController().getFrame().getContainerWindow()
        box = toolkit.createMessageBox(window, box_type, BUTTONS_OK, title, text[:1500])
        box.execute()
    except Exception:
        print("%s: %s" % (title, text))


def _confirm(doc, title, text):
    try:
        import uno
        from com.sun.star.awt.MessageBoxButtons import BUTTONS_YES_NO
        from com.sun.star.awt.MessageBoxResults import YES
        from com.sun.star.awt.MessageBoxType import QUERYBOX

        ctx = uno.getComponentContext()
        toolkit = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.Toolkit", ctx
        )
        window = doc.getCurrentController().getFrame().getContainerWindow()
        box = toolkit.createMessageBox(
            window, QUERYBOX, BUTTONS_YES_NO, title, text[:1500]
        )
        return box.execute() == YES
    except Exception:
        return False


def _get(obj, name, default=None):
    try:
        return obj.getPropertyValue(name)
    except Exception:
        return default


def _set(obj, name, value):
    try:
        obj.setPropertyValue(name, value)
        return True
    except Exception:
        return False


def _prop_state(obj, name):
    try:
        state = obj.getPropertyState(name)
        # DIRECT_VALUE=0, DEFAULT_VALUE=1, AMBIGUOUS_VALUE=2
        try:
            iv = int(state)
        except Exception:
            iv = -1
        if iv == 0:
            return _STATE_DIRECT
        if iv == 1:
            return _STATE_DEFAULT
        if iv == 2:
            return _STATE_AMBIGUOUS
    except Exception:
        pass
    return _STATE_UNKNOWN


def _set_prop_to_default(obj, name):
    try:
        obj.setPropertyToDefault(name)
        return True
    except Exception:
        return False


def _user_defined_properties(doc):
    try:
        props = doc.getDocumentProperties()
    except Exception:
        try:
            props = doc.DocumentProperties
        except Exception:
            return None
    try:
        return props.UserDefinedProperties
    except Exception:
        return None


def _udp_get(doc, key):
    udp = _user_defined_properties(doc)
    if udp is None:
        return None
    try:
        info = udp.getPropertySetInfo()
        if info is None or not info.hasPropertyByName(key):
            return None
        return udp.getPropertyValue(key)
    except Exception:
        return None


def _udp_set(doc, key, value):
    udp = _user_defined_properties(doc)
    if udp is None:
        return False
    try:
        info = udp.getPropertySetInfo()
        has = info is not None and info.hasPropertyByName(key)
        if not has:
            try:
                from com.sun.star.beans.PropertyAttribute import REMOVEABLE
            except Exception:
                REMOVEABLE = 1
            udp.addProperty(key, REMOVEABLE, value)
        else:
            udp.setPropertyValue(key, value)
        try:
            doc.setModified(True)
        except Exception:
            pass
        return True
    except Exception:
        return False


def _udp_remove(doc, key):
    udp = _user_defined_properties(doc)
    if udp is None:
        return False
    try:
        info = udp.getPropertySetInfo()
        if info is None or not info.hasPropertyByName(key):
            return True
        udp.removeProperty(key)
        try:
            doc.setModified(True)
        except Exception:
            pass
        return True
    except Exception:
        return False


def _selection_has_warichu(cursor):
    return bool(_get(cursor, "CharCombineIsOn", False))


def _selection_has_ruby(cursor):
    val = _get(cursor, "RubyText", "")
    return bool(val)


def _selection_has_tate(cursor):
    try:
        rot = int(_get(cursor, "CharRotation", 0) or 0)
    except Exception:
        rot = 0
    fit = bool(_get(cursor, "CharRotationIsFitToLine", False))
    return rot == 900 and fit


def _is_vertical(doc, text_range):
    if _tate is not None and hasattr(_tate, "_paragraph_is_vertical"):
        try:
            return bool(_tate._paragraph_is_vertical(doc, text_range))
        except Exception:
            pass
    return False


def _em_size_pt(cursor):
    try:
        h = cursor.getPropertyValue("CharHeightAsian")
        if h:
            return float(h)
    except Exception:
        pass
    try:
        return float(cursor.getPropertyValue("CharHeight") or 12.0)
    except Exception:
        return 12.0


def _snapshot_formatting(cursor):
    """Capture scale/kern/style for restore. Refuse if ambiguous."""
    scale_state = _prop_state(cursor, "CharScaleWidth")
    kern_state = _prop_state(cursor, "CharKerning")
    if scale_state == _STATE_AMBIGUOUS or kern_state == _STATE_AMBIGUOUS:
        return None, "mixed"
    scale = _get(cursor, "CharScaleWidth", 100)
    kern = _get(cursor, "CharKerning", 0)
    try:
        scale = int(scale if scale is not None else 100)
    except Exception:
        scale = 100
    try:
        kern = int(kern if kern is not None else 0)
    except Exception:
        kern = 0
    style = _get(cursor, "CharStyleName", "") or ""
    style_state = _prop_state(cursor, "CharStyleName")
    return {
        "scale": scale,
        "kern": kern,
        "scale_state": scale_state,
        "kern_state": kern_state,
        "char_style": style,
        "char_style_state": style_state,
    }, None


def _restore_formatting(cursor, payload):
    if not payload:
        return False
    scale_state = payload.get("scale_state", _STATE_DIRECT)
    kern_state = payload.get("kern_state", _STATE_DIRECT)
    if scale_state == _STATE_DEFAULT:
        if not _set_prop_to_default(cursor, "CharScaleWidth"):
            _set(cursor, "CharScaleWidth", 100)
    else:
        _set(cursor, "CharScaleWidth", int(payload.get("scale", 100)))
    if kern_state == _STATE_DEFAULT:
        if not _set_prop_to_default(cursor, "CharKerning"):
            _set(cursor, "CharKerning", 0)
    else:
        _set(cursor, "CharKerning", int(payload.get("kern", 0)))
    style_state = payload.get("char_style_state", _STATE_DEFAULT)
    style = payload.get("char_style", "") or ""
    if style_state == _STATE_DEFAULT or not style:
        _set_prop_to_default(cursor, "CharStyleName")
    else:
        _set(cursor, "CharStyleName", style)
    return True


def _anchor_covers_selection(anchor, selection):
    """True if bookmark anchor equals or contains the selection."""
    if anchor is None or selection is None:
        return False
    try:
        text = anchor.getText()
        # selection starts at/after anchor start and ends at/before anchor end
        # compareRegionStarts(anchor, selection) <= 0 ⇒ anchor.start <= sel.start
        # compareRegionEnds(selection, anchor) <= 0 ⇒ sel.end <= anchor.end
        if text.compareRegionStarts(anchor, selection) > 0:
            return False
        if text.compareRegionEnds(selection, anchor) > 0:
            return False
        return True
    except Exception:
        try:
            return _range_text(anchor) == _range_text(selection) and bool(
                _range_text(anchor)
            )
        except Exception:
            return False


def _find_jidori_at(doc, text_range):
    """Return (id, bookmark, anchor, payload) or (None, None, None, None)."""
    try:
        bookmarks = doc.getBookmarks()
        names = list(bookmarks.getElementNames())
    except Exception:
        return None, None, None, None
    for name in names:
        jid = id_from_bookmark_name(name)
        if not jid:
            continue
        try:
            bm = bookmarks.getByName(name)
            anchor = bm.getAnchor()
        except Exception:
            continue
        if not _anchor_covers_selection(anchor, text_range):
            # Also accept when selection covers the whole bookmark
            if not _anchor_covers_selection(text_range, anchor):
                continue
        payload = decode_restore_payload(_udp_get(doc, udp_key_for_id(jid)))
        return jid, bm, anchor, payload
    return None, None, None, None


def _delete_bookmark(doc, name):
    try:
        bookmarks = doc.getBookmarks()
        if bookmarks.hasByName(name):
            bookmarks.removeByName(name)
            return True
    except Exception:
        pass
    # Fallback: dispose content
    try:
        bm = doc.getBookmarks().getByName(name)
        bm.dispose()
        return True
    except Exception:
        return False


def _create_bookmark(doc, text_range, name):
    """Wrap text_range in a named bookmark. Returns True on success."""
    try:
        text = text_range.getText()
        bm = doc.createInstance("com.sun.star.text.Bookmark")
        bm.Name = name
        # Absorb=True → bookmark spans the range
        text.insertTextContent(text_range, bm, True)
        return True
    except Exception:
        return False


def _ask_n_cells(doc, default_n, explanation=""):
    """Small N dialog. Returns int or None if cancelled."""
    import uno

    global _session_last_n
    try:
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        dialog_model = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControlDialogModel", ctx
        )
        dialog_model.Title = "字取り · Jidori"
        dialog_model.Width = 200
        dialog_model.Height = 78
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
            Height=10,
            Label="Fit the selected text into:",
        )
        _insert(
            "num",
            "NumericField",
            PositionX=10,
            PositionY=20,
            Width=50,
            Height=14,
            Value=float(default_n),
            ValueMin=float(_N_MIN),
            ValueMax=float(_N_MAX),
            DecimalAccuracy=0,
            StrictFormat=True,
            Spin=True,
        )
        _insert(
            "lbl2",
            "FixedText",
            PositionX=64,
            PositionY=22,
            Width=120,
            Height=10,
            Label="character cells",
        )
        _insert(
            "hint",
            "FixedText",
            PositionX=10,
            PositionY=38,
            Width=180,
            Height=16,
            Label=explanation
            or "Approximate fit to N full-width character positions.",
            MultiLine=True,
        )
        _insert(
            "ok",
            "Button",
            PositionX=90,
            PositionY=58,
            Width=45,
            Height=14,
            Label="Apply",
            PushButtonType=1,
            DefaultButton=True,
        )
        _insert(
            "cancel",
            "Button",
            PositionX=140,
            PositionY=58,
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
            control.getControl("num").setFocus()
        except Exception:
            pass
        result = control.execute()
        value = default_n
        try:
            value = int(round(float(dialog_model.getByName("num").Value)))
        except Exception:
            value = default_n
        control.dispose()
        if result != 1:
            return None
        if value < _N_MIN or value > _N_MAX:
            _message(
                doc,
                "marinaMoji jidori",
                "Enter a whole number from %d to %d." % (_N_MIN, _N_MAX),
                kind="warning",
            )
            return None
        return value
    except Exception as exc:
        _message(
            doc,
            "marinaMoji jidori",
            "Could not open the jidori dialog (%s)." % type(exc).__name__,
            kind="error",
        )
        return None


def _apply_plan_to_cursor(cursor, plan, em_pt):
    scale, kern = _math.plan_to_uno_values(plan, em_pt)
    if scale is None:
        return False
    ok1 = _set(cursor, "CharScaleWidth", int(scale))
    ok2 = _set(cursor, "CharKerning", int(kern or 0))
    return ok1 and ok2


# ---------------------------------------------------------------------------
# Public commands
# ---------------------------------------------------------------------------


def apply_jidori(*_args):
    """Toolbar: fit selection into N character cells."""
    global _session_last_n
    try:
        doc = _get_document()
    except RuntimeError as exc:
        return
    cursor = _get_selection_range(doc, allow_collapsed=False)
    if cursor is None or _is_collapsed(cursor):
        _message(
            doc,
            "marinaMoji jidori",
            "Select the text to fit into a specified number of character cells.",
        )
        return

    text = _range_text(cursor)
    if "\n" in text or "\r" in text:
        _message(
            doc,
            "marinaMoji jidori",
            "Jidori applies to a single inline run.\n"
            "Select text within one paragraph only.",
            kind="warning",
        )
        return

    if not is_cjk_jidori_text(text):
        _message(
            doc,
            "marinaMoji jidori",
            "Jidori currently supports Japanese (CJK) text only.\n"
            "Latin letters and Western digits are not fitted as full-width cells.",
            kind="warning",
        )
        return

    if _selection_has_warichu(cursor):
        _message(
            doc,
            "marinaMoji jidori",
            "Cannot apply jidori on warichū. Remove warichū first, or select other text.",
            kind="warning",
        )
        return
    if _selection_has_ruby(cursor):
        _message(
            doc,
            "marinaMoji jidori",
            "Cannot apply jidori on ruby. Remove ruby first, or select other text.",
            kind="warning",
        )
        return
    if _selection_has_tate(cursor):
        _message(
            doc,
            "marinaMoji jidori",
            "Cannot apply jidori on tate-chū-yoko. Remove it first, or select other text.",
            kind="warning",
        )
        return

    n = _math.count_graphemes(text)
    verdict, msg = classify_jidori_length(n)
    if verdict == "refuse":
        _message(doc, "marinaMoji jidori", msg or "Selection refused.", kind="warning")
        return
    if verdict == "confirm":
        if not _confirm(doc, "marinaMoji jidori", msg):
            return

    vertical = _is_vertical(doc, cursor)
    existing_id, existing_bm, existing_anchor, existing_payload = _find_jidori_at(
        doc, cursor
    )

    # Reapply: work on full bookmark span; keep original restore baseline
    target = cursor
    restore_base = None
    jid = None
    if existing_id and existing_anchor is not None:
        target = existing_anchor
        # Require full span if selection is a proper subset with different text length
        if _range_text(cursor) != _range_text(existing_anchor):
            if not _anchor_covers_selection(cursor, existing_anchor):
                _message(
                    doc,
                    "marinaMoji jidori",
                    "Select the entire existing jidori span to change N.",
                    kind="warning",
                )
                return
            target = existing_anchor
            try:
                doc.getCurrentController().select(target)
            except Exception:
                pass
        jid = existing_id
        restore_base = existing_payload
        default_n = int((existing_payload or {}).get("N") or initial_n(n, _session_last_n))
    else:
        snap, err = _snapshot_formatting(cursor)
        if err == "mixed":
            _message(
                doc,
                "marinaMoji jidori",
                "Selection has mixed character scaling or spacing.\n"
                "Select a uniformly formatted run.",
                kind="warning",
            )
            return
        restore_base = snap
        default_n = initial_n(n, _session_last_n)

    hint = "Approximate fit to N full-width character positions."
    if vertical:
        hint = "Vertical: expansion only (compression not supported)."
    N = _ask_n_cells(doc, default_n, explanation=hint)
    if N is None:
        return

    # Recompute from baseline text (not already-adjusted width)
    base_text = _range_text(target)
    n = _math.count_graphemes(base_text)
    plan = _math.plan_jidori(base_text, N, vertical=vertical)
    if plan.mode == "invalid":
        if vertical and N < n:
            _message(
                doc,
                "marinaMoji jidori",
                "Compression into fewer cells is not supported in vertical writing yet.\n"
                "Expanding into more cells works. For fewer cells, use horizontal writing\n"
                "or set Scale width manually (glyphs may distort).",
                kind="warning",
            )
        else:
            _message(
                doc,
                "marinaMoji jidori",
                "Cannot apply jidori for this selection and N.\n(%s)" % plan.note,
                kind="warning",
            )
        return

    # On reapply: restore baseline formatting first so we do not compound
    if jid and restore_base:
        _restore_formatting(target, restore_base)

    if plan.mode == "noop":
        # Still record identity if new; or update N metadata
        em_pt = _em_size_pt(target)
        scale, kern = 100, 0
    else:
        em_pt = _em_size_pt(target)
        if not _apply_plan_to_cursor(target, plan, em_pt):
            _message(
                doc,
                "marinaMoji jidori",
                "Could not set character scaling/spacing.",
                kind="error",
            )
            return
        scale, kern = _math.plan_to_uno_values(plan, em_pt)

    before = base_text
    after = _range_text(target)
    if before != after:
        _message(
            doc,
            "marinaMoji jidori",
            "Text changed unexpectedly. Please undo and report this.",
            kind="error",
        )
        return

    if jid is None:
        jid = new_jidori_id()
        bname = bookmark_name_for_id(jid)
        if not _create_bookmark(doc, target, bname):
            # Formatting applied but identity failed — warn; Remove may not work
            _message(
                doc,
                "marinaMoji jidori",
                "Jidori formatting was applied, but a bookmark could not be created.\n"
                "Remove jidori may not restore prior formatting after save.",
                kind="warning",
            )
            _session_last_n = N
            return

    payload = dict(restore_base or {})
    payload.update(
        {
            "N": N,
            "n": n,
            "applied_scale": int(scale if scale is not None else 100),
            "applied_kern": int(kern if kern is not None else 0),
            "vertical": bool(vertical),
            "text": before,
        }
    )
    if not _udp_set(doc, udp_key_for_id(jid), encode_restore_payload(payload)):
        _message(
            doc,
            "marinaMoji jidori",
            "Formatting applied, but restore metadata could not be saved.\n"
            "Remove after reopen may not restore prior scaling/spacing.",
            kind="warning",
        )
    _session_last_n = N


def remove_jidori(*_args):
    """Toolbar: remove marinaMoji jidori and restore prior formatting."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    cursor = _get_selection_range(doc, allow_collapsed=True)
    if cursor is None:
        _message(
            doc,
            "marinaMoji jidori",
            "Select the jidori text (or place the caret inside it).",
        )
        return

    jid, bm, anchor, payload = _find_jidori_at(doc, cursor)
    if jid is None or anchor is None:
        _message(
            doc,
            "marinaMoji jidori",
            "No marinaMoji jidori formatting was identified in this selection.",
        )
        return

    before = _range_text(anchor)
    if payload:
        _restore_formatting(anchor, payload)
    else:
        # Identity without payload — refuse destructive reset
        _message(
            doc,
            "marinaMoji jidori",
            "A jidori bookmark was found, but restore data is missing.\n"
            "Refusing to reset scaling/spacing to defaults.",
            kind="warning",
        )
        return

    after = _range_text(anchor)
    if before != after:
        _message(
            doc,
            "marinaMoji jidori",
            "Text changed unexpectedly while removing jidori. Please undo.",
            kind="error",
        )
        return

    _delete_bookmark(doc, bookmark_name_for_id(jid))
    _udp_remove(doc, udp_key_for_id(jid))
    try:
        doc.getCurrentController().select(anchor)
    except Exception:
        pass
