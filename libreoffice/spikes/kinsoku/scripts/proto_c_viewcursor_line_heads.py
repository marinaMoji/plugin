#!/usr/bin/env python3
# Stage E1 Prototype C — EXPERIMENTAL view-cursor line-head probe (read-only).
#
# WARNING: This does NOT equal Writer's internal break table.
# Multiportions (ruby/warichū), vertical writing, and fields can mislead.
# Use only to document feasibility limits — not for production diagnostics.

"""Probe layout line starts via XLineCursor.isAtStartOfLine (preferred) and goDown walk."""

from __future__ import annotations


def probe_is_at_start_of_line(view_cursor, text_range):
    """
    Preferred check: move view cursor to text_range, query XLineCursor.isAtStartOfLine.

    Returns dict with at_start (bool|None) and failure_mode if any.
    Requires active SwView. Does not modify document content (may move selection).
    """
    out = {"at_start": None, "method": "XLineCursor.isAtStartOfLine"}
    try:
        view_cursor.gotoRange(text_range, False)
    except Exception as exc:
        out["failure_mode"] = "gotoRange"
        out["detail"] = str(exc)
        return out
    try:
        # queryInterface pattern varies by bridge; try attribute then method
        if hasattr(view_cursor, "isAtStartOfLine"):
            out["at_start"] = bool(view_cursor.isAtStartOfLine())
        else:
            out["failure_mode"] = "no_isAtStartOfLine"
    except Exception as exc:
        out["failure_mode"] = "isAtStartOfLine"
        out["detail"] = str(exc)
    return out


def collect_line_start_chars(view_cursor, max_lines=200):
    """
    Starting from the beginning of the current paragraph selection,
    record the first character of each visual line by goDown(1, False).

    Returns a list of dicts: {line_index, char, failure_mode?}.
    Weaker than probe_is_at_start_of_line for single-character checks.
    """
    results = []
    try:
        view_cursor.gotoStart(False)
    except Exception as exc:
        return [{"failure_mode": "gotoStart", "detail": str(exc)}]

    for i in range(max_lines):
        try:
            view_cursor.goRight(1, True)
            ch = view_cursor.getString()
            view_cursor.collapseToStart()
        except Exception as exc:
            results.append({"line_index": i, "failure_mode": "read", "detail": str(exc)})
            break
        at_start = None
        try:
            if hasattr(view_cursor, "isAtStartOfLine"):
                at_start = bool(view_cursor.isAtStartOfLine())
        except Exception:
            pass
        results.append(
            {
                "line_index": i,
                "char": ch,
                "isAtStartOfLine": at_start,
                "confidence": "heuristic",
            }
        )
        try:
            moved = view_cursor.goDown(1, False)
        except Exception as exc:
            results.append({"line_index": i, "failure_mode": "goDown", "detail": str(exc)})
            break
        if not moved:
            break
    return results


NOTES = """
Limitations to record when testing:
1. Requires an active Writer view (not headless-safe).
2. Prefer isAtStartOfLine after gotoRange over goDown walking alone.
3. Implementation uses IsAtLeftMargin — validate vertical writing separately.
4. Ruby / warichū / fields: accessible LINE indices may disagree with model string.
5. Do not emit default-on KINSOKU_LINE_START production diagnostics from this alone.
"""


def g_exportedScripts():
    return ()


if __name__ == "__main__":
    print(NOTES)
