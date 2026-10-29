#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Throwaway LibreOffice warichū (CharCombine) feasibility spike.

Uses LibreOffice's bundled Python + UNO. Does NOT modify the product extension.

Typical usage (macOS):

  # Terminal A — start a listening LibreOffice (quit other Writer first):
  /Applications/LibreOffice.app/Contents/MacOS/soffice \\
    --headless --norestore --nofirststartwizard \\
    --accept="socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext"

  # Terminal B — run this with LO's Python:
  /Applications/LibreOffice.app/Contents/Resources/python \\
    libreoffice/spikes/warichu/run_spike.py

Artifacts land in ./artifacts/ (ODT, DOCX, XML extracts, JSON report).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
ARTIFACTS = SPIKE_DIR / "artifacts"
FIXTURES_PATH = SPIKE_DIR / "fixtures.json"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 2002


def _die(msg: str, code: int = 1) -> None:
    print("ERROR:", msg, file=sys.stderr)
    sys.exit(code)


def _wait_port(host: str, port: int, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError as exc:
            last_err = exc
            time.sleep(0.25)
    _die("LibreOffice UNO socket not open on %s:%s (%s). Start soffice --accept=..." % (host, port, last_err))


def _connect(host: str, port: int):
    try:
        import uno  # noqa: WPS433 — only available in LO Python
        from com.sun.star.connection import NoConnectException
    except ImportError:
        _die(
            "Cannot import uno. Run this script with LibreOffice's Python, e.g.\n"
            "  /Applications/LibreOffice.app/Contents/Resources/python %s" % __file__
        )

    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local
    )
    url = "uno:socket,host=%s,port=%d;urp;StarOffice.ComponentContext" % (host, port)
    try:
        ctx = resolver.resolve(url)
    except NoConnectException as exc:
        _die("UNO connect failed: %s" % exc)
    desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    return uno, ctx, desktop


def _lo_version(desktop) -> str:
    try:
        cfg = desktop  # noqa: F841 — placeholder; use ConfigurationProvider via ctx later
    except Exception:
        pass
    # Best-effort: read from soffice --version via env is elsewhere; store Unknown here
    # and let the shell wrapper fill host_version if present.
    return os.environ.get("MARINAMOJI_LO_VERSION", "Unknown")


def _prop(cursor, name: str):
    try:
        return cursor.getPropertyValue(name)
    except Exception as exc:
        return {"error": type(exc).__name__, "message": str(exc)}


def _set_prop(cursor, name: str, value):
    try:
        cursor.setPropertyValue(name, value)
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)}


def _inspect_combine(cursor) -> dict:
    return {
        "CharCombineIsOn": _prop(cursor, "CharCombineIsOn"),
        "CharCombinePrefix": _prop(cursor, "CharCombinePrefix"),
        "CharCombineSuffix": _prop(cursor, "CharCombineSuffix"),
        "string": cursor.getString() if hasattr(cursor, "getString") else None,
    }


def _apply_combine(cursor, prefix: str, suffix: str) -> dict:
    results = {
        "CharCombineIsOn": _set_prop(cursor, "CharCombineIsOn", True),
        "CharCombinePrefix": _set_prop(cursor, "CharCombinePrefix", prefix or ""),
        "CharCombineSuffix": _set_prop(cursor, "CharCombineSuffix", suffix or ""),
    }
    results["after"] = _inspect_combine(cursor)
    return results


def _clear_combine(cursor) -> dict:
    results = {
        "CharCombineIsOn": _set_prop(cursor, "CharCombineIsOn", False),
        "CharCombinePrefix": _set_prop(cursor, "CharCombinePrefix", ""),
        "CharCombineSuffix": _set_prop(cursor, "CharCombineSuffix", ""),
    }
    results["after"] = _inspect_combine(cursor)
    return results


def _store_url(path: Path) -> str:
    import uno

    return uno.systemPathToFileUrl(str(path.resolve()))


def _save_as(doc, path: Path, filter_name: str) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    try:
        import uno
        from com.sun.star.beans import PropertyValue

        props = []
        p = PropertyValue()
        p.Name = "FilterName"
        p.Value = filter_name
        props.append(p)
        p2 = PropertyValue()
        p2.Name = "Overwrite"
        p2.Value = True
        props.append(p2)
        doc.storeAsURL(_store_url(path), tuple(props))
        return {"ok": True, "path": str(path), "filter": filter_name}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc), "path": str(path)}


def _extract_combine_xml(odt_path: Path, out_path: Path) -> dict:
    """Pull style:text-combine (and nearby) snippets from ODT package."""
    hits = []
    try:
        with zipfile.ZipFile(odt_path) as zf:
            for name in ("content.xml", "styles.xml"):
                if name not in zf.namelist():
                    continue
                data = zf.read(name).decode("utf-8")
                for match in re.finditer(r".{0,80}text-combine.{0,120}", data):
                    hits.append({"file": name, "snippet": match.group(0)})
                # Also catch FO-style combine attributes if present
                for match in re.finditer(r".{0,80}combine.{0,80}", data, flags=re.IGNORECASE):
                    snip = match.group(0)
                    if "text-combine" in snip or "Combine" in snip or "combine" in snip.lower():
                        if not any(h["snippet"] == snip for h in hits):
                            hits.append({"file": name, "snippet": snip})
        out_path.write_text(
            json.dumps(hits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return {"ok": True, "hit_count": len(hits), "extract": str(out_path)}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)}


def _new_writer(desktop):
    return desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())


def _append_paragraph(text, content: str):
    """Insert a new paragraph of `content` and return a cursor selecting it."""
    try:
        from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
    except ImportError:
        PARAGRAPH_BREAK = 0

    cursor = text.createTextCursor()
    cursor.gotoEnd(False)
    # Avoid a leading empty paragraph on a brand-new document.
    existing = text.getString() or ""
    if existing.strip():
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        cursor.gotoEnd(False)
    text.insertString(cursor, content, True)  # absorb → selection is the new text
    return cursor


def run_cases(desktop, fixtures: dict, out_dir: Path) -> dict:
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "lo_version_env": _lo_version(desktop),
        "python": sys.version,
        "cases": [],
        "roundtrip": {},
        "errors": [],
    }

    doc = _new_writer(desktop)
    text = doc.Text

    for case in fixtures["cases"]:
        entry = {"id": case["id"], "label": case["label"], "source_text": case["text"]}
        try:
            cursor = _append_paragraph(text, case["text"])
            brackets = case.get("brackets") or {}
            entry["apply"] = _apply_combine(
                cursor, brackets.get("prefix", ""), brackets.get("suffix", "")
            )
            entry["inspect"] = _inspect_combine(cursor)
            # Soft check: source string unchanged
            got = cursor.getString()
            entry["source_preserved"] = got == case["text"]
            entry["got_string"] = got
        except Exception as exc:
            entry["error"] = "%s: %s" % (type(exc).__name__, exc)
            entry["traceback"] = traceback.format_exc()
            report["errors"].append(case["id"])
        report["cases"].append(entry)

    odt_path = out_dir / "warichu_spike.odt"
    docx_path = out_dir / "warichu_spike.docx"
    report["save_odt"] = _save_as(doc, odt_path, "writer8")
    report["save_docx"] = _save_as(doc, docx_path, "MS Word 2007 XML")

    if report["save_odt"].get("ok"):
        report["odf_extract"] = _extract_combine_xml(
            odt_path, out_dir / "odf_combine_snippets.json"
        )

    # Reopen ODT and inspect first paragraph portion properties
    if report["save_odt"].get("ok"):
        try:
            doc.close(True)
        except Exception:
            pass
        reopened = desktop.loadComponentFromURL(_store_url(odt_path), "_blank", 0, ())
        enum = reopened.Text.createEnumeration()
        reopen_cases = []
        idx = 0
        while enum.hasMoreElements() and idx < len(fixtures["cases"]):
            para = enum.nextElement()
            # Walk text portions
            if hasattr(para, "createEnumeration"):
                portions = para.createEnumeration()
                while portions.hasMoreElements():
                    portion = portions.nextElement()
                    try:
                        ptype = portion.getPropertyValue("TextPortionType")
                    except Exception:
                        ptype = None
                    if ptype and str(ptype) not in ("Text", "0"):
                        # skip non-text if identifiable
                        continue
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
        try:
            reopened.close(True)
        except Exception:
            pass
    else:
        try:
            doc.close(True)
        except Exception:
            pass

    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    return report


def write_matrix(report: dict, path: Path) -> None:
    """Draft capability matrix from automated evidence only."""

    def status_for(case_ok: bool) -> str:
        return "Verified" if case_ok else "Unsupported/Failed"

    any_apply = False
    any_preserve = False
    any_roundtrip_on = False
    for c in report.get("cases", []):
        after = (c.get("apply") or {}).get("after") or {}
        if after.get("CharCombineIsOn") is True:
            any_apply = True
        if c.get("source_preserved"):
            any_preserve = True
    for item in (report.get("roundtrip") or {}).get("reopen_odt") or []:
        if (item.get("combine") or {}).get("CharCombineIsOn") is True:
            any_roundtrip_on = True

    odf_hits = (report.get("odf_extract") or {}).get("hit_count", 0)

    lines = [
        "# LibreOffice warichū capability matrix (spike)",
        "",
        "Generated by `run_spike.py`. Status values are from **automated** checks only.",
        "Alignment screenshots (T04) and accessibility (T10) remain manual.",
        "",
        "| Capability | Status | Evidence |",
        "|---|---|---|",
        "| Host / version | Recorded | `%s` / env `%s` |"
        % (report.get("python", "").split()[0], report.get("lo_version_env")),
        "| T01 Insert CharCombineIsOn | %s | cases[].apply |"
        % status_for(any_apply),
        "| T02 Inspect properties | %s | cases[].inspect |"
        % status_for(any_apply),
        "| Source string preserved on apply | %s | cases[].source_preserved |"
        % status_for(any_preserve),
        "| T08 Save ODT | %s | save_odt |"
        % status_for(bool((report.get("save_odt") or {}).get("ok"))),
        "| T08 Reopen combine flag | %s | roundtrip.reopen_odt |"
        % status_for(any_roundtrip_on),
        "| ODF text-combine (or combine) in XML | %s | odf_combine_snippets.json (%s hits) |"
        % (("Verified" if odf_hits else "Unknown/None"), odf_hits),
        "| T09 Save DOCX | %s | save_docx |"
        % status_for(bool((report.get("save_docx") or {}).get("ok"))),
        "| T04 Unequal alignment | Unknown | needs GUI screenshot |",
        "| T05 Manual break without text change | Unknown | not automated |",
        "| T07 Vertical writing | Unknown | not automated |",
        "",
        "Full JSON: `artifacts/spike_report.json`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="LibreOffice CharCombine warichū spike")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--skip-wait", action="store_true")
    args = parser.parse_args(argv)

    if not FIXTURES_PATH.is_file():
        _die("Missing fixtures: %s" % FIXTURES_PATH)

    fixtures = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    if not args.skip_wait:
        print("Waiting for UNO socket %s:%d ..." % (args.host, args.port))
        _wait_port(args.host, args.port)

    print("Connecting…")
    _uno, _ctx, desktop = _connect(args.host, args.port)
    print("Running fixture cases…")
    report = run_cases(desktop, fixtures, ARTIFACTS)

    report_path = ARTIFACTS / "spike_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    matrix_path = ARTIFACTS / "capability_matrix.md"
    write_matrix(report, matrix_path)

    print("Wrote", report_path)
    print("Wrote", matrix_path)
    if report.get("errors"):
        print("Case errors:", ", ".join(report["errors"]))
        return 2
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
