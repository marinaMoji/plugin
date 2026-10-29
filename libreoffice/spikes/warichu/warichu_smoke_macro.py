# -*- coding: utf-8 -*-
"""
In-Writer smoke for marinaMoji warichū apply/remove (caret-aware).

Install beside other spikes; run: run_warichu_smoke()
Does not modify LibreOffice core.
"""

from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, timezone

import uno

# Import extension helpers if available on path; else duplicate minimal checks.
try:
    import warichu as warichu_mod
except ImportError:
    warichu_mod = None


def _artifact_dir():
    preferred = os.path.join(
        os.path.expanduser("~"),
        "Code",
        "marinaMoji",
        "plugin",
        "libreoffice",
        "spikes",
        "warichu",
        "artifacts",
        "smoke",
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


def run_warichu_smoke(*_args):
    out = {"started_at": datetime.now(timezone.utc).isoformat(), "steps": [], "ok": False}
    desk = _desktop()
    doc = desk.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    text = doc.Text
    try:
        cursor = text.createTextCursor()
        text.insertString(cursor, "本文割り注は、良いです。続き", False)
        # Select note only: characters after 本文 (2) length 10
        cursor.gotoStart(False)
        cursor.goRight(2, False)
        cursor.goRight(10, True)
        note_before = cursor.getString()
        out["steps"].append({"select_note": note_before})

        _set(cursor, "CharCombineIsOn", True)
        out["steps"].append(
            {
                "apply": True,
                "CharCombineIsOn": _get(cursor, "CharCombineIsOn"),
                "text": cursor.getString(),
                "preserved": cursor.getString() == note_before,
            }
        )

        # Collapse caret into middle of note
        cursor.collapseToStart()
        cursor.goRight(3, False)
        out["steps"].append({"caret_collapsed": cursor.isCollapsed()})

        if warichu_mod is not None:
            span = warichu_mod.expand_to_warichu_span(text, cursor)
            if span is None:
                out["steps"].append({"expand": None, "error": "no span"})
            else:
                before = span.getString()
                warichu_mod._clear_combine(span)
                after = span.getString()
                out["steps"].append(
                    {
                        "caret_remove": True,
                        "before": before,
                        "after": after,
                        "preserved": before == after,
                        "combine_after": _get(span, "CharCombineIsOn"),
                    }
                )
        else:
            # Fallback without module: clear current char only (document limitation)
            out["steps"].append({"warichu_module": "missing — caret expand skipped"})

        path = os.path.join(_artifact_dir(), "warichu_smoke.odt")
        if os.path.exists(path):
            os.remove(path)
        from com.sun.star.beans import PropertyValue

        props = []
        for n, v in (("FilterName", "writer8"), ("Overwrite", True)):
            p = PropertyValue()
            p.Name = n
            p.Value = v
            props.append(p)
        doc.storeAsURL(uno.systemPathToFileUrl(path), tuple(props))
        out["odt"] = path
        out["ok"] = True
    except Exception:
        out["error"] = traceback.format_exc()
    out["finished_at"] = datetime.now(timezone.utc).isoformat()
    report = os.path.join(_artifact_dir(), "smoke_report.json")
    with open(report, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return None


g_exportedScripts = (run_warichu_smoke,)
