# -*- coding: utf-8 -*-
"""
Controlled warichū re-test: Japanese font + ja-JP Asian locale + roomy line spacing.

Compares:
  A) plain text (control)
  B) CharCombine with JP settings (UNO, character cursor)
  C) same as B but with 200% line spacing
  D) short even / odd / unequal samples under C

Entry point: run_retest_jp()
"""

from __future__ import annotations

import json
import os
import traceback
import zipfile
import re
from datetime import datetime, timezone

import uno


JP_FONT_CANDIDATES = (
    "Hiragino Mincho ProN",
    "ヒラギノ明朝 ProN",
    "Hiragino Mincho Pro",
    "ヒラギノ明朝 Pro",
    "Hiragino Sans",
    "ヒラギノ角ゴシック",
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
        "retest_jp",
    )
    desktop = os.path.join(
        os.path.expanduser("~"), "Desktop", "warichu_retest_jp_artifacts"
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
        # XMessageBoxFactory
        peer = None
        try:
            frame = XSCRIPTCONTEXT.getDesktop().getCurrentFrame()  # noqa: F821
            win = frame.getContainerWindow() if frame else None
            if win is not None and hasattr(tk, "createMessageBox"):
                from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
                from com.sun.star.awt.MessageBoxType import INFOBOX

                peer = tk.createMessageBox(win, INFOBOX, BUTTONS_OK, title, text[:1800])
        except Exception:
            peer = None
        if peer is not None and hasattr(peer, "execute"):
            peer.execute()
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


def _pick_font(cursor):
    """Try candidate Asian fonts; return the one that sticks."""
    for name in JP_FONT_CANDIDATES:
        _set(cursor, "CharFontNameAsian", name)
        _set(cursor, "CharFontName", name)
        got = _get(cursor, "CharFontNameAsian")
        if got == name or (isinstance(got, str) and name in got):
            return name, got
    return JP_FONT_CANDIDATES[0], _get(cursor, "CharFontNameAsian")


def _line_spacing_200(cursor):
    """Paragraph line spacing 200% so two half-lines have vertical room."""
    try:
        from com.sun.star.style.LineSpacing import LineSpacing
        from com.sun.star.style.LineSpacingMode import PROP

        ls = LineSpacing()
        ls.Mode = PROP
        ls.Height = 200  # percent of single spacing
        return _set(cursor, "ParaLineSpacing", ls)
    except Exception:
        # Older / alternate: Height as short percent via struct created by uno
        try:
            ls = uno.createUnoStruct("com.sun.star.style.LineSpacing")
            ls.Mode = 0  # PROP
            ls.Height = 200
            return _set(cursor, "ParaLineSpacing", ls)
        except Exception as exc:
            return {"ok": False, "error": type(exc).__name__, "message": str(exc)}


def _append_heading(text, label):
    try:
        from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
    except ImportError:
        PARAGRAPH_BREAK = 0
    cursor = text.createTextCursor()
    cursor.gotoEnd(False)
    if (text.getString() or "").strip():
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        cursor.gotoEnd(False)
    text.insertString(cursor, label, True)
    _set(cursor, "CharWeight", 150.0)  # bold-ish
    _set(cursor, "CharCombineIsOn", False)
    cursor.gotoEnd(False)
    cursor.collapseToEnd()
    return cursor


def _append_sample(text, content, *, combine, brackets, roomy_lines, font_name):
    try:
        from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
    except ImportError:
        PARAGRAPH_BREAK = 0

    cursor = text.createTextCursor()
    cursor.gotoEnd(False)
    text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    cursor.gotoEnd(False)

    # Insert as selected run
    text.insertString(cursor, content, True)

    # Always set JP locale + font on the run first
    locale_result = _set(cursor, "CharLocaleAsian", _ja_locale())
    _set(cursor, "CharLocale", _ja_locale())
    font_req, font_got = font_name, None
    _set(cursor, "CharFontNameAsian", font_name)
    _set(cursor, "CharFontName", font_name)
    font_got = _get(cursor, "CharFontNameAsian")
    height = _set(cursor, "CharHeightAsian", 14.0)
    _set(cursor, "CharHeight", 14.0)

    spacing = None
    if roomy_lines:
        # Line spacing is a paragraph property — apply on paragraph cursor
        para = cursor.getText().createTextCursorByRange(cursor)
        para.gotoStartOfParagraph(False)
        para.gotoEndOfParagraph(True)
        spacing = _line_spacing_200(para)

    combine_result = None
    if combine:
        prefix, suffix = brackets
        combine_result = {
            "CharCombineIsOn": _set(cursor, "CharCombineIsOn", True),
            "CharCombinePrefix": _set(cursor, "CharCombinePrefix", prefix),
            "CharCombineSuffix": _set(cursor, "CharCombineSuffix", suffix),
            "after": {
                "CharCombineIsOn": _get(cursor, "CharCombineIsOn"),
                "CharCombinePrefix": _get(cursor, "CharCombinePrefix"),
                "CharCombineSuffix": _get(cursor, "CharCombineSuffix"),
                "CharFontNameAsian": _get(cursor, "CharFontNameAsian"),
                "CharLocaleAsian": str(_get(cursor, "CharLocaleAsian")),
            },
        }
    else:
        _set(cursor, "CharCombineIsOn", False)

    return {
        "text": content,
        "combine": combine,
        "roomy_lines": roomy_lines,
        "locale": locale_result,
        "font_requested": font_req,
        "font_got": font_got,
        "height": height,
        "spacing": spacing,
        "combine_result": combine_result,
        "source_preserved": cursor.getString() == content,
    }


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


def _extract_combine(odt_path, out_path):
    hits = []
    try:
        with zipfile.ZipFile(odt_path) as zf:
            data = zf.read("content.xml").decode("utf-8")
            for match in re.finditer(r".{0,120}text-combine.{0,160}", data):
                hits.append(match.group(0))
            # character styles?
            for match in re.finditer(
                r'style:family="text"[^>]*>.*?text-combine.*?</style:style>', data
            ):
                hits.append("CHARSTYLE: " + match.group(0)[:300])
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(hits, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        return {"ok": True, "hit_count": len(hits)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def run_retest_jp(*_args):
    out_dir = _artifact_dir()
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "lo_version": _lo_version(),
        "artifact_dir": out_dir,
        "purpose": (
            "Controlled re-test: Hiragino/JP locale + optional 200% line spacing. "
            "Please screenshot each labeled block."
        ),
        "sections": [],
        "errors": [],
    }

    desktop = _desktop()
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    text = doc.Text

    # Probe font on an empty cursor at start
    probe = text.createTextCursor()
    font_name, font_probe = _pick_font(probe)
    report["font_selected"] = font_name
    report["font_probe"] = font_probe

    samples = [
        ("even_short", "割注試験", "（", "）"),
        ("odd_short", "割注の試験", "（", "）"),
        ("unequal", "これは非常に長い割注の本文である", "（", "）"),
        ("mixed", "AB漢字12かな", "(", ")"),
        ("no_brackets", "括弧なし", "", ""),
    ]

    try:
        _append_heading(
            text,
            "RETEST JP — font=%s · CharLocaleAsian=ja-JP · compare A/B/C"
            % font_name,
        )

        _append_heading(text, "A) Control — plain text, no combine, default spacing")
        for sid, body, _p, _s in samples[:3]:
            report["sections"].append(
                {
                    "id": "A_%s" % sid,
                    **_append_sample(
                        text,
                        body,
                        combine=False,
                        brackets=("", ""),
                        roomy_lines=False,
                        font_name=font_name,
                    ),
                }
            )

        _append_heading(
            text, "B) Combine ON — JP font/locale — default (single) line spacing"
        )
        for sid, body, prefix, suffix in samples:
            report["sections"].append(
                {
                    "id": "B_%s" % sid,
                    **_append_sample(
                        text,
                        body,
                        combine=True,
                        brackets=(prefix, suffix),
                        roomy_lines=False,
                        font_name=font_name,
                    ),
                }
            )

        _append_heading(
            text, "C) Combine ON — JP font/locale — 200% paragraph line spacing"
        )
        for sid, body, prefix, suffix in samples:
            report["sections"].append(
                {
                    "id": "C_%s" % sid,
                    **_append_sample(
                        text,
                        body,
                        combine=True,
                        brackets=(prefix, suffix),
                        roomy_lines=True,
                        font_name=font_name,
                    ),
                }
            )

        _append_heading(
            text,
            "Manual check: select a B/C line → Format → Character → Position. "
            "Confirm 'Combine characters' is checked. Try Hiragino if font differs.",
        )
    except Exception as exc:
        report["errors"].append(traceback.format_exc())
        _msg("warichū retest JP", "Failed while building doc:\n%s" % exc)
        return

    odt = os.path.join(out_dir, "warichu_retest_jp.odt")
    report["save_odt"] = _save(doc, odt, "writer8")
    if report["save_odt"].get("ok"):
        report["odf"] = _extract_combine(
            odt, os.path.join(out_dir, "odf_combine_snippets.json")
        )

    # Leave document open for screenshots; also store JSON
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report_path = os.path.join(out_dir, "retest_jp_report.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    notes = os.path.join(out_dir, "WHAT_TO_LOOK_FOR.md")
    with open(notes, "w", encoding="utf-8") as fh:
        fh.write(
            "\n".join(
                [
                    "# What to look for (JP retest)",
                    "",
                    "Document: `warichu_retest_jp.odt` (left open).",
                    "Font requested: **%s**" % font_name,
                    "",
                    "## Sections",
                    "- **A** — plain Japanese text (sanity: must look normal).",
                    "- **B** — combine on, default line spacing (same as first spike conditions, but JP font/locale).",
                    "- **C** — combine on, **200%% line spacing** (tests “overlap because the line box is too short”).",
                    "",
                    "## Pass / fail",
                    "- **Pass:** each combined run shows two readable mini-rows inside one line, with brackets if requested.",
                    "- **Fail:** glyphs still stacked on top of each other / double-printed (as in first spike).",
                    "- Note whether **C** is better than **B**.",
                    "",
                    "Optional: Format → Character → Position on one combined word; screenshot that dialog too.",
                    "",
                ]
            )
        )

    _msg(
        "warichū retest JP",
        "Open doc left for screenshots.\nFont: %s\nArtifacts: %s\nCompare sections A / B / C."
        % (font_name, out_dir),
    )
    return None


g_exportedScripts = (run_retest_jp,)
