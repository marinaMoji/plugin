# -*- coding: utf-8 -*-
"""
Reproduce warichū breakage from setting RubyText="" on combine apply.

A) Bare CharCombineIsOn (correct marinaMoji 0.3.20+)
B) CharCombineIsOn after RubyText="" (0.3.18–0.3.19 regression)
C) Warichū first, then ruby on a *separate* adjacent base (user sequence)
D) Group ruby INDENT_BLOCK vs mono CENTER

Entry: run_warichu_ruby_interaction_spike()
"""

from __future__ import annotations

import json
import os
import traceback
import zipfile
from datetime import datetime, timezone

import uno


def _artifact_dir():
    preferred = os.path.join(
        os.path.expanduser("~"),
        "Code",
        "marinaMoji",
        "plugin",
        "libreoffice",
        "spikes",
        "ruby",
        "artifacts",
        "warichu_interaction",
    )
    os.makedirs(preferred, exist_ok=True)
    return preferred


def _desktop():
    try:
        return XSCRIPTCONTEXT.getDesktop()  # noqa: F821
    except NameError:
        ctx = uno.getComponentContext()
        return ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx
        )


def _set(obj, name, value):
    try:
        obj.setPropertyValue(name, value)
        return True
    except Exception:
        return False


def _get(obj, name, default=None):
    try:
        return obj.getPropertyValue(name)
    except Exception:
        return default


def _ja():
    from com.sun.star.lang import Locale

    loc = Locale()
    loc.Language = "ja"
    loc.Country = "JP"
    return loc


def _pb():
    from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK

    return PARAGRAPH_BREAK


def _style(c, font="Hiragino Mincho ProN", size=14.0):
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
    url = uno.systemPathToFileUrl(os.path.abspath(path))
    doc.storeAsURL(url, (PropertyValue(Name="FilterName", Value="writer8"),))


def _set_vertical(doc):
    from com.sun.star.text.WritingMode2 import RL_TB

    page = doc.StyleFamilies.getByName("PageStyles").getByName("Standard")
    return _set(page, "WritingMode", RL_TB)


def _odf_flags(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("content.xml").decode("utf-8", errors="replace")
    return {
        "text_combine_lines": xml.count('text-combine="lines"'),
        "empty_ruby_text": xml.count("<text:ruby-text/>") + xml.count("<text:ruby-text></text:ruby-text>"),
        "has_ruby_text_hon": "ほん" in xml,
        "has_note": "割り注は、良いです。" in xml or "字割り注" in xml,
    }


def run_warichu_ruby_interaction_spike(*_args):
    out = _artifact_dir()
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Warichū first / empty RubyText regression; mono vs group adjust",
        "cases": [],
    }
    desktop = _desktop()
    try:
        for writing, tag in (("horizontal", "h"), ("vertical", "v")):
            doc = desktop.loadComponentFromURL(
                "private:factory/swriter", "_blank", 0, ()
            )
            text = doc.Text
            if writing == "vertical":
                _set_vertical(doc)

            c = text.createTextCursor()
            text.insertString(
                c,
                "Warichū×ruby interaction — %s — do not clear RubyText on combine"
                % writing,
                True,
            )
            _style(c, size=10.0)

            # A) correct warichū
            c = _append(text)
            text.insertString(c, "A) bare combine (0.3.20+)", True)
            _style(c, size=10.0)
            c = _append(text)
            text.insertString(c, "本文", True)
            _style(c)
            c.collapseToEnd()
            text.insertString(c, "割り注は、良いです。", True)
            _style(c)
            ok_a = _set(c, "CharCombineIsOn", True)
            props_a = {
                "id": "A_bare_%s" % tag,
                "CharCombineIsOn": _get(c, "CharCombineIsOn"),
                "RubyText": _get(c, "RubyText"),
                "set_ok": ok_a,
            }
            c.collapseToEnd()
            text.insertString(c, "国際", True)
            _style(c)
            report["cases"].append(props_a)

            # B) regression: clear RubyText then combine
            c = _append(text)
            text.insertString(c, "B) RubyText=\"\" then combine (REGRESSION)", True)
            _style(c, size=10.0)
            c = _append(text)
            text.insertString(c, "本文", True)
            _style(c)
            c.collapseToEnd()
            text.insertString(c, "割り注は、良いです。", True)
            _style(c)
            _set(c, "RubyText", "")
            ok_b = _set(c, "CharCombineIsOn", True)
            props_b = {
                "id": "B_clear_ruby_%s" % tag,
                "CharCombineIsOn": _get(c, "CharCombineIsOn"),
                "RubyText": _get(c, "RubyText"),
                "set_ok": ok_b,
            }
            c.collapseToEnd()
            text.insertString(c, "国際", True)
            _style(c)
            report["cases"].append(props_b)

            # C) user sequence: warichū first on note, then ruby on separate 文
            c = _append(text)
            text.insertString(
                c, "C) warichū first on 字割り注, then ruby ほん on 文", True
            )
            _style(c, size=10.0)
            c = _append(text)
            text.insertString(c, "文", True)
            _style(c)
            base_cur = text.createTextCursorByRange(c)
            c.collapseToEnd()
            text.insertString(c, "字割り注", True)
            _style(c)
            ok_w = _set(c, "CharCombineIsOn", True)
            # now ruby on 文 only (CENTER for mono)
            _set(base_cur, "CharCombineIsOn", False)
            _set(base_cur, "RubyText", "ほん")
            _set(base_cur, "RubyAdjust", 1)  # CENTER
            _set(base_cur, "RubyPosition", 0)
            _set(base_cur, "RubyAdjust", 1)
            report["cases"].append(
                {
                    "id": "C_user_seq_%s" % tag,
                    "warichu_CharCombineIsOn": _get(c, "CharCombineIsOn"),
                    "warichu_set_ok": ok_w,
                    "ruby_text": _get(base_cur, "RubyText"),
                    "ruby_adjust": _get(base_cur, "RubyAdjust"),
                    "base": base_cur.getString(),
                    "note": c.getString(),
                }
            )

            # D) group 本文/もと INDENT_BLOCK
            c = _append(text)
            text.insertString(c, "D) group 本文/もと INDENT_BLOCK", True)
            _style(c, size=10.0)
            c = _append(text)
            text.insertString(c, "本文", True)
            _style(c)
            _set(c, "RubyText", "もと")
            _set(c, "RubyAdjust", 4)
            _set(c, "RubyPosition", 0)
            report["cases"].append(
                {
                    "id": "D_group_%s" % tag,
                    "RubyAdjust": _get(c, "RubyAdjust"),
                    "RubyText": _get(c, "RubyText"),
                }
            )

            path = os.path.join(out, "warichu_ruby_interaction_%s.odt" % tag)
            _save(doc, path)
            report["cases"].append({"id": "odf_%s" % tag, "path": path, **_odf_flags(path)})
            try:
                doc.close(True)
            except Exception:
                pass

        report["ok"] = True
    except Exception as exc:
        report["ok"] = False
        report["error"] = str(exc)
        report["traceback"] = traceback.format_exc()

    with open(
        os.path.join(out, "warichu_ruby_interaction_report.json"),
        "w",
        encoding="utf-8",
    ) as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    # LO macros must not return a Python dict (UNO cannot convert it).
    return None
