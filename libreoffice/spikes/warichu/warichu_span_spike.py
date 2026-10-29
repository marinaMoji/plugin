# -*- coding: utf-8 -*-
"""
Warichū spike v4: character-span combine.

Finding: bare CharCombineIsOn (ODF text-combine=lines only) can work
(e.g. 本文+括弧なし). Setting CharCombinePrefix/Suffix often collapses glyphs.

Entry: run_span_spike()
"""

from __future__ import annotations

import json
import os
import re
import traceback
import zipfile
from datetime import datetime, timezone

import uno

JP_FONTS = (
    "Hiragino Mincho ProN",
    "ヒラギノ明朝 ProN",
    "Hiragino Mincho Pro",
    "BIZ UDMincho",
)


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
        "span_spike",
    )
    desktop = os.path.join(
        os.path.expanduser("~"), "Desktop", "warichu_span_spike_artifacts"
    )
    for path in (preferred, desktop):
        try:
            os.makedirs(path, exist_ok=True)
            probe = os.path.join(path, ".write_test")
            with open(probe, "w", encoding="utf-8") as fh:
                fh.write("ok")
            os.remove(probe)
            return path
        except Exception:
            continue
    return preferred


def _msg(title, text):
    try:
        ctx = uno.getComponentContext()
        tk = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.Toolkit", ctx
        )
        frame = XSCRIPTCONTEXT.getDesktop().getCurrentFrame()  # noqa: F821
        win = frame.getContainerWindow() if frame else None
        if win is not None and hasattr(tk, "createMessageBox"):
            from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
            from com.sun.star.awt.MessageBoxType import INFOBOX

            box = tk.createMessageBox(win, INFOBOX, BUTTONS_OK, title, text[:1800])
            box.execute()
            return
    except Exception:
        pass
    print("%s: %s" % (title, text))


def _desktop():
    try:
        return XSCRIPTCONTEXT.getDesktop()  # noqa: F821
    except NameError:
        ctx = uno.getComponentContext()
        return ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx
        )


def _lo_version():
    try:
        ctx = uno.getComponentContext()
        cfg_prov = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.configuration.ConfigurationProvider", ctx
        )
        from com.sun.star.beans import PropertyValue

        arg = PropertyValue()
        arg.Name = "nodepath"
        arg.Value = "/org.openoffice.Setup/Product"
        cfg = cfg_prov.createInstanceWithArguments(
            "com.sun.star.configuration.ConfigurationAccess", (arg,)
        )
        parts = []
        for key in ("ooName", "ooSetupVersionAboutBox", "ooSetupVersion"):
            try:
                parts.append(str(cfg.getByName(key)))
            except Exception:
                pass
        return " ".join(parts) or "Unknown"
    except Exception as exc:
        return "Unknown (%s)" % exc


def _set(obj, name, value):
    try:
        obj.setPropertyValue(name, value)
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)}


def _get(obj, name):
    try:
        return obj.getPropertyValue(name)
    except Exception as exc:
        return {"error": type(exc).__name__, "message": str(exc)}


def _ja_locale():
    from com.sun.star.lang import Locale

    loc = Locale()
    loc.Language = "ja"
    loc.Country = "JP"
    loc.Variant = ""
    return loc


def _para_break():
    try:
        from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK

        return PARAGRAPH_BREAK
    except ImportError:
        return 0


def _pick_font(cursor):
    for name in JP_FONTS:
        _set(cursor, "CharFontNameAsian", name)
        _set(cursor, "CharFontName", name)
        got = _get(cursor, "CharFontNameAsian")
        if got == name or (isinstance(got, str) and name.split()[0] in str(got)):
            return name
    return JP_FONTS[0]


def _store_url(path):
    return uno.systemPathToFileUrl(os.path.abspath(path))


def _save(doc, path, filter_name):
    from com.sun.star.beans import PropertyValue

    if os.path.exists(path):
        os.remove(path)
    props = []
    for name, value in (("FilterName", filter_name), ("Overwrite", True)):
        p = PropertyValue()
        p.Name = name
        p.Value = value
        props.append(p)
    try:
        doc.storeAsURL(_store_url(path), tuple(props))
        return {"ok": True, "path": path}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)}


def _append_paragraph(text):
    cursor = text.createTextCursor()
    cursor.gotoEnd(False)
    if (text.getString() or "").strip():
        text.insertControlCharacter(cursor, _para_break(), False)
        cursor.gotoEnd(False)
    return cursor


def _style_body_run(cursor, font_name, size_pt=14.0):
    """Normal body text — must clear sticky CharCombine* from prior note spans."""
    _set(cursor, "CharLocaleAsian", _ja_locale())
    _set(cursor, "CharFontNameAsian", font_name)
    _set(cursor, "CharFontName", font_name)
    _set(cursor, "CharHeightAsian", size_pt)
    _set(cursor, "CharHeight", size_pt)
    _set(cursor, "CharWeight", 100.0)  # NORMAL — headings may leave bold sticky
    _set(cursor, "CharCombineIsOn", False)
    _set(cursor, "CharCombinePrefix", "")
    _set(cursor, "CharCombineSuffix", "")
    _set(cursor, "CharStyleName", "")


def _insert_body_plus_note(text, body, note, font_name, *, with_brackets=False):
    """
    Insert [body][note span].
    with_brackets=False: set ONLY CharCombineIsOn (matches working 括弧なし / manual T1).
    with_brackets=True: also set Prefix/Suffix （ ） — suspected to break paint.
    """
    cursor = _append_paragraph(text)

    text.insertString(cursor, body, True)
    _style_body_run(cursor, font_name)
    # Do not touch CharCombine* on body
    cursor.collapseToEnd()

    text.insertString(cursor, note, True)
    # Base font/locale only — do not call _style_body_run (it clears combine).
    _set(cursor, "CharLocaleAsian", _ja_locale())
    _set(cursor, "CharFontNameAsian", font_name)
    _set(cursor, "CharFontName", font_name)
    _set(cursor, "CharHeightAsian", 14.0)
    _set(cursor, "CharHeight", 14.0)
    _set(cursor, "CharWeight", 100.0)
    _set(cursor, "CharStyleName", "")
    apply = {"CharCombineIsOn": _set(cursor, "CharCombineIsOn", True)}
    if with_brackets:
        apply["CharCombinePrefix"] = _set(cursor, "CharCombinePrefix", "（")
        apply["CharCombineSuffix"] = _set(cursor, "CharCombineSuffix", "）")
    # When not using brackets, leave Prefix/Suffix untouched after IsOn=True
    # (do not write "") so ODF matches manual T1: text-combine=lines only.

    after = {
        "string": cursor.getString(),
        "CharCombineIsOn": _get(cursor, "CharCombineIsOn"),
        "CharCombinePrefix": _get(cursor, "CharCombinePrefix"),
        "CharCombineSuffix": _get(cursor, "CharCombineSuffix"),
    }
    cursor.collapseToEnd()
    return {
        "body": body,
        "note": note,
        "with_brackets": with_brackets,
        "apply": apply,
        "after": after,
        "source_preserved": after["string"] == note,
        "note_len": len(note),
    }


def _extract_odf(odt_path, out_path):
    info = {
        "combine_text_styles": [],
        "paragraph_combine_lines": [],
        "sample_paras": [],
        "ok": False,
    }
    try:
        with zipfile.ZipFile(odt_path) as zf:
            data = zf.read("content.xml").decode("utf-8")
        for m in re.finditer(
            r'<style:style style:name="([^"]+)" style:family="text"[^>]*>.*?</style:style>',
            data,
        ):
            block = m.group(0)
            if 'text-combine="lines"' in block:
                info["combine_text_styles"].append(
                    {
                        "name": m.group(1),
                        "has_brackets": "text-combine-start-char" in block,
                        "xml": block,
                    }
                )
        for m in re.finditer(
            r'<style:style style:name="([^"]+)" style:family="paragraph"[^>]*>.*?</style:style>',
            data,
        ):
            block = m.group(0)
            if 'text-combine="lines"' in block:
                info["paragraph_combine_lines"].append(m.group(1))
        for m in re.finditer(r"<text:p[^>]*>.*?</text:p>", data):
            para = m.group(0)
            if "text:span" in para:
                info["sample_paras"].append(para[:400])
        info["ok"] = True
        info["bare_combine_styles"] = sum(
            1 for s in info["combine_text_styles"] if not s["has_brackets"]
        )
        info["bracket_combine_styles"] = sum(
            1 for s in info["combine_text_styles"] if s["has_brackets"]
        )
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(info, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    except Exception as exc:
        info["error"] = str(exc)
    return info


def run_span_spike(*_args):
    out_dir = _artifact_dir()
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "lo_version": _lo_version(),
        "artifact_dir": out_dir,
        "purpose": (
            "Span combine WITHOUT brackets (known-good) vs WITH brackets (suspect). "
            "User reported 本文括弧なし worked."
        ),
        "cases": [],
        "errors": [],
    }

    desktop = _desktop()
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    text = doc.Text
    font_name = _pick_font(text.createTextCursor())
    report["font"] = font_name

    # notes of various lengths; SwCombinedPortion docs say ≤6 chars for letter-grid,
    # but warichū "lines" may allow longer (manual UI did).
    notes_no_brackets = [
        ("known_good", "本文", "括弧なし"),  # user: worked
        ("even4", "本文", "割注試験"),
        ("odd5", "本文", "割注の試験"),
        ("classic", "割り注", "割り注は、良いです。"),  # manual UI structural OK
        ("long", "本文", "これは非常に長い割注の本文である"),
        ("mixed", "本文", "AB漢字12かな"),
        ("two", "本文", "割注"),
        ("six", "本文", "一二三四五六"),
    ]
    notes_with_brackets = [
        ("even4_br", "本文", "割注試験"),
        ("known_br", "本文", "括弧なし"),
        ("classic_br", "割り注", "割り注は、良いです。"),
    ]

    try:
        c = _append_paragraph(text)
        text.insertString(
            c,
            "SPAN v4 — bare combine (no brackets) vs combine+brackets",
            True,
        )
        _style_body_run(c, font_name, 12.0)
        _set(c, "CharWeight", 150.0)
        c.collapseToEnd()

        c = _append_paragraph(text)
        text.insertString(
            c,
            "A) CharCombineIsOn ONLY — expect these to match 本文括弧なし success",
            True,
        )
        _style_body_run(c, font_name, 12.0)
        c.collapseToEnd()

        for sid, body, note in notes_no_brackets:
            try:
                entry = _insert_body_plus_note(
                    text, body, note, font_name, with_brackets=False
                )
                entry["id"] = "A_%s" % sid
                report["cases"].append(entry)
            except Exception:
                report["errors"].append("A_%s\n%s" % (sid, traceback.format_exc()))

        c = _append_paragraph(text)
        text.insertString(
            c,
            "B) CharCombineIsOn + Prefix/Suffix （） — suspect collapse",
            True,
        )
        _style_body_run(c, font_name, 12.0)
        c.collapseToEnd()

        for sid, body, note in notes_with_brackets:
            try:
                entry = _insert_body_plus_note(
                    text, body, note, font_name, with_brackets=True
                )
                entry["id"] = "B_%s" % sid
                report["cases"].append(entry)
            except Exception:
                report["errors"].append("B_%s\n%s" % (sid, traceback.format_exc()))

        c = _append_paragraph(text)
        text.insertString(
            c,
            "Please confirm: A known_good (本文括弧なし) and other A lines look like "
            "two mini-rows; say whether B (with brackets) still collapses.",
            True,
        )
        _style_body_run(c, font_name, 11.0)
    except Exception:
        report["errors"].append(traceback.format_exc())

    odt = os.path.join(out_dir, "warichu_span_spike.odt")
    report["save_odt"] = _save(doc, odt, "writer8")
    if report["save_odt"].get("ok"):
        report["odf"] = _extract_odf(odt, os.path.join(out_dir, "odf_analysis.json"))

    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(out_dir, "span_spike_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    odf = report.get("odf") or {}
    matrix = "\n".join(
        [
            "# Span spike v4 — bare combine vs brackets",
            "",
            "Hypothesis: brackets (Prefix/Suffix) break paint; bare combine works.",
            "",
            "| Check | Value |",
            "|---|---|",
            "| Font | %s |" % font_name,
            "| Bare combine text styles | %s |" % odf.get("bare_combine_styles"),
            "| Bracketed combine text styles | %s |" % odf.get("bracket_combine_styles"),
            "| Paragraph-level combine=lines | %s |"
            % (odf.get("paragraph_combine_lines") or "none"),
            "| Errors | %s |" % (len(report["errors"])),
            "",
            "Visual: A lines should work; compare B.",
            "",
        ]
    )
    with open(os.path.join(out_dir, "capability_matrix.md"), "w", encoding="utf-8") as fh:
        fh.write(matrix)

    _msg(
        "warichū span v4",
        "Bare styles: %s · Bracket styles: %s\nArtifacts: %s\nCheck A 本文括弧なし first."
        % (odf.get("bare_combine_styles"), odf.get("bracket_combine_styles"), out_dir),
    )
    return None


g_exportedScripts = (run_span_spike,)
