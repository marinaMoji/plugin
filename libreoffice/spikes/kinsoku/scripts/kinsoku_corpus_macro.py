# -*- coding: utf-8 -*-
"""
Stage E1 kinsoku corpus generator — creates controlled ODTs for body kinsoku tests.

Run as a LibreOffice Python macro (APSO / user Scripts). Read-oriented after create;
writes only under spikes/kinsoku/artifacts/ (or Desktop fallback).

Does NOT change Tools → Options Asian Layout globally beyond what a new Writer
document already inherits. Paragraph Asian toggles are set per test paragraph.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import uno
from com.sun.star.beans import PropertyValue

JP_FONTS = (
    "Hiragino Mincho ProN",
    "ヒラギノ明朝 ProN",
    "YuMincho",
    "游明朝体",
    "Hiragino Sans",
    "ヒラギノ角ゴシック",
    "Noto Serif CJK JP",
    "Noto Sans CJK JP",
)

# Narrow measure: force wraps without manual breaks.
# Writer uses 1/100 mm units. 7000 = 70 mm page width.
PAGE = dict(Width=7000, Height=20000)
MARGINS = dict(LeftMargin=500, RightMargin=500, TopMargin=500, BottomMargin=500)

FILLER = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめも"


def _artifact_dir():
    preferred = os.path.join(
        os.path.expanduser("~"),
        "Code",
        "marinaMoji",
        "plugin",
        "libreoffice",
        "spikes",
        "kinsoku",
        "artifacts",
    )
    desktop = os.path.join(os.path.expanduser("~"), "Desktop", "kinsoku_e1_artifacts")
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


def _desktop():
    try:
        return XSCRIPTCONTEXT.getDesktop()  # noqa: F821
    except NameError:
        ctx = uno.getComponentContext()
        return ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx
        )


def _msg(title, text):
    print("%s: %s" % (title, text))


def _pick_font(doc):
    # Best-effort: set Asian font on paragraph; Writer substitutes if missing.
    for name in JP_FONTS:
        return name
    return "Hiragino Mincho ProN"


def _set_page(doc):
    style = doc.StyleFamilies.getByName("PageStyles").getByName("Standard")
    style.setPropertyValue("Width", PAGE["Width"])
    style.setPropertyValue("Height", PAGE["Height"])
    for k, v in MARGINS.items():
        style.setPropertyValue(k, v)


def _append_para(text, cursor, body, *, forbidden=True, hanging=True, distance=True, font=None):
    cursor.gotoEnd(False)
    text.insertString(cursor, body + "\n", False)
    cursor.gotoEnd(False)
    # Select just-inserted paragraph roughly: go left over body
    cursor.goLeft(len(body) + 1, True)
    cursor.setPropertyValue("ParaIsForbiddenRules", forbidden)
    cursor.setPropertyValue("ParaIsHangingPunctuation", hanging)
    cursor.setPropertyValue("ParaIsCharacterDistance", distance)
    if font:
        cursor.setPropertyValue("CharFontNameAsian", font)
        cursor.setPropertyValue("CharHeightAsian", 14.0)
    cursor.collapseToEnd()


def _cases():
    # One phenomenon per paragraph; filler forces wrap on narrow page.
    f = FILLER * 3
    return [
        ("K01", "line-start 。", f + "です。" + f, True, True),
        ("K01b", "line-start 。 forbidden OFF", f + "です。" + f, False, True),
        ("K02", "line-start 、", f + "こと、" + f, True, True),
        ("K03", "line-start ）", f + "（注）" + f, True, True),
        ("K03b", "line-start 」", f + "「話」" + f, True, True),
        ("K04", "line-start small kana ゃ", f + "きゃ" + f, True, True),
        ("K05", "line-end 「", f + "「" + f, True, True),
        ("K05b", "line-end （", f + "（" + f, True, True),
        ("K06", "consecutive 。」", f + "終わり。」" + f, True, True),
        ("K08", "hanging ON", f + "終わり。" + f, True, True),
        ("K08b", "hanging OFF", f + "終わり。" + f, True, False),
    ]


def run_kinsoku_corpus_horizontal():
    desk = _desktop()
    doc = desk.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    _set_page(doc)
    font = _pick_font(doc)
    text = doc.Text
    cursor = text.createTextCursor()

    # Document settings snapshot (read)
    settings_info = {}
    try:
        # Document implements settings properties on some builds via getPropertySetInfo
        for name in ("CharacterCompressionType", "IsKernAsianPunctuation"):
            try:
                settings_info[name] = doc.getPropertyValue(name)
            except Exception as exc:
                settings_info[name] = "unavailable:%s" % exc
    except Exception as exc:
        settings_info["error"] = str(exc)

    text.insertString(cursor, "Stage E1 kinsoku corpus (horizontal)\n", False)
    text.insertString(
        cursor,
        "LO page ~70mm wide; 14pt Asian; automatic wraps only.\n\n",
        False,
    )

    meta_cases = []
    for cid, label, body, forbidden, hanging in _cases():
        text.insertString(cursor, "[%s] %s\n" % (cid, label), False)
        _append_para(
            text,
            cursor,
            body,
            forbidden=forbidden,
            hanging=hanging,
            font=font,
        )
        meta_cases.append(
            {
                "id": cid,
                "label": label,
                "ParaIsForbiddenRules": forbidden,
                "ParaIsHangingPunctuation": hanging,
                "font": font,
            }
        )

    out_dir = _artifact_dir()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    odt = os.path.join(out_dir, "kinsoku_e1_horizontal_%s.odt" % stamp)
    url = uno.systemPathToFileUrl(odt)
    doc.storeAsURL(url, ())

    meta = {
        "created": stamp,
        "path": odt,
        "direction": "horizontal",
        "page": PAGE,
        "margins": MARGINS,
        "font_preferred": font,
        "document_settings": settings_info,
        "cases": meta_cases,
        "note": "Visual: observe wrap near punct; do not insert manual breaks.",
    }
    meta_path = os.path.join(out_dir, "kinsoku_e1_horizontal_%s.json" % stamp)
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)

    _msg("kinsoku corpus", "Wrote %s" % odt)
    return odt


def g_exportedScripts():
    return (run_kinsoku_corpus_horizontal,)
