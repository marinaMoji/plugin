# -*- coding: utf-8 -*-
"""
Reproduce vertical adjacent ruby + warichū (user screenshot case).

Sequence matching the report:
  Insert 文字割り注
  Ruby モン on 文 (mono CENTER)
  Warichū on 割り注 only (bare CharCombineIsOn)
  Controls: warichū-only, ruby-only, horizontal vs vertical

Entry returns None (UNO-safe).
"""

from __future__ import annotations

import json
import os
import traceback
import zipfile
from datetime import datetime, timezone

import uno


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
        "adjacent_ruby_warichu",
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


def _style(c, size=18.0, font="Hiragino Mincho ProN"):
    _set(c, "CharLocaleAsian", _ja())
    _set(c, "CharFontNameAsian", font)
    _set(c, "CharFontName", font)
    _set(c, "CharHeightAsian", size)
    _set(c, "CharHeight", size)


def _append(text):
    c = text.createTextCursor()
    c.gotoEnd(False)
    if (text.getString() or "").strip():
        text.insertControlCharacter(c, _pb(), False)
        c.gotoEnd(False)
    return c


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


def _odf_snip(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("content.xml").decode("utf-8", errors="replace")
    import re

    paras = []
    for m in re.finditer(r"<text:p[^>]*>.*?</text:p>", xml):
        s = m.group(0)
        if any(k in s for k in ("文字", "割り", "モン", "本文")):
            paras.append(re.sub(r"\s+", " ", s)[:500])
    return {
        "combine_lines": xml.count('text-combine="lines"'),
        "empty_ruby": xml.count("<text:ruby-text/>")
        + xml.count("<text:ruby-text></text:ruby-text>"),
        "ruby_mon": "モン" in xml,
        "paras": paras[:12],
    }


def _insert_screenshot_case(text, label):
    """文字 + ruby on 文 + warichū on 割り注. Returns prop snapshot."""
    c = _append(text)
    text.insertString(c, label, True)
    _style(c, 10.0)
    c = _append(text)

    # Full string first (no sticky inheritance from prior ruby apply)
    text.insertString(c, "文字割り注", True)
    _style(c, 18.0)
    # Select 文 (first char)
    c.collapseToStart()
    # After insertString with True, cursor covers whole string — go to start
    # Recreate: find start of this paragraph run
    # Safer: insert piece by piece
    return None  # replaced below


def _build_case_piecemeal(text, label, *, apply_ruby=True, apply_warichu=True):
    c = _append(text)
    text.insertString(c, label, True)
    _style(c, 10.0)

    c = _append(text)
    # 文
    text.insertString(c, "文", True)
    _style(c, 18.0)
    info = {"label": label, "base_文": c.getString()}
    if apply_ruby:
        _set(c, "RubyText", "モン")
        _set(c, "RubyAdjust", 1)  # CENTER mono
        _set(c, "RubyPosition", 0)
        _set(c, "RubyAdjust", 1)
        info["ruby"] = {
            "RubyText": _get(c, "RubyText"),
            "RubyAdjust": _get(c, "RubyAdjust"),
        }
    c.collapseToEnd()

    # 字 (body, no ruby, no combine)
    text.insertString(c, "字", True)
    _style(c, 18.0)
    # Ensure no combine/ruby sticky on this char — do not set RubyText=""
    _set(c, "CharCombineIsOn", False)
    info["字_combine"] = _get(c, "CharCombineIsOn")
    info["字_ruby"] = _get(c, "RubyText")
    c.collapseToEnd()

    # 割り注 as warichū
    text.insertString(c, "割り注", True)
    _style(c, 18.0)
    if apply_warichu:
        ok = _set(c, "CharCombineIsOn", True)
        info["warichu"] = {
            "set_ok": ok,
            "CharCombineIsOn": _get(c, "CharCombineIsOn"),
            "RubyText": _get(c, "RubyText"),
            "text": c.getString(),
        }
    else:
        info["warichu"] = {"applied": False, "text": c.getString()}
    c.collapseToEnd()
    return info


def _build_warichu_only(text, label):
    c = _append(text)
    text.insertString(c, label, True)
    _style(c, 10.0)
    c = _append(text)
    text.insertString(c, "文字", True)
    _style(c, 18.0)
    c.collapseToEnd()
    text.insertString(c, "割り注", True)
    _style(c, 18.0)
    ok = _set(c, "CharCombineIsOn", True)
    return {
        "label": label,
        "set_ok": ok,
        "CharCombineIsOn": _get(c, "CharCombineIsOn"),
        "text": c.getString(),
    }


def _build_doc(desktop, writing, out):
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    text = doc.Text
    vert = None
    if writing == "vertical":
        vert = _vertical(doc)

    c = text.createTextCursor()
    text.insertString(
        c,
        "Adjacent ruby+warichū — %s — 文/モン + 字 + warichū(割り注)" % writing,
        True,
    )
    _style(c, 10.0)

    cases = []
    cases.append(
        _build_case_piecemeal(
            text,
            "[screenshot] ruby then warichū adjacent",
            apply_ruby=True,
            apply_warichu=True,
        )
    )
    cases.append(
        _build_warichu_only(text, "[control] warichū only (文字 + 割り注)")
    )
    cases.append(
        _build_case_piecemeal(
            text,
            "[control] ruby only",
            apply_ruby=True,
            apply_warichu=False,
        )
    )

    # Sticky-risk sequence: apply ruby, THEN type following chars (inheritance)
    c = _append(text)
    text.insertString(c, "[sticky] ruby on 文, then type 字割り注, then combine note", True)
    _style(c, 10.0)
    c = _append(text)
    text.insertString(c, "文", True)
    _style(c, 18.0)
    _set(c, "RubyText", "モン")
    _set(c, "RubyAdjust", 1)
    _set(c, "RubyPosition", 0)
    c.collapseToEnd()
    # typing while sticky ruby may decorate following chars
    text.insertString(c, "字割り注", True)
    _style(c, 18.0)
    sticky_ruby = _get(c, "RubyText")
    sticky_combine_before = _get(c, "CharCombineIsOn")
    # try combine on whole typed tail
    ok = _set(c, "CharCombineIsOn", True)
    cases.append(
        {
            "label": "[sticky] after ruby type+combine",
            "sticky_RubyText_on_tail": sticky_ruby,
            "combine_before": sticky_combine_before,
            "combine_set_ok": ok,
            "combine_after": _get(c, "CharCombineIsOn"),
            "tail": c.getString(),
        }
    )

    path = os.path.join(out, "adjacent_%s.odt" % writing)
    _save(doc, path)
    try:
        doc.close(True)
    except Exception:
        pass
    return {
        "writing": writing,
        "vertical_ok": vert,
        "odt": path,
        "cases": cases,
        "odf": _odf_snip(path),
    }


def run_adjacent_ruby_warichu_spike(*_args):
    out = _outdir()
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Vertical adjacent 文/モン + warichū 割り注 corruption",
        "artifact_dir": out,
    }
    try:
        desktop = _desktop()
        report["horizontal"] = _build_doc(desktop, "horizontal", out)
        report["vertical"] = _build_doc(desktop, "vertical", out)
        report["ok"] = True
    except Exception as exc:
        report["ok"] = False
        report["error"] = str(exc)
        report["traceback"] = traceback.format_exc()
    with open(
        os.path.join(out, "adjacent_report.json"), "w", encoding="utf-8"
    ) as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    return None
