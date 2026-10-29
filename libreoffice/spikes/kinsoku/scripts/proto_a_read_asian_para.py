#!/usr/bin/env python3
# Stage E1 Prototype A — read Asian paragraph composition settings (read-only).
#
# Usage (with Writer running, or via macro / APSO):
#   Import into LibreOffice user Scripts, or run under LO's python with UNO bridge.
#
# Does NOT modify the document. Does NOT change Tools → Options.

"""Read ParaIs* Asian typography flags and ForbiddenCharacters for the caret paragraph."""

from __future__ import annotations

PARA_PROPS = (
    "ParaIsForbiddenRules",
    "ParaIsHangingPunctuation",
    "ParaIsCharacterDistance",
)


def _get(obj, name, default=None):
    try:
        return obj.getPropertyValue(name)
    except Exception:
        return default


def read_paragraph_asian(text_cursor):
    """Return a dict of Asian paragraph props for the cursor's paragraph."""
    out = {}
    for name in PARA_PROPS:
        out[name] = _get(text_cursor, name)
    return out


def read_document_forbidden(doc):
    """Best-effort ForbiddenCharacters via document settings."""
    info = {"available": False}
    try:
        settings = doc.createInstance("com.sun.star.document.Settings")
    except Exception:
        settings = None
    if settings is None:
        try:
            settings = doc
        except Exception:
            return info
    try:
        xfc = settings.getPropertyValue("ForbiddenCharacters")
    except Exception:
        return info
    info["available"] = xfc is not None
    info["interface"] = type(xfc).__name__ if xfc is not None else None
    # Locale-specific getters vary by IDL revision; leave raw for experiment notes.
    info["note"] = "Inspect XForbiddenCharacters methods interactively; do not write."
    return info


def snapshot_selection(desktop=None):
    """
    Called from a LO macro context: returns JSON-serialisable snapshot.
    Expects XSCRIPTCONTEXT when run as a macro.
    """
    import json

    try:
        ctx = XSCRIPTCONTEXT  # noqa: F821 — LO macro global
        doc = ctx.getDocument()
        controller = doc.getCurrentController()
        selection = controller.getSelection()
    except Exception as exc:
        return {"error": "no_document", "detail": str(exc)}

    if selection is None or selection.getCount() < 1:
        return {"error": "no_selection"}

    cursor = selection.getByIndex(0)
    snap = {
        "paragraph_asian": read_paragraph_asian(cursor),
        "forbidden": read_document_forbidden(doc),
        "string_preview": "",
    }
    try:
        text = cursor.getString()
        snap["string_preview"] = (text[:80] + "…") if len(text) > 80 else text
    except Exception:
        pass
    return snap


def g_exportedScripts():
    return (snapshot_selection,)


if __name__ == "__main__":
    print("Prototype A: load as a LibreOffice Python macro and run snapshot_selection.")
    print("Properties of interest:", ", ".join(PARA_PROPS))
