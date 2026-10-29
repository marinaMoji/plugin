# -*- coding: utf-8 -*-
"""
Fixed line distance vs ruby — does ruby inflate line pitch?

Creates H/V docs with:
  - Fixed ParaLineSpacing (absolute)
  - ParaVertAlignment BASELINE vs AUTOMATIC vs CENTER (Text-to-text)
  - Parallel paragraphs: plain body vs body with ruby

Entry returns None (UNO-safe).
"""

from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, timezone

import uno

# com.sun.star.style.LineSpacingMode
_LS_PROP = 0
_LS_MINIMUM = 1
_LS_LEADING = 2
_LS_FIX = 3  # absolute Height (not "4")

# com.sun.star.text.ParagraphVertAlign
_VA_AUTOMATIC = 0
_VA_BASELINE = 1
_VA_TOP = 2
_VA_CENTER = 3
_VA_BOTTOM = 4

BODY_PT = 14.0
# Fixed line pitch: 28 pt ≈ double body (room for half-size ruby in the gap)
FIXED_LINE_PT = 28.0


def _outdir():
    p = os.path.join(
        os.path.expanduser("~"),
        "Code",
        "marinaMoji",
        "plugin",
        "libreoffice",
        "spikes",
        "ruby",
        "artifacts",
        "line_spacing",
    )
    os.makedirs(p, exist_ok=True)
    return p


def _desktop():
    try:
        return XSCRIPTCONTEXT.getDesktop()  # noqa: F821
    except NameError:
        ctx = uno.getComponentContext()
        return ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx
        )


def _set(o, n, v):
    try:
        o.setPropertyValue(n, v)
        return True
    except Exception:
        return False


def _get(o, n, d=None):
    try:
        return o.getPropertyValue(n)
    except Exception:
        return d


def _ja():
    from com.sun.star.lang import Locale

    loc = Locale()
    loc.Language = "ja"
    loc.Country = "JP"
    return loc


def _pb():
    from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK

    return PARAGRAPH_BREAK


def _style_run(c, size=BODY_PT, font="Hiragino Mincho ProN"):
    _set(c, "CharLocaleAsian", _ja())
    _set(c, "CharFontNameAsian", font)
    _set(c, "CharFontName", font)
    _set(c, "CharHeightAsian", size)
    _set(c, "CharHeight", size)


def _fixed_spacing():
    """LineSpacing struct: Mode FIX; Height in 1/100 mm for FIX mode."""
    ls = uno.createUnoStruct("com.sun.star.style.LineSpacing")
    ls.Mode = _LS_FIX
    # pt → mm → 1/100 mm
    ls.Height = int(round(FIXED_LINE_PT * 25.4 / 72.0 * 100.0))
    return ls


def _append(text):
    c = text.createTextCursor()
    c.gotoEnd(False)
    if (text.getString() or "").strip():
        text.insertControlCharacter(c, _pb(), False)
        c.gotoEnd(False)
    return c


def _para_props(cursor, vert_align):
    ok_ls = _set(cursor, "ParaLineSpacing", _fixed_spacing())
    ok_va = _set(cursor, "ParaVertAlignment", vert_align)
    # Snap to grid off for this measurement (isolate fixed spacing)
    _set(cursor, "ParaSnapToGrid", False)
    return {
        "ParaLineSpacing_set": ok_ls,
        "ParaVertAlignment_set": ok_va,
        "ParaVertAlignment": _get(cursor, "ParaVertAlignment"),
        "ParaLineSpacing": _describe_ls(_get(cursor, "ParaLineSpacing")),
        "ParaSnapToGrid": _get(cursor, "ParaSnapToGrid"),
    }


def _describe_ls(ls):
    if ls is None:
        return None
    try:
        return {"Mode": int(ls.Mode), "Height": int(ls.Height)}
    except Exception:
        return str(ls)


def _save(doc, path):
    from com.sun.star.beans import PropertyValue

    if os.path.exists(path):
        os.remove(path)
    doc.storeAsURL(
        uno.systemPathToFileUrl(os.path.abspath(path)),
        (PropertyValue(Name="FilterName", Value="writer8"),),
    )


def _vertical(doc):
    from com.sun.star.text.WritingMode2 import RL_TB

    page = doc.StyleFamilies.getByName("PageStyles").getByName("Standard")
    return _set(page, "WritingMode", RL_TB)


def _insert_plain_block(text, vert_align, lines):
    """Several paragraphs / or one para with hard breaks? Use separate paras
    each with same fixed spacing — measures inter-paragraph? Better: one
    paragraph with LINE BREAKs so line pitch is within-para.

    Writer: insert Soft line? Use paragraph breaks with zero spacing above/below.
    """
    info = {"kind": "plain", "lines": []}
    for i, s in enumerate(lines):
        c = _append(text)
        text.insertString(c, s, True)
        _style_run(c)
        props = _para_props(c, vert_align)
        _set(c, "ParaTopMargin", 0)
        _set(c, "ParaBottomMargin", 0)
        if i == 0:
            info["para_props"] = props
        info["lines"].append(s)
        c.collapseToEnd()
    return info


def _insert_ruby_block(text, vert_align, lines_with_ruby):
    """lines_with_ruby: list of (plain_prefix, base, reading, plain_suffix)."""
    info = {"kind": "ruby", "lines": []}
    for i, (pre, base, reading, suf) in enumerate(lines_with_ruby):
        c = _append(text)
        if pre:
            text.insertString(c, pre, True)
            _style_run(c)
            c.collapseToEnd()
        text.insertString(c, base, True)
        _style_run(c)
        _set(c, "RubyText", reading)
        _set(c, "RubyAdjust", 0)  # LEFT — product default
        _set(c, "RubyPosition", 0)
        _set(c, "RubyAdjust", 0)
        c.collapseToEnd()
        if suf:
            text.insertString(c, suf, True)
            _style_run(c)
        # Apply para props to whole para: expand selection to para
        # Re-get paragraph cursor
        c.gotoStartOfParagraph(False)
        c.gotoEndOfParagraph(True)
        props = _para_props(c, vert_align)
        _set(c, "ParaTopMargin", 0)
        _set(c, "ParaBottomMargin", 0)
        if i == 0:
            info["para_props"] = props
        info["lines"].append(
            {"pre": pre, "base": base, "reading": reading, "suf": suf}
        )
        c.collapseToEnd()
    return info


def _build(desktop, writing, vert_align, align_name, out):
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    text = doc.Text
    if writing == "vertical":
        _vertical(doc)

    c = text.createTextCursor()
    title = (
        "Line spacing spike — %s — Text-to-text=%s — fixed %.0fpt — body %.0fpt"
        % (writing, align_name, FIXED_LINE_PT, BODY_PT)
    )
    text.insertString(c, title, True)
    _style_run(c, 9.0)

    # Marker lines for PDF measurement (unique glyphs)
    plain_lines = [
        "あいうえお一",
        "かきくけこ二",
        "さしすせそ三",
        "たちつてと四",
    ]
    ruby_lines = [
        ("", "漢字", "かんじ", "一"),
        ("", "日本", "にほん", "二"),
        ("", "文字", "もじ", "三"),
        ("", "試験", "しけん", "四"),
    ]

    c = _append(text)
    text.insertString(c, "=== PLAIN (no ruby) ===", True)
    _style_run(c, 9.0)
    plain = _insert_plain_block(text, vert_align, plain_lines)

    c = _append(text)
    text.insertString(c, "=== RUBY (group on each line) ===", True)
    _style_run(c, 9.0)
    ruby = _insert_ruby_block(text, vert_align, ruby_lines)

    # Mixed: plain / ruby / plain / ruby alternating
    c = _append(text)
    text.insertString(c, "=== MIXED alternate ===", True)
    _style_run(c, 9.0)
    mixed_plain = _insert_plain_block(text, vert_align, ["あい混合一", "うえ混合三"])
    # insert ruby between by separate calls already sequential

    tag = "%s_%s" % (writing, align_name.lower())
    path = os.path.join(out, "linespace_%s.odt" % tag)
    _save(doc, path)
    try:
        doc.close(True)
    except Exception:
        pass
    return {
        "tag": tag,
        "writing": writing,
        "ParaVertAlignment": vert_align,
        "align_name": align_name,
        "fixed_line_pt": FIXED_LINE_PT,
        "body_pt": BODY_PT,
        "odt": path,
        "plain": plain,
        "ruby": ruby,
    }


def run_ruby_line_spacing_spike(*_args):
    out = _outdir()
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Measure whether ruby expands fixed ParaLineSpacing; "
            "compare ParaVertAlignment BASELINE vs AUTOMATIC vs CENTER "
            "(Paragraph dialog Text-to-text)."
        ),
        "artifact_dir": out,
        "uno_map": {
            "Text-to-text Base line": "ParaVertAlignment = ParagraphVertAlign.BASELINE (1)",
            "Text-to-text Automatic": "ParaVertAlignment = AUTOMATIC (0)",
            "Text-to-text Center": "ParaVertAlignment = CENTER (3)",
            "Fixed line spacing": "ParaLineSpacing Mode=FIXED Height=twips",
        },
        "documents": [],
    }
    try:
        desktop = _desktop()
        for writing in ("horizontal", "vertical"):
            for va, name in (
                (_VA_BASELINE, "BASELINE"),
                (_VA_AUTOMATIC, "AUTOMATIC"),
                (_VA_CENTER, "CENTER"),
            ):
                report["documents"].append(
                    _build(desktop, writing, va, name, out)
                )
        report["ok"] = True
    except Exception as exc:
        report["ok"] = False
        report["error"] = str(exc)
        report["traceback"] = traceback.format_exc()

    with open(os.path.join(out, "line_spacing_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    return None
