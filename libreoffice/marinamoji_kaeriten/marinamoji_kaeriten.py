# -*- coding: utf-8 -*-
"""
marinaMoji Kaeriten — LibreOffice Writer (single-file macro module).
Render / unrender kaeriten: 說㆒㆑者 ↔ anchored frames. Scope: selection or whole document.
Shipped in the .oxt as a UNO Job (toolbar/menu) and optionally copied to user/Scripts/python by install.sh.
"""

import json
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from collections import namedtuple
from xml.sax.saxutils import escape as _xml_escape

import uno

try:
    from export_core import export_plain_text as _plain_text_export
except ImportError:
    _plain_text_export = None

# UNO enums at module level (after import uno), same pattern as LO TableSample.py
try:
    from com.sun.star.text.TextContentAnchorType import AS_CHARACTER
    from com.sun.star.text.VertOrientation import CHAR_BOTTOM as _VERT_CHAR_BOTTOM
    from com.sun.star.text.VertOrientation import CHAR_TOP as _VERT_CHAR_TOP
    from com.sun.star.text.VertOrientation import CHAR_CENTER as _VERT_CHAR_CENTER
    from com.sun.star.text.WrapTextMode import NONE as _WRAP_NONE
    from com.sun.star.style.LineSpacingMode import FIX as _LINE_FIX
    from com.sun.star.drawing.TextVerticalAdjust import BOTTOM as _TEXT_VERT_BOTTOM
    from com.sun.star.drawing.TextVerticalAdjust import CENTER as _TEXT_VERT_CENTER
    from com.sun.star.drawing.TextHorizontalAdjust import CENTER as _TEXT_HORIZ_CENTER
except ImportError:
    AS_CHARACTER = 1
    _VERT_CHAR_BOTTOM = 6
    _VERT_CHAR_TOP = 4
    _VERT_CHAR_CENTER = 5
    _WRAP_NONE = 0
    _LINE_FIX = 2
    _TEXT_VERT_BOTTOM = 2
    _TEXT_VERT_CENTER = 1
    _TEXT_HORIZ_CENTER = 1

# Vertical (縦書き) paragraph/page WritingMode2 values: TB_RL=2, TB_LR=3.
_VERTICAL_WRITING_MODES = (2, 3)
_WRITING_LR_TB = 0
_WRITING_TB_RL = 2
# Frame WritingMode for 縦書き frames so their own text stacks top→bottom
# (one column, no line breaks between compound glyphs). TB_RL = 2.
_FRAME_WRITING_TB_RL = _WRITING_TB_RL
# 1 pt = 0.3527…mm → 1/100 mm conversion for flush (em-tight) vertical sizing.
_PT_TO_HMM = 35.2778

# Map mapping.json names → VertOrientation constants. In 縦書き the as-character
# frame's VertOrient controls the *horizontal* side of the column (axis rotates).
_VERT_ORIENT_BY_NAME = {
    "char_bottom": _VERT_CHAR_BOTTOM,
    "char_top": _VERT_CHAR_TOP,
    "char_center": _VERT_CHAR_CENTER,
}

_CLUSTER_RE = re.compile(r"([^\u3190-\u319f\s])([\u3190-\u319f]+)")
_MARKS_RE = re.compile(r"[\u3190-\u319f]+")
_SOURCE_PREFIX = "MARINAMOJI:source="
_KaeritenCluster = namedtuple("KaeritenCluster", ("base_char", "marks", "start", "end"))
_GRAPHIC_NAME = "marinaMoji_kaeriten_image"


def _marks_start(cluster):
    return cluster.start + len(cluster.base_char)


def _find_clusters(text):
    out = []
    for match in _CLUSTER_RE.finditer(text):
        out.append(_KaeritenCluster(match.group(1), match.group(2), match.start(), match.end()))
    return out


def _sort_clusters(clusters):
    return sorted(clusters, key=lambda c: c.start, reverse=True)


def _short_hash(data):
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def _safe_meta_value(value):
    return str(value).replace(";", "_").replace("|", "_").replace("=", "_")


def _encode_desc(marks, fingerprint=None):
    desc = _SOURCE_PREFIX + marks
    if fingerprint:
        desc += ";fp=" + str(fingerprint).replace(";", "_")
    return desc


def _desc_fields(description):
    if not description or not description.startswith(_SOURCE_PREFIX):
        return None, None
    body = description[len(_SOURCE_PREFIX) :]
    marks, _sep, rest = body.partition(";")
    fp = None
    for field in rest.split(";"):
        if field.startswith("fp="):
            fp = field[3:]
            break
    return marks, fp


def _decode_desc(description):
    marks, _fp = _desc_fields(description)
    return marks


def _decode_fp(description):
    _marks, fp = _desc_fields(description)
    return fp


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
        rendering = data.get("rendering", {})
        self._lo_primary = str(rendering.get("libreoffice_primary", "anchored_frame")).lower()
        lo = rendering.get("libreoffice_frame", {})
        word_img = rendering.get("word_inline_picture", {})
        lo_img = rendering.get("libreoffice_image", {})
        self._rendering_hash = _short_hash(
            {
                "version": data.get("version"),
                "libreoffice_primary": self._lo_primary,
                "libreoffice_frame": lo,
                "libreoffice_image": lo_img,
                "marks": data.get("marks", []),
            }
        )
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
        # 縦書き: which side of the column the marks sit on, plus an optional nudge.
        # Default char_bottom → left of the column (traditional kanbun: kaeriten
        # on the reader's left; okurigana stays on the right). char_top → right.
        self._vertical_vert_orient_name = str(
            lo.get("vertical_vert_orient", "char_bottom")
        ).lower()
        self._vertical_orient_position_hmm = lo.get(
            "vertical_orient_position_hmm", 0
        )
        if isinstance(self._vertical_orient_position_hmm, float):
            self._vertical_orient_position_hmm = int(
                round(self._vertical_orient_position_hmm * 100)
            )
        else:
            self._vertical_orient_position_hmm = int(self._vertical_orient_position_hmm)
        self._frame_width_hmm = int(lo.get("frame_width_hmm", 180))
        self._line_height_twips = int(lo.get("line_height_twips", 0))  # 0 = auto from font
        # 縦書き box sizing (em-relative). Width is the column thickness (a touch
        # over 1 em so the glyph isn't clipped on the right); height is em-tight per
        # glyph so the box hugs the marks. glyph_kern_hmm < 0 pulls stacked compound
        # marks (㆒ above ㆑) closer together (applied as CharKerning).
        self._vertical_box_width_factor = float(lo.get("vertical_box_width_factor", 1.18))
        self._vertical_box_height_factor = float(lo.get("vertical_box_height_factor", 1.0))
        self._vertical_box_pad_hmm = int(lo.get("vertical_box_pad_hmm", 0))
        self._vertical_glyph_kern_hmm = int(lo.get("vertical_glyph_kern_hmm", -40))
        self._image_glyph_ratio = float(lo_img.get("glyph_ratio", word_img.get("glyph_ratio", 0.42)))
        self._image_compound_glyph_ratio = float(
            lo_img.get(
                "compound_glyph_ratio",
                word_img.get("compound_glyph_ratio", self._image_glyph_ratio),
            )
        )
        self._image_line_gap_ratio = float(lo_img.get("line_gap_ratio", word_img.get("line_gap_ratio", 0)))
        self._image_compound_line_gap_ratio = float(
            lo_img.get(
                "compound_line_gap_ratio",
                word_img.get("compound_line_gap_ratio", -0.15),
            )
        )
        self._image_compound_touch = bool(
            lo_img.get("compound_touch", word_img.get("compound_touch", False))
        )
        self._image_compound_touch_overlap_ratio = float(
            lo_img.get(
                "compound_touch_overlap_ratio",
                word_img.get("compound_touch_overlap_ratio", 0.72),
            )
        )
        self._image_glyph_fill = float(lo_img.get("glyph_fill", word_img.get("glyph_fill", 0.94)))
        self._image_color = str(lo_img.get("color", word_img.get("color", "#000000")))
        self._image_font_family = str(
            lo_img.get(
                "font_family",
                word_img.get(
                    "font_family",
                    '"Hiragino Mincho ProN","YuMincho","Yu Mincho","MS Mincho","Songti SC","SimSun",serif',
                ),
            )
        )
        self._image_background = lo_img.get("background", word_img.get("background", None))
        self._image_horizontal_vert_orient_position_hmm = int(
            lo_img.get("vert_orient_position_hmm", self._vert_orient_position_hmm)
        )
        self._image_vertical_orient_position_hmm = int(
            lo_img.get("vertical_orient_position_hmm", self._vertical_orient_position_hmm)
        )
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

    @property
    def vertical_vert_orient(self):
        return _VERT_ORIENT_BY_NAME.get(
            self._vertical_vert_orient_name, _VERT_CHAR_BOTTOM
        )

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

    def frame_text(self, marks, vertical=False):
        glyphs = self.glyphs_for_marks(marks)
        # Horizontal: the frame is a horizontal text box, so stack the compound
        # glyphs with newlines (一 over レ). Vertical: the frame itself flows
        # top→bottom, so the glyphs already stack in one column — a newline would
        # start a *second* column (the unwanted "line break"), so just join them.
        return "".join(glyphs) if vertical else "\n".join(glyphs)

    def vertical_box_hmm(self, n_glyphs):
        """Em-tight extent for a 縦書き frame, in 1/100 mm.

        width  = column thickness (~1 em, slightly over so the glyph isn't clipped)
        height = n ems down the column, minus the compound kerning, so the box
                 hugs the marks with no empty space below.
        """
        em = max(60, int(round(self.effective_char_height_pt * _PT_TO_HMM)))
        n = max(1, int(n_glyphs))
        width = int(round(em * self._vertical_box_width_factor)) + self._vertical_box_pad_hmm
        height = int(round(em * n * self._vertical_box_height_factor))
        height += self._vertical_glyph_kern_hmm * (n - 1) + self._vertical_box_pad_hmm
        height = max(em // 2, height)
        return width, height

    @property
    def vertical_line_twips(self):
        """Column thickness inside a 縦書き frame; matches the box width."""
        return int(round(self.effective_char_height_pt * 20 * self._vertical_box_width_factor))

    @property
    def use_image_renderer(self):
        return self._lo_primary in ("inline_image", "image", "svg_image", "graphic")


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


def _char_font_from_props(prop_set):
    for name in ("CharFontNameAsian", "CharFontName"):
        try:
            v = prop_set.getPropertyValue(name)
            if v:
                return str(v)
        except Exception:
            pass
    return None


def _char_font_from_style_family(doc, family_name, style_name):
    if not style_name:
        return None
    try:
        styles = doc.getStyleFamilies().getByName(family_name)
        style = styles.getByName(style_name)
        return _char_font_from_props(style)
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


def _resolve_char_font_name(doc, cursor):
    font = _char_font_from_props(cursor)
    if font:
        return font
    try:
        font = _char_font_from_style_family(
            doc, "CharacterStyles", cursor.getPropertyValue("CharStyleName")
        )
        if font:
            return font
    except Exception:
        pass
    try:
        font = _char_font_from_style_family(
            doc, "ParagraphStyles", cursor.getPropertyValue("ParaStyleName")
        )
        if font:
            return font
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


def _host_char_font(doc, text, cursor_at_marks):
    """Font family of the kanji before kaeriten marks (or paragraph default)."""
    host = text.createTextCursorByRange(cursor_at_marks)
    try:
        if host.goLeft(1, False):
            host.goRight(1, True)
            font = _resolve_char_font_name(doc, host)
            if font:
                return font
    except Exception:
        pass
    try:
        para = text.createTextCursorByRange(cursor_at_marks)
        para.gotoStartOfParagraph(False)
        font = _resolve_char_font_name(doc, para)
        if font:
            return font
    except Exception:
        pass
    return ""


def _host_char_font_at_anchor(doc, text, anchor):
    return _host_char_font(doc, text, text.createTextCursorByRange(anchor))


def _page_style_is_vertical(doc, name):
    """True when the named page style uses a vertical WritingMode."""
    if not name:
        return False
    try:
        page = doc.getStyleFamilies().getByName("PageStyles").getByName(name)
        return page.getPropertyValue("WritingMode") in _VERTICAL_WRITING_MODES
    except Exception:
        return False


def _current_page_style(doc):
    """Return the active page style object for the current cursor/page."""
    name = None
    try:
        name = doc.getCurrentController().getViewCursor().getPropertyValue(
            "PageStyleName"
        )
    except Exception:
        name = None
    if not name:
        try:
            work = _work_range(doc)
            cursor = doc.Text.createTextCursorByRange(work.getStart())
            name = cursor.getPropertyValue("PageStyleName")
        except Exception:
            name = None
    if not name:
        return None, None
    try:
        page = doc.getStyleFamilies().getByName("PageStyles").getByName(name)
        return name, page
    except Exception:
        return name, None


def _refresh_rendered_views(doc):
    """Refresh only existing rendered views; do not render new source marks."""
    work = _get_document_range(doc)
    mapper = _MarkMapper()
    _refresh_frames_in_place(doc, work, mapper)
    _refresh_graphics_in_place(doc, work, mapper)


def toggle_page_writing_mode(*_args):
    """Toggle current page style between horizontal LR_TB and vertical TB_RL."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    _name, page = _current_page_style(doc)
    if page is None:
        return
    try:
        current = page.getPropertyValue("WritingMode")
    except Exception:
        current = _WRITING_LR_TB
    next_mode = _WRITING_LR_TB if current in _VERTICAL_WRITING_MODES else _WRITING_TB_RL
    try:
        page.setPropertyValue("WritingMode", next_mode)
    except Exception:
        return
    _refresh_rendered_views(doc)


def _is_vertical_writing(doc, cursor):
    """
    Detect 縦書き at a paragraph cursor.

    Paragraphs usually inherit direction from the page (WritingMode = CONTEXT/PAGE),
    so we check the paragraph's own WritingMode first, then fall back to the page
    style (named on the paragraph, else the current view cursor's page).
    """
    try:
        wm = cursor.getPropertyValue("WritingMode")
        if wm in _VERTICAL_WRITING_MODES:
            return True
        if wm in (0, 1):  # LR_TB / RL_TB → explicitly horizontal
            return False
    except Exception:
        pass

    name = None
    try:
        name = cursor.getPropertyValue("PageStyleName")
    except Exception:
        name = None
    if not name:
        try:
            name = doc.getCurrentController().getViewCursor().getPropertyValue(
                "PageStyleName"
            )
        except Exception:
            name = None
    return _page_style_is_vertical(doc, name)


def _render_fingerprint(doc, text, anchor, marks, mapper, vertical=None, host_pt=None):
    """Fingerprint the host style + renderer settings that affect rendered views."""
    if host_pt is None:
        host_pt = _host_char_height_at_anchor(doc, text, anchor)
    host = float(host_pt) if host_pt and host_pt > 0 else 12.0
    if vertical is None:
        vertical = _is_vertical_writing(doc, text.createTextCursorByRange(anchor))
    font = _host_char_font_at_anchor(doc, text, anchor)
    renderer = "image" if mapper.use_image_renderer else "frame"
    return "|".join(
        (
            "v1",
            "renderer=%s" % renderer,
            "pt=%.1f" % host,
            "vert=%d" % (1 if vertical else 0),
            "font=%s" % _safe_meta_value(font),
            "rh=%s" % mapper._rendering_hash,
        )
    )


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


def _apply_frame_dimensions(frame, mapper, n_glyphs, vertical=False):
    """Set width/height from host-scaled metrics (not stale LayoutSize alone)."""
    if vertical:
        # 縦書き: fix the box to an em-tight extent so it hugs the marks with no
        # empty space below (the column-advance is the frame Height here).
        w, h = mapper.vertical_box_hmm(n_glyphs)
        frame.setPropertyValue("FrameIsAutomaticHeight", False)
        frame.setPropertyValue("Width", w)
        frame.setPropertyValue("Height", h)
        _set_frame_content_align(frame, vertical)
        return
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
    _set_frame_content_align(frame, vertical)


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


def _style_frame_text(frame_text, mapper, vertical=False):
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
    if vertical:
        # Pull stacked compound glyphs (㆒ above ㆑) closer along the column.
        try:
            cursor.setPropertyValue("CharKerning", mapper._vertical_glyph_kern_hmm)
        except Exception:
            pass
    # 縦書き: the single column's *thickness* (across the column) is the line
    # height, so pin it to ~one em to match the box width and avoid right clipping.
    line_twips = mapper.vertical_line_twips if vertical else _line_spacing_twips(mapper, h)
    try:
        ls = uno.createUnoStruct("com.sun.star.style.LineSpacing")
        ls.Mode = _LINE_FIX
        ls.Height = line_twips
        cursor.setPropertyValue("ParaLineSpacing", ls)
    except Exception:
        pass


def _set_frame_content_align(frame, vertical=False):
    """Stack sits on the bottom of the frame (kaeriten on the line).

    For 縦書き the frame is em-tight in both axes, so center the glyphs to keep
    them flush instead of bottom-anchoring (which would shove them to one edge).
    """
    try:
        vadj = _TEXT_VERT_CENTER if vertical else _TEXT_VERT_BOTTOM
        frame.setPropertyValue("TextVerticalAdjust", vadj)
        frame.setPropertyValue("TextHorizontalAdjust", _TEXT_HORIZ_CENTER)
    except Exception:
        pass


def _pt_to_hmm(pt):
    return max(1, int(round(float(pt) * _PT_TO_HMM)))


def _image_metrics_from_host(mapper, glyph_count):
    """Word-style painted cluster metrics, in points.

    `compound_touch` changes the glyph-to-glyph advance in the drawing itself,
    so LibreOffice text kerning/line-breaking cannot force レ into another column.
    """
    host_pt = mapper.effective_char_height_pt / mapper._font_size_ratio
    host_pt = host_pt if host_pt and host_pt > 0 else 12.0
    n = max(1, int(glyph_count))
    compound = n > 1
    ratio = mapper._image_compound_glyph_ratio if compound else mapper._image_glyph_ratio
    cell_pt = max(1.0, host_pt * ratio)
    gap_ratio = mapper._image_compound_line_gap_ratio if compound else mapper._image_line_gap_ratio
    gap_pt = cell_pt * gap_ratio
    if compound and mapper._image_compound_touch:
        gap_pt = -cell_pt * mapper._image_compound_touch_overlap_ratio
    width_pt = cell_pt
    height_pt = max(cell_pt * 0.5, cell_pt * n + gap_pt * (n - 1))
    return {
        "cell_pt": cell_pt,
        "gap_pt": gap_pt,
        "width_pt": width_pt,
        "height_pt": height_pt,
    }


def _svg_for_marks(marks, mapper):
    glyphs = mapper.glyphs_for_marks(marks)
    metrics = _image_metrics_from_host(mapper, len(glyphs))
    width = metrics["width_pt"]
    height = metrics["height_pt"]
    cell = metrics["cell_pt"]
    gap = metrics["gap_pt"]
    font_size = cell * mapper._image_glyph_fill
    family = _xml_escape(mapper._image_font_family, {'"': "&quot;"})
    color = _xml_escape(mapper._image_color)
    bg = mapper._image_background
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="%.3fpt" height="%.3fpt" viewBox="0 0 %.3f %.3f">' % (width, height, width, height),
    ]
    if bg:
        parts.append(
            '<rect x="0" y="0" width="%.3f" height="%.3f" fill="%s"/>' %
            (width, height, _xml_escape(str(bg)))
        )
    parts.append(
        '<g fill="%s" font-family="%s" font-size="%.3f" '
        'text-anchor="middle" dominant-baseline="text-after-edge">' %
        (color, family, font_size)
    )
    for i, glyph in enumerate(glyphs):
        stack_from_bottom = len(glyphs) - 1 - i
        x = cell / 2.0
        y = height - (cell + gap) * stack_from_bottom
        parts.append(
            '<text x="%.3f" y="%.3f">%s</text>' %
            (x, y, _xml_escape(str(glyph)))
        )
    parts.append("</g></svg>")
    return "\n".join(parts), metrics


def _image_cache_dir():
    path = os.path.join(tempfile.gettempdir(), "marinamoji_kaeriten")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def _write_marks_svg(marks, mapper):
    svg, metrics = _svg_for_marks(marks, mapper)
    # Keep a short deterministic-ish name for easier debugging; include metrics so
    # the same marks at different host sizes/touch settings don't share a link.
    safe = "".join("%04x" % ord(ch) for ch in marks)
    key = "%s_%03d_%03d_%+04d" % (
        safe,
        int(round(metrics["width_pt"] * 100)),
        int(round(metrics["height_pt"] * 100)),
        int(round(metrics["gap_pt"] * 100)),
    )
    path = os.path.join(_image_cache_dir(), "kaeriten_%s.svg" % key)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path, metrics


def _prop(name, value):
    p = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    p.Name = name
    p.Value = value
    return p


def _graphic_from_url(file_url):
    try:
        ctx = uno.getComponentContext()
        provider = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.graphic.GraphicProvider", ctx
        )
        return provider.queryGraphic((_prop("URL", file_url),))
    except Exception:
        return None


def _set_text_content_desc(obj, marks, fingerprint=None):
    desc = _encode_desc(marks, fingerprint)
    for name, value in (
        ("Description", desc),
        ("Title", _GRAPHIC_NAME),
        ("Name", _GRAPHIC_NAME),
    ):
        try:
            obj.setPropertyValue(name, value)
        except Exception:
            pass


def _marks_from_text_content(obj):
    for name in ("Description", "AlternativeText"):
        try:
            marks = _decode_desc(obj.getPropertyValue(name))
            if marks is not None:
                return marks
        except Exception:
            pass
    return None


def _fingerprint_from_text_content(obj):
    for name in ("Description", "AlternativeText"):
        try:
            fp = _decode_fp(obj.getPropertyValue(name))
            if fp is not None:
                return fp
        except Exception:
            pass
    return None


def _set_graphic_margins_zero(graphic):
    """Clear spacing around image views; the SVG itself controls visual spacing."""
    for name in ("LeftMargin", "RightMargin", "TopMargin", "BottomMargin"):
        try:
            graphic.setPropertyValue(name, 0)
        except Exception:
            pass


def _configure_graphic(graphic, mapper, metrics, vertical=False):
    graphic.setPropertyValue("AnchorType", AS_CHARACTER)
    _set_graphic_margins_zero(graphic)
    graphic.setPropertyValue("Width", _pt_to_hmm(metrics["width_pt"]))
    graphic.setPropertyValue("Height", _pt_to_hmm(metrics["height_pt"]))
    try:
        graphic.setPropertyValue("Surround", _WRAP_NONE)
        graphic.setPropertyValue("TextWrap", _WRAP_NONE)
    except Exception:
        pass
    try:
        if vertical:
            graphic.setPropertyValue("VertOrient", mapper.vertical_vert_orient)
            graphic.setPropertyValue(
                "VertOrientPosition", mapper._image_vertical_orient_position_hmm
            )
        else:
            graphic.setPropertyValue("VertOrient", _VERT_CHAR_BOTTOM)
            graphic.setPropertyValue(
                "VertOrientPosition", mapper._image_horizontal_vert_orient_position_hmm
            )
    except Exception:
        pass


def _insert_graphic(text, cursor, marks, mapper, doc, vertical=False, fingerprint=None):
    path, metrics = _write_marks_svg(marks, mapper)
    url = uno.systemPathToFileUrl(path)
    graphic = doc.createInstance("com.sun.star.text.TextGraphicObject")
    _configure_graphic(graphic, mapper, metrics, vertical)
    _set_text_content_desc(graphic, marks, fingerprint)
    loaded = _graphic_from_url(url)
    if loaded is not None:
        try:
            graphic.setPropertyValue("Graphic", loaded)
        except Exception:
            graphic.setPropertyValue("GraphicURL", url)
    else:
        graphic.setPropertyValue("GraphicURL", url)
    text.insertTextContent(cursor, graphic, False)
    # Some LO versions reapply defaults after insertion; reassert metadata/layout.
    _set_text_content_desc(graphic, marks, fingerprint)
    _configure_graphic(graphic, mapper, metrics, vertical)


def _configure_frame(frame, mapper, vertical=False):
    frame.setPropertyValue("AnchorType", AS_CHARACTER)
    frame.setPropertyValue("FrameIsAutomaticHeight", True)
    _set_borderless(frame)
    _set_frame_insets_zero(frame)
    _set_frame_content_align(frame, vertical)
    frame.setPropertyValue("Width", mapper.effective_frame_width_hmm())
    try:
        frame.setPropertyValue("Surround", _WRAP_NONE)
        frame.setPropertyValue("TextWrap", _WRAP_NONE)
    except Exception:
        pass
    try:
        # Force the frame's own text to flow top→bottom in 縦書き so compound
        # glyphs stack in one column (no second-column "line break").
        frame.setPropertyValue(
            "WritingMode", _FRAME_WRITING_TB_RL if vertical else 0
        )
    except Exception:
        pass
    try:
        if vertical:
            # 縦書き: the perpendicular (VertOrient) axis is horizontal, so this
            # chooses the column side. char_bottom → left (traditional kaeriten).
            frame.setPropertyValue("VertOrient", mapper.vertical_vert_orient)
            frame.setPropertyValue(
                "VertOrientPosition", mapper._vertical_orient_position_hmm
            )
        else:
            # BOTTOM (3) anchors to page/line box and sits too low; CHAR_BOTTOM (6) uses the glyph.
            frame.setPropertyValue("VertOrient", _VERT_CHAR_BOTTOM)
            frame.setPropertyValue(
                "VertOrientPosition", mapper._vert_orient_position_hmm
            )
    except Exception:
        pass


def _insert_frame(text, cursor, marks, mapper, doc, vertical=False, fingerprint=None):
    frame = doc.createInstance("com.sun.star.text.TextFrame")
    _configure_frame(frame, mapper, vertical)
    frame.setPropertyValue("Description", _encode_desc(marks, fingerprint))
    try:
        frame.setPropertyValue("Name", _FRAME_NAME)
    except Exception:
        pass
    text.insertTextContent(cursor, frame, False)
    ft = frame.getText()
    fc = ft.createTextCursor()
    ft.insertString(fc, mapper.frame_text(marks, vertical), False)
    _style_frame_text(ft, mapper, vertical)
    # LO may reapply frame style defaults on insert — clear insets, align, size.
    _set_frame_insets_zero(frame)
    _configure_frame(frame, mapper, vertical)
    n_glyphs = len(mapper.glyphs_for_marks(marks))
    _apply_frame_dimensions(frame, mapper, n_glyphs, vertical)


def _insert_view(text, cursor, marks, mapper, doc, vertical=False, fingerprint=None):
    if mapper.use_image_renderer:
        _insert_graphic(text, cursor, marks, mapper, doc, vertical, fingerprint)
    else:
        _insert_frame(text, cursor, marks, mapper, doc, vertical, fingerprint)


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


def _collect_mark_runs(text, work_range):
    """Live cursors at each kaeriten run in the *body* text within work_range.

    We enumerate paragraphs → text portions instead of doing offset arithmetic on
    work_range.getString(). An as-character frame is its own ("Frame") portion and
    contributes no characters to getString(), yet cursor.goRight() counts it as one
    position — so once a kaeriten is rendered, string offsets desync from cursor
    motion and later marks land in the wrong place (or get skipped). Walking text
    portions keeps each goRight inside a single, frame-free run, so positions stay
    correct no matter how many frames already exist.
    """
    runs = []
    try:
        para_enum = text.createEnumeration()
    except Exception:
        return runs
    while para_enum.hasMoreElements():
        para = para_enum.nextElement()
        try:
            if not para.supportsService("com.sun.star.text.Paragraph"):
                continue
            portion_enum = para.createEnumeration()
        except Exception:
            continue
        while portion_enum.hasMoreElements():
            try:
                portion = portion_enum.nextElement()
                if portion.TextPortionType != "Text":
                    continue
                s = portion.getString()
            except Exception:
                continue
            for m in _MARKS_RE.finditer(s):
                try:
                    start = text.createTextCursorByRange(portion.getStart())
                    if m.start() > 0:
                        start.goRight(m.start(), False)
                except Exception:
                    continue
                if not _range_contains(work_range, start):
                    continue
                runs.append((start, m.group(0)))
    return runs


def _format_clusters(text, work_range, mapper, doc):
    count = 0
    # Process last→first so removing/inserting earlier in the doc doesn't shift the
    # live cursors we still need to handle.
    for start, marks in reversed(_collect_mark_runs(text, work_range)):
        base = text.createTextCursorByRange(start)
        if not base.goLeft(1, True):
            continue
        base_char = base.getString()
        if not base_char or _MARKS_RE.match(base_char) or base_char.isspace():
            continue  # orphan marks with no kanji to attach to
        host_pt = _host_char_height(doc, text, start)
        mapper.apply_host_size(host_pt)
        vertical = _is_vertical_writing(doc, start)
        fingerprint = _render_fingerprint(
            doc, text, start, marks, mapper, vertical=vertical, host_pt=host_pt
        )
        run = text.createTextCursorByRange(start)
        run.goRight(len(marks), True)
        insert_at = text.createTextCursorByRange(start)
        run.setString("")
        _insert_view(text, insert_at, marks, mapper, doc, vertical, fingerprint)
        mapper.clear_runtime_size()
        count += 1
    return count


def _refresh_frames_in_place(doc, work_range, mapper):
    """Update existing frames, or convert them to images when image rendering is primary."""
    text = doc.Text
    count = 0
    for frame, _marks in list(_iter_frames(doc)):
        try:
            anchor = frame.getAnchor()
        except Exception:
            continue
        if not _range_contains(work_range, anchor):
            continue
        host_pt = _host_char_height_at_anchor(doc, text, anchor)
        mapper.apply_host_size(host_pt)
        vertical = _is_vertical_writing(
            doc, text.createTextCursorByRange(anchor)
        )
        fingerprint = _render_fingerprint(
            doc, text, anchor, _marks, mapper, vertical=vertical, host_pt=host_pt
        )
        if mapper.use_image_renderer:
            try:
                cursor = text.createTextCursorByRange(anchor)
                _insert_graphic(text, cursor, _marks, mapper, doc, vertical, fingerprint)
                text.removeTextContent(frame)
                count += 1
            except Exception:
                pass
            mapper.clear_runtime_size()
            continue
        try:
            if _decode_fp(frame.getPropertyValue("Description")) == fingerprint:
                mapper.clear_runtime_size()
                continue
        except Exception:
            pass
        n_glyphs = len(mapper.glyphs_for_marks(_marks)) if _marks else 1
        ft = frame.getText()
        if _marks:
            # Rewrite content so direction changes (and the no-linebreak rule for
            # vertical compounds) apply to frames rendered before this fix.
            try:
                ft.setString(mapper.frame_text(_marks, vertical))
            except Exception:
                pass
        _style_frame_text(ft, mapper, vertical)
        _set_frame_insets_zero(frame)
        _configure_frame(frame, mapper, vertical)
        _apply_frame_dimensions(frame, mapper, n_glyphs, vertical)
        try:
            frame.setPropertyValue("Description", _encode_desc(_marks, fingerprint))
        except Exception:
            pass
        mapper.clear_runtime_size()
        count += 1
    return count


def _refresh_graphics_in_place(doc, work_range, mapper):
    """Redraw existing image views from source marks and current host size."""
    text = doc.Text
    count = 0
    for graphic, marks in _iter_graphics(doc):
        try:
            anchor = graphic.getAnchor()
        except Exception:
            continue
        if not _range_contains(work_range, anchor):
            continue
        host_pt = _host_char_height_at_anchor(doc, text, anchor)
        mapper.apply_host_size(host_pt)
        vertical = _is_vertical_writing(
            doc, text.createTextCursorByRange(anchor)
        )
        fingerprint = _render_fingerprint(
            doc, text, anchor, marks, mapper, vertical=vertical, host_pt=host_pt
        )
        if _fingerprint_from_text_content(graphic) == fingerprint:
            mapper.clear_runtime_size()
            continue
        path, metrics = _write_marks_svg(marks, mapper)
        url = uno.systemPathToFileUrl(path)
        loaded = _graphic_from_url(url)
        if loaded is not None:
            try:
                graphic.setPropertyValue("Graphic", loaded)
            except Exception:
                graphic.setPropertyValue("GraphicURL", url)
        else:
            graphic.setPropertyValue("GraphicURL", url)
        _set_text_content_desc(graphic, marks, fingerprint)
        _configure_graphic(graphic, mapper, metrics, vertical)
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


def _iter_graphics(doc):
    try:
        graphics = doc.getGraphicObjects()
    except Exception:
        return
    if graphics is None:
        return
    for i in range(graphics.getCount()):
        try:
            graphic = graphics.getByIndex(i)
        except Exception:
            continue
        marks = _marks_from_text_content(graphic)
        if marks is not None:
            yield graphic, marks


def _iter_views(doc):
    for frame, marks in _iter_frames(doc):
        yield frame, marks
    for graphic, marks in _iter_graphics(doc):
        yield graphic, marks


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
    for view, marks in _iter_views(doc):
        try:
            anchor = view.getAnchor()
        except Exception:
            continue
        if _range_contains(work_range, anchor):
            to_restore.append((view, marks))
    count = 0
    for view, marks in to_restore:
        cursor = text.createTextCursorByRange(view.getAnchor())
        text.insertString(cursor, marks, False)
        text.removeTextContent(view)
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
            elif ptype in ("Graphic", "TextContent"):
                content = None
                for attr in ("TextContent", "TextGraphicObject"):
                    try:
                        content = getattr(portion, attr)
                        break
                    except Exception:
                        pass
                marks = _marks_from_text_content(content) if content is not None else None
                parts.append(marks if marks else portion.getString())
            else:
                parts.append(portion.getString())
        return "".join(parts)
    except Exception:
        pass

    plain = work_range.getString()
    inserts = []
    for view, marks in _iter_views(doc):
        try:
            anchor = view.getAnchor()
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
    n_updated += _refresh_graphics_in_place(doc, work_range, mapper)
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
    format_selection,
    format_paragraph,
    format_document,
    refresh_rendering,
    show_source,
)
