# -*- coding: utf-8 -*-
"""
Vertical ruby geometry spike — character frames vs optical ink.

Creates vertical Writer docs for CENTER / BLOCK / INDENT_BLOCK on 本文/もと,
with two Japanese fonts, with and without character document grid.

Does NOT change marinaMoji product defaults. Measurement only.

Entry: run_ruby_vertical_geometry_spike()
"""

from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, timezone

import uno

ADJUSTS = (
    ("CENTER", 1),
    ("BLOCK", 3),
    ("INDENT_BLOCK", 4),
)

# Prefer one Mincho + one Gothic that macOS LO can resolve.
FONT_CANDIDATES = (
    ("mincho", ("Hiragino Mincho ProN", "ヒラギノ明朝 ProN", "YuMincho")),
    ("gothic", ("Hiragino Sans", "ヒラギノ角ゴシック", "Hiragino Kaku Gothic ProN", "YuGothic")),
)

BASE = "本文"
READING = "もと"
BODY_PT = 28.0  # large for measurable PDF positions


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
        "vertical_geometry",
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


def _para_break():
    from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK

    return PARAGRAPH_BREAK


def _resolve_font(cursor, candidates):
    for name in candidates:
        _set(cursor, "CharFontNameAsian", name)
        _set(cursor, "CharFontName", name)
        got = _get(cursor, "CharFontNameAsian")
        if got == name:
            return name
        if isinstance(got, str) and name.split()[0] in got:
            return got
    return candidates[0]


def _style(cursor, font, size=BODY_PT):
    _set(cursor, "CharLocaleAsian", _ja())
    _set(cursor, "CharFontNameAsian", font)
    _set(cursor, "CharFontName", font)
    _set(cursor, "CharHeightAsian", size)
    _set(cursor, "CharHeight", size)
    _set(cursor, "CharWeight", 100.0)
    _set(cursor, "CharCombineIsOn", False)
    # Do not clear RubyText here — sticky empty wrappers pollute ODF.


def _append(text):
    c = text.createTextCursor()
    c.gotoEnd(False)
    if (text.getString() or "").strip():
        text.insertControlCharacter(c, _para_break(), False)
        c.gotoEnd(False)
    return c


def _set_vertical(doc):
    from com.sun.star.text.WritingMode2 import RL_TB

    styles = doc.StyleFamilies.getByName("PageStyles")
    page = styles.getByName("Standard")
    ok = _set(page, "WritingMode", RL_TB)
    return {"ok": ok, "WritingMode": "RL_TB"}


def _configure_grid(doc, *, enabled):
    """Character document grid (lines+chars) or none.

    Writer page-style props: GridMode 0=NONE, 1=LINES, 2=LINES_AND_CHARS.
    """
    styles = doc.StyleFamilies.getByName("PageStyles")
    page = styles.getByName("Standard")
    info = {"requested": enabled}
    if enabled:
        # LINES_AND_CHARS = 2
        info["GridMode_set"] = _set(page, "GridMode", 2)
        # Base height ~ body size in 1/100 mm: 28pt ≈ 9.87mm ≈ 987
        info["GridBaseHeight_set"] = _set(page, "GridBaseHeight", 987)
        # Ruby height ~ half: ~493
        info["GridRubyHeight_set"] = _set(page, "GridRubyHeight", 493)
        info["GridDisplay_set"] = _set(page, "GridDisplay", True)
        info["GridPrint_set"] = _set(page, "GridPrint", True)
        info["GridLines_set"] = _set(page, "GridLines", 20)
    else:
        info["GridMode_set"] = _set(page, "GridMode", 0)
        info["GridDisplay_set"] = _set(page, "GridDisplay", False)
        info["GridPrint_set"] = _set(page, "GridPrint", False)
    info["GridMode"] = _get(page, "GridMode")
    info["GridBaseHeight"] = _get(page, "GridBaseHeight")
    info["GridRubyHeight"] = _get(page, "GridRubyHeight")
    return info


def _save(doc, path):
    from com.sun.star.beans import PropertyValue

    if os.path.exists(path):
        os.remove(path)
    url = uno.systemPathToFileUrl(os.path.abspath(path))
    props = (PropertyValue(Name="FilterName", Value="writer8"),)
    doc.storeAsURL(url, props)


def _insert_case(text, font, label, adjust):
    c = _append(text)
    text.insertString(c, label, True)
    _style(c, font, 11.0)
    c.collapseToEnd()

    c = _append(text)
    text.insertString(c, BASE, True)
    _style(c, font, BODY_PT)
    ok_t = _set(c, "RubyText", READING)
    ok_a = _set(c, "RubyAdjust", adjust)
    _set(c, "RubyPosition", 0)
    _set(c, "RubyAdjust", adjust)
    props = {
        "label": label,
        "font": font,
        "base": BASE,
        "reading": READING,
        "RubyAdjust": _get(c, "RubyAdjust"),
        "RubyText": _get(c, "RubyText"),
        "RubyPosition": _get(c, "RubyPosition"),
        "set_text_ok": ok_t,
        "set_adjust_ok": ok_a,
        "base_preserved": c.getString() == BASE,
        "CharHeightAsian": _get(c, "CharHeightAsian"),
        "CharFontNameAsian": _get(c, "CharFontNameAsian"),
    }
    c.collapseToEnd()
    # Marker after ruby so PDF extraction can anchor the column.
    text.insertString(c, "｜", True)
    _style(c, font, BODY_PT)
    c.collapseToEnd()
    return props


def _build_doc(desktop, font_key, font_name, grid_on, out_dir):
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    text = doc.Text
    # Clear default empty paragraph content by writing into first para.
    c0 = text.createTextCursor()
    c0.gotoStart(False)
    text.insertString(c0, "", False)

    vert = _set_vertical(doc)
    grid = _configure_grid(doc, enabled=grid_on)

    # Probe font on a throwaway write
    probe = _append(text)
    resolved = _resolve_font(probe, (font_name,))
    # Remove probe content by overwriting heading below — keep simple: style only
    probe.collapseToEnd()

    title = (
        "Vertical ruby geometry — font=%s (%s) — grid=%s — body=%spt — LO UNO"
        % (resolved, font_key, "ON" if grid_on else "OFF", int(BODY_PT))
    )
    c = text.createTextCursor()
    c.gotoStart(False)
    # If document already has empty para, write title into start
    if not (text.getString() or "").strip():
        text.insertString(c, title, True)
        _style(c, resolved, 10.0)
        _set(c, "CharWeight", 150.0)
        c.collapseToEnd()
    else:
        h = _append(text)
        text.insertString(h, title, True)
        _style(h, resolved, 10.0)
        _set(h, "CharWeight", 150.0)

    note = _append(text)
    text.insertString(
        note,
        "Frame vs optical: JLREQ uses square character frames / advance, "
        "not ink centres. Field shading OFF for screenshots.",
        True,
    )
    _style(note, resolved, 9.0)

    cases = []
    for name, adj in ADJUSTS:
        label = "[%s] %s/%s RubyAdjust=%s" % (font_key, BASE, READING, name)
        cases.append(_insert_case(text, resolved, label, adj))

    # Theoretical frame model (em units; base advance=1, ruby advance=0.5)
    theory = _theoretical_frames()

    tag = "%s_grid%s" % (font_key, "on" if grid_on else "off")
    odt = os.path.join(out_dir, "ruby_vert_geom_%s.odt" % tag)
    _save(doc, odt)
    try:
        doc.close(True)
    except Exception:
        pass

    return {
        "tag": tag,
        "font_key": font_key,
        "font_resolved": resolved,
        "grid": grid,
        "vertical": vert,
        "body_pt": BODY_PT,
        "odt": odt,
        "cases": cases,
        "theory_em": theory,
    }


def _theoretical_frames():
    """Character-frame model for 2 base @ 1em + 2 ruby @ 0.5em (JLREQ).

    Block axis runs 0 → 2 (top→bottom in vertical). Positions are frame
    edges and centres in base-em units — not glyph ink.
    """
    base_adv = 1.0
    ruby_adv = 0.5
    n_base = 2
    n_ruby = 2
    base_len = n_base * base_adv  # 2.0
    ruby_solid = n_ruby * ruby_adv  # 1.0
    free = base_len - ruby_solid  # 1.0

    base_frames = []
    for i in range(n_base):
        start = i * base_adv
        end = start + base_adv
        base_frames.append(
            {"ch": BASE[i], "start": start, "end": end, "centre": (start + end) / 2}
        )

    def ruby_layout(lead, inter, trail, mode):
        # lead/inter/trail in base-em; inter is total gap between the two ruby frames
        frames = []
        pos = lead
        for i in range(n_ruby):
            start = pos
            end = start + ruby_adv
            frames.append(
                {
                    "ch": READING[i],
                    "start": start,
                    "end": end,
                    "centre": (start + end) / 2,
                }
            )
            pos = end + (inter if i == 0 else 0)
        return {
            "mode": mode,
            "lead": lead,
            "inter": inter,
            "trail": trail,
            "ruby_frames": frames,
            "pair_offsets": [
                {
                    "base": base_frames[i]["ch"],
                    "ruby": frames[i]["ch"],
                    "base_centre": base_frames[i]["centre"],
                    "ruby_centre": frames[i]["centre"],
                    "delta_centre": frames[i]["centre"] - base_frames[i]["centre"],
                }
                for i in range(n_ruby)
            ],
            "notes": "",
        }

    # CENTER: solid ruby (no inter ruby gap), centred on base
    lead_c = free / 2.0  # 0.5
    center = ruby_layout(lead_c, 0.0, lead_c, "CENTER")
    center["notes"] = "Solid ruby block centred on base span (no letter distribution)."

    # BLOCK / Fig.125: edges flush; all free space between ruby letters
    block = ruby_layout(0.0, free, 0.0, "BLOCK")
    block["notes"] = (
        "JLREQ Fig.125 / ODF distribute-letter: align first/last edges; "
        "space only between ruby characters."
    )

    # INDENT_BLOCK / Fig.124 / JIS 1:2:1 for one inter-gap (n_ruby=2 → one gap)
    # lead:inter:trail = 1:2:1 → lead=free/4, inter=free/2, trail=free/4
    indent = ruby_layout(free / 4.0, free / 2.0, free / 4.0, "INDENT_BLOCK")
    indent["notes"] = (
        "JLREQ Fig.124 / JIS X 4051 ratio 1:2:1 (ODF distribute-space). "
        "For 2×½em ruby on 2×1em base, ruby frame centres coincide with base centres."
    )

    return {
        "assumptions": {
            "base_advance_em": base_adv,
            "ruby_advance_em": ruby_adv,
            "base_len_em": base_len,
            "ruby_solid_em": ruby_solid,
            "free_em": free,
            "note": "Advances = square character frames (JLREQ), not ink bbox.",
        },
        "base_frames": base_frames,
        "layouts": {"CENTER": center, "BLOCK": block, "INDENT_BLOCK": indent},
    }


def run_ruby_vertical_geometry_spike(*_args):
    out_dir = _artifact_dir()
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "lo_version": _lo_version(),
        "purpose": (
            "Measure vertical ruby frame geometry for CENTER/BLOCK/INDENT_BLOCK; "
            "distinguish character-frame alignment from optical glyph centres; "
            "no product default change."
        ),
        "artifact_dir": out_dir,
        "documents": [],
    }
    desktop = _desktop()
    try:
        # Resolve fonts once
        probe_doc = desktop.loadComponentFromURL(
            "private:factory/swriter", "_blank", 0, ()
        )
        pc = probe_doc.Text.createTextCursor()
        fonts = {}
        for key, cands in FONT_CANDIDATES:
            fonts[key] = _resolve_font(pc, cands)
        try:
            probe_doc.close(True)
        except Exception:
            pass

        report["fonts_resolved"] = fonts

        for key, font_name in fonts.items():
            for grid_on in (False, True):
                report["documents"].append(
                    _build_doc(desktop, key, font_name, grid_on, out_dir)
                )

        report["theory_em"] = _theoretical_frames()
        report["ok"] = True
    except Exception as exc:
        report["ok"] = False
        report["error"] = str(exc)
        report["traceback"] = traceback.format_exc()

    path = os.path.join(out_dir, "vertical_geometry_report.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    # LO macros must not return a Python dict (UNO cannot convert it).
    return None
