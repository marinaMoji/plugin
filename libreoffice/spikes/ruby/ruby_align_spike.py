# -*- coding: utf-8 -*-
"""
Phase 3 ruby investigation: marinaMoji-style UNO apply vs alignment matrix.

Creates horizontal + vertical ODTs with:
  - Classic 本文 + もと under each RubyAdjust value
  - Control: same as marinaMoji default (CENTER + ABOVE)
  - Isolated ruby (no warichū) and combined with warichū

Entry: run_ruby_align_spike()
"""

from __future__ import annotations

import json
import os
import re
import traceback
import zipfile
from datetime import datetime, timezone

import uno

ADJUSTS = (
    ("LEFT", 0),
    ("CENTER", 1),
    ("RIGHT", 2),
    ("BLOCK", 3),
    ("INDENT_BLOCK", 4),
)

JP_FONTS = (
    "Hiragino Mincho ProN",
    "ヒラギノ明朝 ProN",
    "Noto Sans JP",
    "YuMincho",
)


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
        "align_spike",
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
        return True
    except Exception as exc:
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


def _para_break():
    from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK

    return PARAGRAPH_BREAK


def _pick_font(cursor):
    for name in JP_FONTS:
        _set(cursor, "CharFontNameAsian", name)
        _set(cursor, "CharFontName", name)
        got = _get(cursor, "CharFontNameAsian")
        if got == name or (isinstance(got, str) and name.split()[0] in str(got)):
            return name
    return JP_FONTS[0]


def _style_body(cursor, font, size=14.0):
    _set(cursor, "CharLocaleAsian", _ja())
    _set(cursor, "CharFontNameAsian", font)
    _set(cursor, "CharFontName", font)
    _set(cursor, "CharHeightAsian", size)
    _set(cursor, "CharHeight", size)
    _set(cursor, "CharWeight", 100.0)
    _set(cursor, "CharCombineIsOn", False)
    _set(cursor, "RubyText", "")


def _append(text):
    c = text.createTextCursor()
    c.gotoEnd(False)
    if (text.getString() or "").strip():
        text.insertControlCharacter(c, _para_break(), False)
        c.gotoEnd(False)
    return c


def _heading(text, font, title):
    c = _append(text)
    text.insertString(c, title, True)
    _style_body(c, font, 11.0)
    _set(c, "CharWeight", 150.0)
    c.collapseToEnd()


def _insert_ruby_example(text, font, label, base, reading, adjust, *, with_warichu=False):
    """Insert label para + body with ruby on base, optional warichū after."""
    c = _append(text)
    text.insertString(c, label, True)
    _style_body(c, font, 10.0)
    c.collapseToEnd()

    c = _append(text)
    # body prefix empty — start with base
    text.insertString(c, base, True)
    _style_body(c, font, 14.0)
    _set(c, "RubyText", reading)
    ok_adj = _set(c, "RubyAdjust", adjust)
    ok_pos = _set(c, "RubyPosition", 0)  # ABOVE / right in vertical
    props = {
        "RubyText": _get(c, "RubyText"),
        "RubyAdjust": _get(c, "RubyAdjust"),
        "RubyPosition": _get(c, "RubyPosition"),
        "set_adjust_ok": ok_adj,
        "set_position_ok": ok_pos,
        "base": base,
        "reading": reading,
        "base_preserved": _get(c, "getString") if False else c.getString() == base,
    }
    # getString on selection
    props["base_preserved"] = c.getString() == base
    c.collapseToEnd()

    if with_warichu:
        note = "割り注は、良いです。"
        text.insertString(c, note, True)
        _style_body(c, font, 14.0)
        _set(c, "RubyText", "")
        _set(c, "CharCombineIsOn", True)
        props["warichu"] = note
        props["warichu_preserved"] = c.getString() == note
        c.collapseToEnd()

    text.insertString(c, "国際", True)
    _style_body(c, font, 14.0)
    _set(c, "RubyText", "")
    _set(c, "CharCombineIsOn", False)
    c.collapseToEnd()
    return props


def _set_vertical(doc):
    try:
        from com.sun.star.text.WritingMode2 import RL_TB

        styles = doc.StyleFamilies.getByName("PageStyles")
        page = styles.getByName("Standard")
        _set(page, "WritingMode", RL_TB)
        return {"ok": True, "WritingMode": "RL_TB"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _save(doc, path, filter_name):
    from com.sun.star.beans import PropertyValue

    if os.path.exists(path):
        os.remove(path)
    props = []
    for n, v in (("FilterName", filter_name), ("Overwrite", True)):
        p = PropertyValue()
        p.Name = n
        p.Value = v
        props.append(p)
    try:
        doc.storeAsURL(uno.systemPathToFileUrl(os.path.abspath(path)), tuple(props))
        return {"ok": True, "path": path}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _extract_odf(odt_path, out_json):
    info = {"ruby_bits": [], "combine": 0, "ok": False}
    try:
        with zipfile.ZipFile(odt_path) as zf:
            data = zf.read("content.xml").decode("utf-8")
        info["has_text_ruby"] = "text:ruby" in data
        info["ruby_text_count"] = data.count("text:ruby-text")
        info["combine"] = data.count('text-combine="lines"')
        for m in re.finditer(r"<text:ruby[\s\S]*?</text:ruby>", data):
            info["ruby_bits"].append(m.group(0)[:500])
        # Also style-based ruby?
        for m in re.finditer(r'ruby[^"]{0,80}', data, re.I):
            if len(info["ruby_bits"]) < 20:
                info.setdefault("ruby_attr_snips", []).append(m.group(0)[:120])
        info["ok"] = True
        with open(out_json, "w", encoding="utf-8") as fh:
            json.dump(info, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    except Exception as exc:
        info["error"] = str(exc)
    return info


def _build(writing, out_dir, font):
    desk = _desktop()
    doc = desk.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    text = doc.Text
    section = {"writing": writing, "cases": [], "errors": []}
    if writing == "vertical":
        section["vertical"] = _set_vertical(doc)

    try:
        _heading(
            text,
            font,
            "Ruby align spike — %s — font=%s — LO native UNO (same as marinaMoji)"
            % (writing, font),
        )
        _heading(
            text,
            font,
            "Disable field shading for screenshots: View → Field Shadings. Click away.",
        )

        # Prior default (CENTER) kept for visual comparison with 0.3.17
        section["cases"].append(
            {
                "id": "legacy_CENTER",
                **_insert_ruby_example(
                    text,
                    font,
                    "[legacy 0.3.17] CENTER+ABOVE isolated",
                    "本文",
                    "もと",
                    1,
                    with_warichu=False,
                ),
            }
        )
        section["cases"].append(
            {
                "id": "legacy_CENTER_warichu",
                **_insert_ruby_example(
                    text,
                    font,
                    "[legacy 0.3.17] CENTER+ABOVE + warichū (screenshot case)",
                    "本文",
                    "もと",
                    1,
                    with_warichu=True,
                ),
            }
        )

        for name, adj in ADJUSTS:
            section["cases"].append(
                {
                    "id": "iso_%s" % name,
                    **_insert_ruby_example(
                        text,
                        font,
                        "[isolated] RubyAdjust=%s 本文/もと" % name,
                        "本文",
                        "もと",
                        adj,
                        with_warichu=False,
                    ),
                }
            )

        # Current marinaMoji default (INDENT_BLOCK / Fig.124) with warichū
        section["cases"].append(
            {
                "id": "mm_default_INDENT_BLOCK_warichu",
                **_insert_ruby_example(
                    text,
                    font,
                    "[marinaMoji default 0.3.19+] INDENT_BLOCK+ABOVE + warichū",
                    "本文",
                    "もと",
                    4,
                    with_warichu=True,
                ),
            }
        )
        section["cases"].append(
            {
                "id": "mm_default_INDENT_BLOCK",
                **_insert_ruby_example(
                    text,
                    font,
                    "[marinaMoji default 0.3.19+] INDENT_BLOCK+ABOVE isolated",
                    "本文",
                    "もと",
                    4,
                    with_warichu=False,
                ),
            }
        )
        # Fig.125 alternative retained for comparison (not the product default)
        section["cases"].append(
            {
                "id": "alt_BLOCK",
                **_insert_ruby_example(
                    text,
                    font,
                    "[alternative] BLOCK+ABOVE isolated (Fig.125)",
                    "本文",
                    "もと",
                    3,
                    with_warichu=False,
                ),
            }
        )

        # Extra cases
        for base, reading, tag in (
            ("本", "ほん", "mono"),
            ("日本", "にほん", "group"),
            ("国際", "こくさい", "long"),
            ("今日", "きょう", "jukugo_like"),
        ):
            section["cases"].append(
                {
                    "id": "extra_%s" % tag,
                    **_insert_ruby_example(
                        text,
                        font,
                        "[extra] %s base=%s reading=%s CENTER" % (tag, base, reading),
                        base,
                        reading,
                        1,
                        with_warichu=False,
                    ),
                }
            )
    except Exception:
        section["errors"].append(traceback.format_exc())

    odt = os.path.join(out_dir, "ruby_align_%s.odt" % writing)
    section["save_odt"] = _save(doc, odt, "writer8")
    if section["save_odt"].get("ok"):
        section["odf"] = _extract_odf(
            odt, os.path.join(out_dir, "odf_%s.json" % writing)
        )
    try:
        doc.close(True)
    except Exception:
        pass
    return section


def run_ruby_align_spike(*_args):
    out_dir = _artifact_dir()
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "lo_version": _lo_version(),
        "artifact_dir": out_dir,
        "purpose": "Compare RubyAdjust modes; marinaMoji default INDENT_BLOCK (Fig.124); warichū interaction",
    }
    desk = _desktop()
    probe = desk.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    font = _pick_font(probe.Text.createTextCursor())
    report["font"] = font
    try:
        probe.close(True)
    except Exception:
        pass

    report["horizontal"] = _build("horizontal", out_dir, font)
    report["vertical"] = _build("vertical", out_dir, font)
    report["finished_at"] = datetime.now(timezone.utc).isoformat()

    with open(os.path.join(out_dir, "ruby_align_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # Headless PDF hint file
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(
            "# Ruby align spike\n\n"
            "Open ODTs in Writer. Turn **off** View → Field Shadings.\n"
            "Compare CENTER vs BLOCK for 本文/もと in horizontal and vertical.\n"
            "Convert PDF:\n\n"
            "```bash\n"
            "soffice --headless --convert-to pdf --outdir artifacts/align_spike "
            "artifacts/align_spike/ruby_align_horizontal.odt\n"
            "```\n"
        )
    return None


g_exportedScripts = (run_ruby_align_spike,)
