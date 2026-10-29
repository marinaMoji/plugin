# -*- coding: utf-8 -*-
"""
Warichū CharCombine spike as a LibreOffice **user macro**.

Runs *inside* soffice (Tools → Macros, or vnd.sun.star.script URL).
Writes artifacts next to this file when possible, else to ~/Desktop/warichu_spike_artifacts/.

Entry points (for the Macro dialog):
  run_spike()
"""

from __future__ import annotations

import json
import os
import re
import traceback
import zipfile
from datetime import datetime, timezone

import uno


def _artifact_dir():
    candidates = []
    # Prefer the repo spike folder if the developer copied fixtures from there
    here = os.path.dirname(os.path.abspath(__file__))
    # When installed as user macro, __file__ is under LibreOffice user Scripts
    repo = os.path.join(here, "artifacts")
    # Always-writable fallback
    desktop = os.path.join(os.path.expanduser("~"), "Desktop", "warichu_spike_artifacts")
    # Explicit override
    env = os.environ.get("MARINAMOJI_WARICHU_ARTIFACTS")
    if env:
        candidates.append(env)
    # Known marinaMoji checkout on this machine (developer convenience)
    candidates.append(
        os.path.join(
            os.path.expanduser("~"),
            "Code",
            "marinaMoji",
            "plugin",
            "libreoffice",
            "spikes",
            "warichu",
            "artifacts",
        )
    )
    # If running from the repo copy (not the user Scripts install)
    if os.path.basename(here) == "warichu" or os.path.isdir(
        os.path.join(here, "..", "..", "marinamoji_kaeriten")
    ):
        candidates.append(os.path.join(here, "artifacts"))
    candidates.append(desktop)
    candidates.append(repo)
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            probe = os.path.join(path, ".write_test")
            with open(probe, "w", encoding="utf-8") as fh:
                fh.write("ok")
            os.remove(probe)
            return path
        except Exception:
            continue
    return desktop


def _fixtures_path():
    here = os.path.dirname(os.path.abspath(__file__))
    for name in ("warichu_spike_fixtures.json", "fixtures.json"):
        path = os.path.join(here, name)
        if os.path.isfile(path):
            return path
    # Repo relative guess when macro was not installed via install_user_macro.sh
    guess = os.path.join(
        os.path.expanduser("~"),
        "Code",
        "marinaMoji",
        "plugin",
        "libreoffice",
        "spikes",
        "warichu",
        "fixtures.json",
    )
    return guess


def _msg(title, text):
    try:
        ctx = uno.getComponentContext()
        tk = ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
        peer = tk.createMessageBox(None, 1, 1, title, text[:1500])
        # MessageBox API varies; fall back to print
        if hasattr(peer, "execute"):
            peer.execute()
            return
    except Exception:
        pass
    print("%s: %s" % (title, text))


def _get_desktop():
    try:
        doc = XSCRIPTCONTEXT.getDesktop()  # noqa: F821 — injected in macro context
        return doc
    except NameError:
        ctx = uno.getComponentContext()
        return ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx
        )


def _prop(obj, name):
    try:
        return obj.getPropertyValue(name)
    except Exception as exc:
        return {"error": type(exc).__name__, "message": str(exc)}


def _set_prop(obj, name, value):
    try:
        obj.setPropertyValue(name, value)
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)}


def _inspect(cursor):
    return {
        "CharCombineIsOn": _prop(cursor, "CharCombineIsOn"),
        "CharCombinePrefix": _prop(cursor, "CharCombinePrefix"),
        "CharCombineSuffix": _prop(cursor, "CharCombineSuffix"),
        "string": cursor.getString() if hasattr(cursor, "getString") else None,
    }


def _apply(cursor, prefix, suffix):
    results = {
        "CharCombineIsOn": _set_prop(cursor, "CharCombineIsOn", True),
        "CharCombinePrefix": _set_prop(cursor, "CharCombinePrefix", prefix or ""),
        "CharCombineSuffix": _set_prop(cursor, "CharCombineSuffix", suffix or ""),
    }
    results["after"] = _inspect(cursor)
    return results


def _store_url(path):
    return uno.systemPathToFileUrl(os.path.abspath(path))


def _save_as(doc, path, filter_name):
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
        return {"ok": False, "error": type(exc).__name__, "message": str(exc), "path": path}


def _extract_combine_xml(odt_path, out_path):
    hits = []
    try:
        with zipfile.ZipFile(odt_path) as zf:
            for name in ("content.xml", "styles.xml"):
                if name not in zf.namelist():
                    continue
                data = zf.read(name).decode("utf-8")
                for match in re.finditer(r".{0,100}text-combine.{0,140}", data):
                    hits.append({"file": name, "snippet": match.group(0)})
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(hits, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        return {"ok": True, "hit_count": len(hits), "extract": out_path}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)}


def _append_paragraph(text, content):
    try:
        from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
    except ImportError:
        PARAGRAPH_BREAK = 0
    cursor = text.createTextCursor()
    cursor.gotoEnd(False)
    existing = text.getString() or ""
    if existing.strip():
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        cursor.gotoEnd(False)
    text.insertString(cursor, content, True)
    return cursor


def _lo_version_string():
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
        return " ".join(parts) if parts else "Unknown"
    except Exception as exc:
        return "Unknown (%s)" % exc


def run_spike(*_args):
    """Macro entry: build fixture doc, apply CharCombine, save, reopen, report."""
    out_dir = _artifact_dir()
    fixtures_path = _fixtures_path()
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "lo_version": _lo_version_string(),
        "fixtures_path": fixtures_path,
        "artifact_dir": out_dir,
        "cases": [],
        "roundtrip": {},
        "errors": [],
    }

    try:
        with open(fixtures_path, encoding="utf-8") as fh:
            fixtures = json.load(fh)
    except Exception as exc:
        _msg("warichū spike", "Could not read fixtures:\n%s\n%s" % (fixtures_path, exc))
        return

    desktop = _get_desktop()
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    text = doc.Text

    for case in fixtures.get("cases", []):
        entry = {"id": case["id"], "label": case["label"], "source_text": case["text"]}
        try:
            cursor = _append_paragraph(text, case["text"])
            brackets = case.get("brackets") or {}
            entry["apply"] = _apply(
                cursor, brackets.get("prefix", ""), brackets.get("suffix", "")
            )
            entry["inspect"] = _inspect(cursor)
            got = cursor.getString()
            entry["source_preserved"] = got == case["text"]
            entry["got_string"] = got
        except Exception as exc:
            entry["error"] = "%s: %s" % (type(exc).__name__, exc)
            entry["traceback"] = traceback.format_exc()
            report["errors"].append(case["id"])
        report["cases"].append(entry)

    odt_path = os.path.join(out_dir, "warichu_spike.odt")
    docx_path = os.path.join(out_dir, "warichu_spike.docx")
    report["save_odt"] = _save_as(doc, odt_path, "writer8")
    report["save_docx"] = _save_as(doc, docx_path, "MS Word 2007 XML")

    if report["save_odt"].get("ok"):
        report["odf_extract"] = _extract_combine_xml(
            odt_path, os.path.join(out_dir, "odf_combine_snippets.json")
        )

    # Reopen
    if report["save_odt"].get("ok"):
        try:
            doc.close(True)
        except Exception:
            pass
        reopened = desktop.loadComponentFromURL(_store_url(odt_path), "_blank", 0, ())
        enum = reopened.Text.createEnumeration()
        reopen_cases = []
        idx = 0
        n = len(fixtures.get("cases", []))
        while enum.hasMoreElements() and idx < n:
            para = enum.nextElement()
            if not hasattr(para, "createEnumeration"):
                continue
            portions = para.createEnumeration()
            while portions.hasMoreElements():
                portion = portions.nextElement()
                s = portion.getString() if hasattr(portion, "getString") else ""
                if not s:
                    continue
                reopen_cases.append(
                    {
                        "index": idx,
                        "string": s,
                        "combine": {
                            "CharCombineIsOn": _prop(portion, "CharCombineIsOn"),
                            "CharCombinePrefix": _prop(portion, "CharCombinePrefix"),
                            "CharCombineSuffix": _prop(portion, "CharCombineSuffix"),
                        },
                    }
                )
                idx += 1
                break
        report["roundtrip"]["reopen_odt"] = reopen_cases
        # Leave the reopened doc open so the user can screenshot alignment (T04)
        report["note"] = (
            "Reopened ODT left open for visual T04/T07 checks. "
            "Use marinaMoji Toggle vertical page for vertical test."
        )
    report["finished_at"] = datetime.now(timezone.utc).isoformat()

    report_path = os.path.join(out_dir, "spike_report.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # Capability matrix (automated slice)
    any_apply = any(
        ((c.get("apply") or {}).get("after") or {}).get("CharCombineIsOn") is True
        for c in report["cases"]
    )
    any_preserve = all(c.get("source_preserved") for c in report["cases"] if "error" not in c)
    any_reopen = any(
        (item.get("combine") or {}).get("CharCombineIsOn") is True
        for item in (report.get("roundtrip") or {}).get("reopen_odt") or []
    )
    odf_hits = (report.get("odf_extract") or {}).get("hit_count", 0)
    matrix = "\n".join(
        [
            "# LibreOffice warichū capability matrix (spike)",
            "",
            "Host: %s" % report.get("lo_version"),
            "Artifacts: %s" % out_dir,
            "",
            "| Capability | Status |",
            "|---|---|",
            "| T01 Insert CharCombineIsOn | %s |" % ("Verified" if any_apply else "Failed"),
            "| Source preserved | %s |" % ("Verified" if any_preserve else "Failed"),
            "| T08 Save ODT | %s |" % ("Verified" if report["save_odt"].get("ok") else "Failed"),
            "| T08 Reopen combine | %s |" % ("Verified" if any_reopen else "Failed"),
            "| ODF text-combine XML | %s (%s hits) |"
            % (("Verified" if odf_hits else "Unknown"), odf_hits),
            "| T09 Save DOCX | %s |" % ("Verified" if report["save_docx"].get("ok") else "Failed"),
            "| T04 Alignment | Unknown (inspect open document) |",
            "| T07 Vertical | Unknown (toggle page writing mode) |",
            "",
            "JSON: spike_report.json",
            "",
        ]
    )
    matrix_path = os.path.join(out_dir, "capability_matrix.md")
    with open(matrix_path, "w", encoding="utf-8") as fh:
        fh.write(matrix)

    summary = (
        "Artifacts: %s\nApply combine: %s\nReopen combine: %s\nODF hits: %s\nErrors: %s"
        % (
            out_dir,
            any_apply,
            any_reopen,
            odf_hits,
            ", ".join(report["errors"]) or "none",
        )
    )
    _msg("warichū spike finished", summary)
    return None


# Alias for Macro dialog clarity
g_exportedScripts = (run_spike,)
