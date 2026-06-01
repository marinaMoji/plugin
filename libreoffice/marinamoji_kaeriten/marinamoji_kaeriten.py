# -*- coding: utf-8 -*-
"""
marinaMoji Kaeriten — LibreOffice Writer (single-file macro module).
Render / unrender kaeriten: 說㆒㆑者 ↔ anchored frames. Scope: selection or whole document.
Shipped in the .oxt as a UNO Job (toolbar/menu) and optionally copied to user/Scripts/python by install.sh.
"""

import json
import os
import re
import subprocess
import sys
from collections import namedtuple

import uno

try:
    from export_core import export_latex_for_clipboard as _latex_clipboard
    from export_core import export_plain_text as _plain_text_export
    from export_core import export_tei_for_clipboard as _tei_clipboard
except ImportError:
    _plain_text_export = _tei_clipboard = _latex_clipboard = None

# UNO enums at module level (after import uno), same pattern as LO TableSample.py
try:
    from com.sun.star.text.TextContentAnchorType import AS_CHARACTER
    from com.sun.star.text.VertOrientation import CHAR_BOTTOM as _VERT_CHAR_BOTTOM
    from com.sun.star.text.WrapTextMode import NONE as _WRAP_NONE
    from com.sun.star.style.LineSpacingMode import FIX as _LINE_FIX
    from com.sun.star.drawing.TextVerticalAdjust import BOTTOM as _TEXT_VERT_BOTTOM
    from com.sun.star.drawing.TextHorizontalAdjust import CENTER as _TEXT_HORIZ_CENTER
except ImportError:
    AS_CHARACTER = 1
    _VERT_CHAR_BOTTOM = 6
    _WRAP_NONE = 0
    _LINE_FIX = 2
    _TEXT_VERT_BOTTOM = 2
    _TEXT_HORIZ_CENTER = 1

_CLUSTER_RE = re.compile(r"([^\u3190-\u319f\s])([\u3190-\u319f]+)")
_SOURCE_PREFIX = "MARINAMOJI:source="
_KaeritenCluster = namedtuple("KaeritenCluster", ("base_char", "marks", "start", "end"))


def _marks_start(cluster):
    return cluster.start + len(cluster.base_char)


def _find_clusters(text):
    out = []
    for match in _CLUSTER_RE.finditer(text):
        out.append(_KaeritenCluster(match.group(1), match.group(2), match.start(), match.end()))
    return out


def _sort_clusters(clusters):
    return sorted(clusters, key=lambda c: c.start, reverse=True)


def _encode_desc(marks):
    return _SOURCE_PREFIX + marks


def _decode_desc(description):
    if not description or not description.startswith(_SOURCE_PREFIX):
        return None
    return description[len(_SOURCE_PREFIX) :]


def _script_dir():
    """Directory containing this module (LO sets __file__ to a file:// URL)."""
    script_ref = __file__
    try:
        if isinstance(script_ref, str) and script_ref.startswith("file:"):
            import uno
            script_ref = uno.fileUrlToSystemPath(script_ref)
        else:
            script_ref = os.path.abspath(script_ref)
    except Exception:
        # Fallback: strip file:// and URL-decode spaces
        if isinstance(script_ref, str) and script_ref.startswith("file://"):
            script_ref = script_ref[7:]
        script_ref = script_ref.replace("%20", " ")
        script_ref = os.path.abspath(script_ref)
    return os.path.dirname(script_ref)


def _mapping_path():
    script_dir = _script_dir()
    path = os.path.join(script_dir, "marinamoji_mapping.json")
    if os.path.isfile(path):
        return path
    raise RuntimeError(
        "marinaMoji: marinamoji_mapping.json not found in " + script_dir
    )


def _load_mapping():
    with open(_mapping_path(), "r", encoding="utf-8") as f:
        return json.load(f)


class _MarkMapper(object):
    def __init__(self):
        data = _load_mapping()
        lo = data.get("rendering", {}).get("libreoffice_frame", {})
        self._char_height_pt = float(lo.get("font_size_pt", 5.0))
        self._font_size_ratio = float(lo.get("font_size_ratio", 0.42))
        self._runtime_char_height = None
        self._host_pt_for_width = None
        # Fine vertical nudge for as-character anchor (1/100 mm; negative = raise).
        self._vert_orient_position_hmm = int(
            lo.get("vert_orient_position_hmm", lo.get("offset_mm_bottom", 0))
        )
        if isinstance(self._vert_orient_position_hmm, float):
            self._vert_orient_position_hmm = int(round(self._vert_orient_position_hmm * 100))
        self._frame_width_hmm = int(lo.get("frame_width_hmm", 180))
        self._line_height_twips = int(lo.get("line_height_twips", 0))  # 0 = auto from font
        self._by_char = {}
        for entry in data.get("marks", []):
            ch = entry.get("char")
            if ch:
                self._by_char[ch] = entry

    @property
    def effective_char_height_pt(self):
        if self._runtime_char_height is not None:
            return self._runtime_char_height
        return self._char_height_pt

    def char_height_from_host(self, host_pt):
        return max(3.0, min(72.0, float(host_pt) * self._font_size_ratio))

    def effective_frame_width_hmm(self):
        host = self._host_pt_for_width if self._host_pt_for_width else 12.0
        return max(80, int(self._frame_width_hmm * host / 12.0))

    def apply_host_size(self, host_pt):
        host = float(host_pt) if host_pt and host_pt > 0 else 12.0
        self._runtime_char_height = self.char_height_from_host(host)
        self._host_pt_for_width = host

    def clear_runtime_size(self):
        self._runtime_char_height = None
        self._host_pt_for_width = None

    def glyphs_for_marks(self, marks):
        chars = list(marks)
        chars.sort(
            key=lambda c: (int(self._by_char.get(c, {}).get("stack_order", 0)), marks.index(c))
        )
        return [self._by_char.get(c, {}).get("display_glyph", c) for c in chars]

    def frame_text(self, marks):
        return "\n".join(self.glyphs_for_marks(marks))


def _get_document():
    try:
        doc = XSCRIPTCONTEXT.getDocument()
        if doc is not None and hasattr(doc, "Text"):
            return doc
    except NameError:
        pass
    import uno
    ctx = uno.getComponentContext()
    desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
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


def _get_selection_range(doc):
    """Writer selection is XIndexAccess of XTextRange(s), not a single range."""
    controller = doc.getCurrentController()
    if controller is None:
        return None
    sel = controller.getSelection()
    if sel is None:
        return None
    # Single text range (some LO versions / contexts)
    if hasattr(sel, "getString"):
        if len(_range_text(sel)) == 0:
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
        if len(_range_text(first)) == 0:
            return None
        return first
    last = sel.getByIndex(count - 1)
    text = doc.Text
    merged = text.createTextCursorByRange(first.getStart())
    merged.gotoRange(last.getEnd(), True)
    if len(_range_text(merged)) == 0:
        return None
    return merged


def _get_document_range(doc):
    text = doc.Text
    cursor = text.createTextCursor()
    cursor.gotoStart(False)
    cursor.gotoEnd(True)
    return cursor


def _char_height_from_props(prop_set):
    for name in ("CharHeightAsian", "CharHeight"):
        try:
            v = float(prop_set.getPropertyValue(name))
            if v > 0.01:
                return v
        except Exception:
            pass
    return None


def _char_height_from_style_family(doc, family_name, style_name):
    if not style_name:
        return None
    try:
        styles = doc.getStyleFamilies().getByName(family_name)
        style = styles.getByName(style_name)
        return _char_height_from_props(style)
    except Exception:
        return None


def _resolve_char_height_pt(doc, cursor):
    """Effective point size; 0 on cursor means 'inherit' — walk paragraph/char styles."""
    h = _char_height_from_props(cursor)
    if h:
        return h
    try:
        h = _char_height_from_style_family(
            doc, "ParagraphStyles", cursor.getPropertyValue("ParaStyleName")
        )
        if h:
            return h
    except Exception:
        pass
    try:
        h = _char_height_from_style_family(
            doc, "CharacterStyles", cursor.getPropertyValue("CharStyleName")
        )
        if h:
            return h
    except Exception:
        pass
    return None


def _host_char_height(doc, text, cursor_at_marks):
    """Point size of the kanji before kaeriten marks (or paragraph default)."""
    host = text.createTextCursorByRange(cursor_at_marks)
    try:
        if host.goLeft(1, False):
            host.goRight(1, True)
            h = _resolve_char_height_pt(doc, host)
            if h:
                return h
    except Exception:
        pass
    try:
        para = text.createTextCursorByRange(cursor_at_marks)
        para.gotoStartOfParagraph(False)
        h = _resolve_char_height_pt(doc, para)
        if h:
            return h
    except Exception:
        pass
    return None


def _host_char_height_at_anchor(doc, text, anchor):
    return _host_char_height(doc, text, text.createTextCursorByRange(anchor))


_FRAME_NAME = "marinaMoji_kaeriten"


def _zero_border():
    bl = uno.createUnoStruct("com.sun.star.table.BorderLine2")
    bl.LineWidth = 0
    return bl


def _set_borderless(frame):
    z = _zero_border()
    for name in ("TopBorder", "BottomBorder", "LeftBorder", "RightBorder"):
        try:
            frame.setPropertyValue(name, z)
        except Exception:
            pass


def _line_spacing_twips(mapper, char_height_pt):
    """Scale line spacing with kaeriten font (fixed twips in mapping only as 5 pt reference)."""
    h = float(char_height_pt)
    ref = mapper._line_height_twips
    if ref > 0:
        return max(int(h * 20), int(ref * h / 5.0))
    return int(h * 28)


def _frame_min_height_hmm(mapper, n_glyphs):
    h_pt = mapper.effective_char_height_pt
    per_line = int(h_pt * 42)
    return per_line * max(1, n_glyphs) + 80


def _apply_frame_dimensions(frame, mapper, n_glyphs):
    """Set width/height from host-scaled metrics (not stale LayoutSize alone)."""
    cap_w = mapper.effective_frame_width_hmm()
    min_h = _frame_min_height_hmm(mapper, n_glyphs)
    frame.setPropertyValue("FrameIsAutomaticHeight", False)
    frame.setPropertyValue("Width", cap_w)
    frame.setPropertyValue("Height", min_h)
    try:
        size = frame.getPropertyValue("LayoutSize")
        w = min(cap_w, max(80, int(size.Width) + 24))
        h = max(min_h, int(size.Height) + 24)
        frame.setPropertyValue("Width", w)
        frame.setPropertyValue("Height", h)
    except Exception:
        pass
    _set_frame_content_align(frame)


def _set_frame_insets_zero(frame):
    """Clear frame insets. LO UI labels differ:
    - Spacing → LeftMargin … BottomMargin (gap to surrounding text)
    - Padding → BorderDistance / *BorderDistance (gap border → content)
    Defaults are often ~1.5–2 mm (0.15–0.2 cm) per side."""
    for name in (
        "LeftMargin",
        "RightMargin",
        "TopMargin",
        "BottomMargin",
        "BorderDistance",
        "LeftBorderDistance",
        "RightBorderDistance",
        "TopBorderDistance",
        "BottomBorderDistance",
    ):
        try:
            frame.setPropertyValue(name, 0)
        except Exception:
            pass


def _style_frame_text(frame_text, mapper):
    """Tight stack inside the frame; CJK size uses CharHeightAsian."""
    cursor = frame_text.createTextCursor()
    cursor.gotoStart(False)
    cursor.gotoEnd(True)
    h = float(mapper.effective_char_height_pt)
    for prop in ("CharHeight", "CharHeightAsian"):
        try:
            cursor.setPropertyValue(prop, h)
        except Exception:
            pass
    for prop in ("ParaTopMargin", "ParaBottomMargin", "ParaLeftMargin", "ParaRightMargin"):
        try:
            cursor.setPropertyValue(prop, 0)
        except Exception:
            pass
    line_twips = _line_spacing_twips(mapper, h)
    try:
        ls = uno.createUnoStruct("com.sun.star.style.LineSpacing")
        ls.Mode = _LINE_FIX
        ls.Height = line_twips
        cursor.setPropertyValue("ParaLineSpacing", ls)
    except Exception:
        pass


def _set_frame_content_align(frame):
    """Stack sits on the bottom of the frame (kaeriten on the line)."""
    try:
        frame.setPropertyValue("TextVerticalAdjust", _TEXT_VERT_BOTTOM)
        frame.setPropertyValue("TextHorizontalAdjust", _TEXT_HORIZ_CENTER)
    except Exception:
        pass


def _configure_frame(frame, mapper):
    frame.setPropertyValue("AnchorType", AS_CHARACTER)
    frame.setPropertyValue("FrameIsAutomaticHeight", True)
    _set_borderless(frame)
    _set_frame_insets_zero(frame)
    _set_frame_content_align(frame)
    frame.setPropertyValue("Width", mapper.effective_frame_width_hmm())
    try:
        frame.setPropertyValue("Surround", _WRAP_NONE)
        frame.setPropertyValue("TextWrap", _WRAP_NONE)
    except Exception:
        pass
    try:
        # BOTTOM (3) anchors to page/line box and sits too low; CHAR_BOTTOM (6) uses the glyph.
        frame.setPropertyValue("VertOrient", _VERT_CHAR_BOTTOM)
        frame.setPropertyValue("VertOrientPosition", mapper._vert_orient_position_hmm)
    except Exception:
        pass


def _insert_frame(text, cursor, marks, mapper, doc):
    frame = doc.createInstance("com.sun.star.text.TextFrame")
    _configure_frame(frame, mapper)
    frame.setPropertyValue("Description", _encode_desc(marks))
    try:
        frame.setPropertyValue("Name", _FRAME_NAME)
    except Exception:
        pass
    text.insertTextContent(cursor, frame, False)
    ft = frame.getText()
    fc = ft.createTextCursor()
    ft.insertString(fc, mapper.frame_text(marks), False)
    _style_frame_text(ft, mapper)
    # LO may reapply frame style defaults on insert — clear insets, align, size.
    _set_frame_insets_zero(frame)
    _configure_frame(frame, mapper)
    n_glyphs = len(mapper.glyphs_for_marks(marks))
    _apply_frame_dimensions(frame, mapper, n_glyphs)


def _cursor_at(text, work_range, offset):
    c = text.createTextCursorByRange(work_range.getStart())
    if offset > 0:
        c.goRight(offset, False)
    return c


def _range_between(text, work_range, start_off, end_off):
    c0 = _cursor_at(text, work_range, start_off)
    c1 = _cursor_at(text, work_range, end_off)
    r = text.createTextCursorByRange(c0)
    r.gotoRange(c1, True)
    return r


def _format_clusters(text, work_range, mapper, doc):
    content = work_range.getString()
    count = 0
    for cluster in _sort_clusters(_find_clusters(content)):
        ms = _marks_start(cluster)
        mark_cursor = _cursor_at(text, work_range, ms)
        host_pt = _host_char_height(doc, text, mark_cursor)
        mapper.apply_host_size(host_pt)
        _range_between(text, work_range, ms, cluster.end).setString("")
        _insert_frame(text, mark_cursor, cluster.marks, mapper, doc)
        mapper.clear_runtime_size()
        count += 1
    return count


def _refresh_frames_in_place(doc, work_range, mapper):
    """Update existing frames from host kanji size (no show_source)."""
    text = doc.Text
    count = 0
    for frame, _marks in _iter_frames(doc):
        try:
            anchor = frame.getAnchor()
        except Exception:
            continue
        if not _range_contains(work_range, anchor):
            continue
        host_pt = _host_char_height_at_anchor(doc, text, anchor)
        mapper.apply_host_size(host_pt)
        n_glyphs = len(mapper.glyphs_for_marks(_marks)) if _marks else 1
        _style_frame_text(frame.getText(), mapper)
        _set_frame_insets_zero(frame)
        _configure_frame(frame, mapper)
        _apply_frame_dimensions(frame, mapper, n_glyphs)
        mapper.clear_runtime_size()
        count += 1
    return count


def _iter_frames(doc):
    try:
        frames = doc.getTextFrames()
    except Exception:
        return
    if frames is None:
        return
    for i in range(frames.getCount()):
        try:
            frame = frames.getByIndex(i)
            desc = frame.getPropertyValue("Description")
        except Exception:
            continue
        marks = _decode_desc(desc)
        if marks is not None:
            yield frame, marks


def _range_contains(work_range, point_range):
    try:
        ws, ps = work_range.getStart(), point_range.getStart()
        we, pe = work_range.getEnd(), point_range.getEnd()
        if work_range.compareRegionStarts(ws, ps) > 0:
            return False
        if work_range.compareRegionEnds(we, pe) < 0:
            return False
        return True
    except Exception:
        return True


def _show_source(doc, work_range):
    text = doc.Text
    to_restore = []
    for frame, marks in _iter_frames(doc):
        try:
            anchor = frame.getAnchor()
        except Exception:
            continue
        if _range_contains(work_range, anchor):
            to_restore.append((frame, marks))
    count = 0
    for frame, marks in to_restore:
        cursor = text.createTextCursorByRange(frame.getAnchor())
        text.insertString(cursor, marks, False)
        text.removeTextContent(frame)
        count += 1
    return count


def _work_range(doc):
    """Non-empty selection, else the whole document."""
    work = _get_selection_range(doc)
    if work is not None:
        return work
    return _get_document_range(doc)


def _char_index_in_range(work_range, position):
    """Character offset of position from the start of work_range."""
    text = work_range.getText()
    start = work_range.getStart()
    cur = text.createTextCursorByRange(start)
    cur.gotoRange(position, True)
    return len(cur.getString())


def _canonical_text_in_range(doc, work_range):
    """
    Unicode source for export: plain text plus marks from marinaMoji frames in range.
    """
    parts = []
    try:
        enum = work_range.createEnumeration()
        while enum.hasMoreElements():
            portion = enum.nextElement()
            ptype = portion.TextPortionType
            if ptype == "Text":
                parts.append(portion.getString())
            elif ptype == "Frame":
                frame = portion.TextFrame
                marks = _decode_desc(frame.getPropertyValue("Description"))
                if marks:
                    parts.append(marks)
                else:
                    parts.append(portion.getString())
            else:
                parts.append(portion.getString())
        return "".join(parts)
    except Exception:
        pass

    plain = work_range.getString()
    inserts = []
    for frame, marks in _iter_frames(doc):
        try:
            anchor = frame.getAnchor()
        except Exception:
            continue
        if not _range_contains(work_range, anchor):
            continue
        inserts.append((_char_index_in_range(work_range, anchor), marks))
    if not inserts:
        return plain
    inserts.sort()
    out = []
    pos = 0
    for idx, marks in inserts:
        if idx > len(plain):
            idx = len(plain)
        out.append(plain[pos:idx])
        out.append(marks)
        pos = idx + (1 if idx < len(plain) else 0)
    out.append(plain[pos:])
    return "".join(out)


def _canonical_text_for_export(doc):
    work = _work_range(doc)
    text = _canonical_text_in_range(doc, work)
    if not text.strip():
        return None
    return text


def _text_transferable(text):
    """XTransferable for plain text (LO expects utf-16 flavor on macOS)."""
    import unohelper
    from com.sun.star.datatransfer import DataFlavor, XTransferable

    flavors = []
    for mime in ("text/plain;charset=utf-16", "text/plain;charset=utf-8", "text/plain"):
        df = DataFlavor()
        df.MimeType = mime
        df.HumanPresentableName = "Text"
        df.DataType = uno.getTypeByName("string")
        flavors.append(df)

    class StringTransferable(unohelper.Base, XTransferable):
        def getTransferDataFlavors(self):
            return tuple(flavors)

        def isDataFlavorSupported(self, flavor):
            return any(f.MimeType == flavor.MimeType for f in flavors)

        def getTransferData(self, flavor):
            if self.isDataFlavorSupported(flavor):
                return text
            raise RuntimeError("unsupported flavor: %s" % flavor.MimeType)

    return StringTransferable()


def _clipboard_set_uno(text):
    try:
        ctx = uno.getComponentContext()
        sm = ctx.ServiceManager
        transferable = _text_transferable(text)
        for service in (
            "com.sun.star.datatransfer.clipboard.SystemClipboard",
            "com.sun.star.datatransfer.clipboard.Clipboard",
        ):
            try:
                clipboard = sm.createInstanceWithContext(service, ctx)
                if clipboard is not None:
                    clipboard.setContents(transferable, None)
                    return True
            except Exception:
                continue
        try:
            toolkit = sm.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
            clipboard = toolkit.getSystemClipboard()
            clipboard.setContents(transferable, None)
            return True
        except Exception:
            pass
    except Exception:
        pass
    return False


def _clipboard_set_subprocess(text):
    """OS clipboard when UNO clipboard is unavailable (common on macOS LO)."""
    payload = text.encode("utf-8")
    if sys.platform == "darwin":
        cmds = (["/usr/bin/pbcopy"], ["pbcopy"])
    elif sys.platform.startswith("linux"):
        cmds = (
            ["wl-copy"],
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
        )
    else:
        return False
    for cmd in cmds:
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                env={"LANG": "en_US.UTF-8"},
            )
            proc.communicate(payload)
            if proc.returncode == 0:
                return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False


def _clipboard_set_text(text):
    if _clipboard_set_uno(text):
        return True
    return _clipboard_set_subprocess(text)


def _export_is_full_document(doc):
    return _get_selection_range(doc) is None


def _render_in_scope(doc, work_range, mapper):
    n_new = _format_clusters(doc.Text, work_range, mapper, doc)
    n_updated = _refresh_frames_in_place(doc, work_range, mapper)
    return n_new, n_updated


def render_kaeriten(*_args):
    # LO toolbar/menu may pass one script-framework argument; ignore it.
    try:
        doc = _get_document()
    except RuntimeError:
        return
    work = _work_range(doc)
    mapper = _MarkMapper()
    _render_in_scope(doc, work, mapper)


def unrender_kaeriten(*_args):
    # LO toolbar/menu may pass one script-framework argument; ignore it.
    try:
        doc = _get_document()
    except RuntimeError:
        return
    work = _work_range(doc)
    _show_source(doc, work)


def copy_plain_text(*_args):
    if _plain_text_export is None:
        return
    try:
        doc = _get_document()
    except RuntimeError:
        return
    text = _canonical_text_for_export(doc)
    if text is None:
        return
    _clipboard_set_text(_plain_text_export(text))


def export_tei(*_args):
    if _tei_clipboard is None:
        return
    try:
        doc = _get_document()
    except RuntimeError:
        return
    text = _canonical_text_for_export(doc)
    if text is None:
        return
    try:
        payload = _tei_clipboard(text, full_document=False)
        _clipboard_set_text(payload)
    except Exception:
        pass


def export_latex(*_args):
    if _latex_clipboard is None:
        return
    try:
        doc = _get_document()
    except RuntimeError:
        return
    text = _canonical_text_for_export(doc)
    if text is None:
        return
    try:
        mapping = _load_mapping()
        payload = _latex_clipboard(
            text, mapping_data=mapping, full_document=False
        )
        _clipboard_set_text(payload)
    except Exception:
        pass


# Legacy names (older menu URLs and saved macro shortcuts)
format_selection = render_kaeriten
format_paragraph = render_kaeriten
format_document = render_kaeriten
refresh_rendering = render_kaeriten
show_source = unrender_kaeriten


g_exportedScripts = (
    render_kaeriten,
    unrender_kaeriten,
    copy_plain_text,
    export_tei,
    export_latex,
    format_selection,
    format_paragraph,
    format_document,
    refresh_rendering,
    show_source,
)
