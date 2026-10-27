# -*- coding: utf-8 -*-
"""
marinaMoji character composer -> LibreOffice Writer (no UNO here, so it is unit-testable).

For a structure with no Unicode character the composer (Insert) writes a drawing as
character_composer_result.svg in the marinaMoji user-profile directory. When the
Writer window regains focus (the composer has just closed) the extension takes a
*fresh, unseen* result and inserts it at the cursor.
"""

import os
import re
import sys
import tempfile

FRESH_SECONDS = 120  # older than this is a leftover from an earlier session
_SEEN_FILE = "composer_seen"


def svg_path(platform=None, home=None):
    """Where the composer writes its SVG, or None where that is not wired up yet."""
    platform = sys.platform if platform is None else platform
    home = os.path.expanduser("~") if home is None else home
    if platform == "darwin":
        base = os.path.join(home, "Library", "Application Support", "marinaMoji")
    elif platform.startswith("linux"):
        base = os.path.join(home, ".config", "marinamoji")
    else:
        return None
    return os.path.join(base, "character_composer_result.svg")


def svg_dimensions(svg):
    """(width, height) from the root <svg> element; (1, 1) if unreadable."""
    root = re.search(r"<svg\b[^>]*>", svg)
    head = root.group(0) if root else ""

    def number(name):
        m = re.search(r"\s%s=\"([\d.]+)" % name, head)
        return float(m.group(1)) if m else 0.0

    width, height = number("width"), number("height")
    if width <= 0 or height <= 0:
        box = re.search(r"viewBox=\"[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)", head)
        if box:
            width, height = float(box.group(1)), float(box.group(2))
    if width <= 0 or height <= 0:
        return 1.0, 1.0
    return width, height


def _seen_path(cache_dir):
    return os.path.join(cache_dir, _SEEN_FILE)


def _last_seen(cache_dir):
    try:
        with open(_seen_path(cache_dir), "r") as f:
            return float(f.read().strip())
    except (OSError, ValueError):
        return 0.0


def _mark_seen(cache_dir, mtime):
    try:
        with open(_seen_path(cache_dir), "w") as f:
            f.write(repr(mtime))
    except OSError:
        pass


def mark_seen(cache_dir, mtime):
    """Record that the result with this modification time has been dealt with."""
    os.makedirs(cache_dir, exist_ok=True)
    _mark_seen(cache_dir, mtime)


def peek_fresh_svg(cache_dir=None, now=None, path=None):
    """Return (svg_text, mtime) for a fresh result not yet dealt with, else None.

    Does not mark it: call mark_seen() once it has been inserted (or given up
    on), so a moment with no Writer document open does not lose the result.
    Anything older than FRESH_SECONDS is ignored and marked.
    """
    import time

    path = svg_path() if path is None else path
    if path is None:
        return None
    if cache_dir is None:
        cache_dir = os.path.join(tempfile.gettempdir(), "marinamoji_kaeriten")
    os.makedirs(cache_dir, exist_ok=True)
    now = time.time() if now is None else now
    try:
        mtime = os.path.getmtime(path)
        with open(path, "r", encoding="utf-8") as f:
            svg = f.read()
    except OSError:
        return None
    if "<svg" not in svg:
        return None
    if mtime <= _last_seen(cache_dir):
        return None
    if now - mtime > FRESH_SECONDS:
        _mark_seen(cache_dir, mtime)  # stale: never insert it later either
        return None
    return svg.strip(), mtime


def take_fresh_svg(cache_dir=None, now=None, path=None):
    """peek_fresh_svg() and mark the result as dealt with."""
    found = peek_fresh_svg(cache_dir, now, path)
    if found is not None:
        if cache_dir is None:
            cache_dir = os.path.join(tempfile.gettempdir(), "marinamoji_kaeriten")
        _mark_seen(cache_dir, found[1])
    return found


def log(cache_dir, message):
    """Append a line to composer_handoff.log (an event job has no visible stderr)."""
    import time

    try:
        os.makedirs(cache_dir, exist_ok=True)
        with open(os.path.join(cache_dir, "composer_handoff.log"), "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (time.strftime("%H:%M:%S"), message))
    except OSError:
        pass
