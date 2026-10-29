# -*- coding: utf-8 -*-
"""
Stage B warichū corpus — native CharCombineIsOn spans.

Creates horizontal + vertical ODTs, optional PDF/DOCX, ODF analysis JSON,
and a visual-inspection checklist. Does not modify Writer's renderer.

Entry: run_stage_b_corpus()
"""

from __future__ import annotations

import json
import os
import re
import traceback
import zipfile
from datetime import datetime, timezone

import uno

FIXTURE_PATHS = (
    os.path.join(
        os.path.expanduser("~"),
        "Code",
        "marinaMoji",
        "plugin",
        "libreoffice",
        "spikes",
        "warichu",
        "fixtures_stage_b.json",
    ),
)

JP_FONTS = (
    "Hiragino Mincho ProN",
    "ヒラギノ明朝 ProN",
    "Noto Sans JP",
    "YuMincho",
    "游明朝体",
    "Hiragino Sans",
    "ヒラギノ角ゴシック",
    "Hiragino Mincho Pro",
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
        "stage_b",
    )
    desktop = os.path.join(
        os.path.expanduser("~"), "Desktop", "warichu_stage_b_artifacts"
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


def _pick_font(cursor, preferred=None):
    names = list(preferred or ()) + list(JP_FONTS)
    seen = set()
    for name in names:
        if not name or name in seen:
            continue
        seen.add(name)
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
        return {"ok": True, "path": path, "filter": filter_name}
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
    _set(cursor, "CharLocaleAsian", _ja_locale())
    _set(cursor, "CharFontNameAsian", font_name)
    _set(cursor, "CharFontName", font_name)
    _set(cursor, "CharHeightAsian", size_pt)
    _set(cursor, "CharHeight", size_pt)
    _set(cursor, "CharWeight", 100.0)
    _set(cursor, "CharCombineIsOn", False)
    _set(cursor, "CharCombinePrefix", "")
    _set(cursor, "CharCombineSuffix", "")
    _set(cursor, "CharStyleName", "")


def _code_points(s):
    return ["U+%04X" % ord(ch) for ch in s]


def _insert_body_plus_note(text, body, note, font_name, *, with_brackets=False):
    cursor = _append_paragraph(text)

    text.insertString(cursor, body, True)
    _style_body_run(cursor, font_name)
    cursor.collapseToEnd()

    text.insertString(cursor, note, True)
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
        "note_codepoints": _code_points(note),
        "with_brackets": with_brackets,
        "apply": apply,
        "after": after,
        "source_preserved": after["string"] == note,
        "note_len": len(note),
    }


def _set_page_vertical(doc):
    """Best-effort: set first text page style to vertical (RLTB)."""
    result = {"ok": False}
    try:
        from com.sun.star.text.WritingMode2 import RL_TB

        styles = doc.StyleFamilies.getByName("PageStyles")
        page = styles.getByName("Standard")
        _set(page, "WritingMode", RL_TB)
        result = {"ok": True, "WritingMode": "RL_TB"}
    except Exception as exc:
        result = {"ok": False, "error": type(exc).__name__, "message": str(exc)}
        try:
            # Fallback: paragraph-level WritingMode if page fails
            text = doc.Text
            cursor = text.createTextCursor()
            cursor.gotoStart(False)
            cursor.gotoEnd(True)
            from com.sun.star.text.WritingMode2 import RL_TB

            _set(cursor, "WritingMode", RL_TB)
            result = {"ok": True, "WritingMode": "RL_TB", "scope": "selection_fallback"}
        except Exception as exc2:
            result["fallback_error"] = str(exc2)
    return result


def _load_fixtures():
    for path in FIXTURE_PATHS:
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                return json.load(fh), path
    # Embedded minimal fallback if fixture file missing
    return {
        "cases": [
            {
                "id": "B01_classic",
                "group": "balance",
                "body": "本文",
                "note": "割り注は、良いです。",
                "writing": "horizontal",
                "brackets": False,
            },
            {
                "id": "B16_bracket_uno_classic",
                "group": "brackets",
                "body": "本文",
                "note": "割り注は、良いです。",
                "writing": "horizontal",
                "brackets": True,
            },
        ]
    }, "(embedded)"


def _extract_odf(odt_path, out_path):
    info = {
        "combine_text_styles": [],
        "paragraph_combine_lines": [],
        "sample_paras": [],
        "notes_from_spans": [],
        "ok": False,
    }
    try:
        with zipfile.ZipFile(odt_path) as zf:
            data = zf.read("content.xml").decode("utf-8")
        for m in re.finditer(
            r'<style:style style:name="([^"]+)" style:family="text"[^>]*>.*?</style:style>',
            data,
            re.DOTALL,
        ):
            block = m.group(0)
            if 'text-combine="lines"' in block:
                info["combine_text_styles"].append(
                    {
                        "name": m.group(1),
                        "has_brackets": "text-combine-start-char" in block,
                        "xml": block[:500],
                    }
                )
        for m in re.finditer(
            r'<style:style style:name="([^"]+)" style:family="paragraph"[^>]*>.*?</style:style>',
            data,
            re.DOTALL,
        ):
            block = m.group(0)
            if 'text-combine="lines"' in block:
                info["paragraph_combine_lines"].append(m.group(1))
        for m in re.finditer(
            r'<text:span text:style-name="([^"]+)">([^<]*)</text:span>', data
        ):
            info["notes_from_spans"].append(
                {"style": m.group(1), "text": m.group(2), "len": len(m.group(2))}
            )
        for m in re.finditer(r"<text:p[^>]*>.*?</text:p>", data):
            para = m.group(0)
            if "text:span" in para:
                info["sample_paras"].append(para[:500])
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


def _heading(text, font_name, title):
    c = _append_paragraph(text)
    text.insertString(c, title, True)
    _style_body_run(c, font_name, 12.0)
    _set(c, "CharWeight", 150.0)
    c.collapseToEnd()


def _build_document(desktop, cases, font_name, writing, report_key, out_dir):
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    text = doc.Text
    section = {
        "writing": writing,
        "font": font_name,
        "cases": [],
        "errors": [],
        "vertical_setup": None,
    }
    if writing == "vertical":
        section["vertical_setup"] = _set_page_vertical(doc)

    try:
        _heading(
            text,
            font_name,
            "Stage B corpus — %s — font=%s" % (writing, font_name),
        )
        _heading(
            text,
            font_name,
            "Visual: record actual upper/lower split; do not assume mid-string.",
        )

        for case in cases:
            if case.get("writing") != writing:
                continue
            cid = case["id"]
            try:
                label = _append_paragraph(text)
                text.insertString(
                    label,
                    "[%s] %s" % (cid, case.get("notes") or case.get("group") or ""),
                    True,
                )
                _style_body_run(label, font_name, 10.0)
                label.collapseToEnd()

                entry = _insert_body_plus_note(
                    text,
                    case.get("body") or "本文",
                    case["note"],
                    font_name,
                    with_brackets=bool(case.get("brackets")),
                )
                entry["id"] = cid
                entry["group"] = case.get("group")
                entry["writing"] = writing
                section["cases"].append(entry)
            except Exception:
                section["errors"].append("%s\n%s" % (cid, traceback.format_exc()))
    except Exception:
        section["errors"].append(traceback.format_exc())

    odt = os.path.join(out_dir, "warichu_stage_b_%s.odt" % writing)
    section["save_odt"] = _save(doc, odt, "writer8")
    pdf = os.path.join(out_dir, "warichu_stage_b_%s.pdf" % writing)
    section["save_pdf"] = _save(doc, pdf, "writer_pdf_Export")
    docx = os.path.join(out_dir, "warichu_stage_b_%s.docx" % writing)
    section["save_docx"] = _save(doc, docx, "MS Word 2007 XML")

    if section["save_odt"].get("ok"):
        section["odf"] = _extract_odf(
            odt, os.path.join(out_dir, "odf_%s.json" % writing)
        )

    try:
        doc.close(True)
    except Exception:
        pass
    return section


def _write_checklist(out_dir, report):
    lines = [
        "# Stage B visual inspection checklist",
        "",
        "LibreOffice: **%s**" % report.get("lo_version"),
        "Generated: %s" % report.get("finished_at"),
        "",
        "For each case, open the ODT/PDF and fill:",
        "",
        "| Case | Observed upper | Observed lower | Stretch visible? | Punct odd? | Pass/Fail/Unclear |",
        "|---|---|---|---|---|---|",
    ]
    for writing in ("horizontal", "vertical"):
        sec = report.get(writing) or {}
        for c in sec.get("cases") or []:
            lines.append(
                "| %s |  |  |  |  |  |" % c.get("id")
            )
    lines.extend(
        [
            "",
            "## Bracket paint (B16–B17, B21)",
            "",
            "- Expected: delimiters （） at ~2× warichū size flanking two lines.",
            "- Stage A: UNO Prefix/Suffix collapsed paint — confirm or refute here.",
            "",
            "## Integrity",
            "",
            "- [ ] Reopen ODT: combine styles still on spans",
            "- [ ] Edit body before note: combine remains",
            "- [ ] Edit note text: still two lines",
            "- [ ] PDF readable; DOCX noted separately",
            "",
        ]
    )
    path = os.path.join(out_dir, "VISUAL_CHECKLIST.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def run_stage_b_corpus(*_args):
    out_dir = _artifact_dir()
    fixtures, fixture_path = _load_fixtures()
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "lo_version": _lo_version(),
        "artifact_dir": out_dir,
        "fixture_path": fixture_path,
        "stage": "B",
        "purpose": "Empirical warichū corpus: balance, punct, mixed, vertical, brackets",
        "source_tree_examined_stage_a": "LibreOffice/core master (web) — binary is 26.8.0.3",
        "errors": [],
    }

    desktop = _desktop()
    probe = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    font_name = _pick_font(
        probe.Text.createTextCursor(), fixtures.get("fonts_preferred")
    )
    report["font_selected"] = font_name
    try:
        probe.close(True)
    except Exception:
        pass

    cases = fixtures.get("cases") or []
    report["horizontal"] = _build_document(
        desktop, cases, font_name, "horizontal", "horizontal", out_dir
    )
    report["vertical"] = _build_document(
        desktop, cases, font_name, "vertical", "vertical", out_dir
    )

    # Integrity probe: reopen horizontal ODT and check first note string
    odt_h = os.path.join(out_dir, "warichu_stage_b_horizontal.odt")
    integrity = {"reopen": False}
    if os.path.isfile(odt_h):
        try:
            doc2 = desktop.loadComponentFromURL(_store_url(odt_h), "_blank", 0, ())
            integrity["reopen"] = True
            integrity["full_text_len"] = len(doc2.Text.getString() or "")
            # Spot-check classic note still present as contiguous characters
            full = doc2.Text.getString() or ""
            integrity["classic_note_in_text"] = "割り注は、良いです。" in full
            integrity["vs_candidate_in_text"] = "葛" in full
            doc2.close(True)
        except Exception as exc:
            integrity["error"] = str(exc)
    report["integrity_spotcheck"] = integrity

    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    checklist = _write_checklist(out_dir, report)
    report["visual_checklist"] = checklist

    with open(os.path.join(out_dir, "stage_b_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    h = report.get("horizontal") or {}
    v = report.get("vertical") or {}
    summary = "\n".join(
        [
            "# Stage B corpus run",
            "",
            "| Item | Value |",
            "|---|---|",
            "| LO | %s |" % report["lo_version"],
            "| Font | %s |" % font_name,
            "| H cases | %s |" % len(h.get("cases") or []),
            "| V cases | %s |" % len(v.get("cases") or []),
            "| H bare styles | %s |"
            % ((h.get("odf") or {}).get("bare_combine_styles")),
            "| H bracket styles | %s |"
            % ((h.get("odf") or {}).get("bracket_combine_styles")),
            "| Classic preserved (reopen) | %s |"
            % integrity.get("classic_note_in_text"),
            "| Checklist | %s |" % checklist,
            "",
        ]
    )
    with open(os.path.join(out_dir, "SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write(summary)

    _msg(
        "Stage B corpus",
        "H=%s V=%s font=%s\n%s"
        % (len(h.get("cases") or []), len(v.get("cases") or []), font_name, out_dir),
    )
    return None


g_exportedScripts = (run_stage_b_corpus,)
