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
# The input method types a Unicode character itself and removes the .txt once it
# has. The extension only steps in for a result that is still there after this
# long, i.e. one the input method could not deliver, so nothing is typed twice.
TEXT_GRACE_SECONDS = 4.0
_SEEN_FILE = "composer_seen"
_SEEN_TEXT_FILE = "composer_seen_text"


# Windows IME profile is AppData\LocalLow\<product> (Mozc GetLocalAppDataPath).
# Older plugin code and some docs looked under %LOCALAPPDATA% (AppData\Local).
# Branding: "marinaMoji", or "Mozc" for an unbranded build.
_WINDOWS_PRODUCT_DIRS = ("marinaMoji", "Mozc")


def _mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return -1.0


def _windows_profile_roots(home, local_app_data=None):
    """Directories that may contain <product>/character_composer_result.svg."""
    if local_app_data is not None:
        # Explicit root (unit tests): do not invent a LocalLow sibling.
        return [local_app_data]
    local = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
    stripped = local.rstrip("\\/")
    if os.path.basename(stripped).lower() == "local":
        local_low = os.path.join(os.path.dirname(stripped), "LocalLow")
    else:
        local_low = os.path.join(home, "AppData", "LocalLow")
    # Prefer LocalLow (where the IME actually writes).
    roots = [local_low, local]
    ordered = []
    seen = set()
    for root in roots:
        key = os.path.normcase(root)
        if key not in seen:
            seen.add(key)
            ordered.append(root)
    return ordered


def svg_path(platform=None, home=None, local_app_data=None):
    """Where the composer writes its SVG, or None where that is not wired up yet.

    On Windows, whichever product directory holds the newest result (LocalLow
    first, then Local).
    """
    platform = sys.platform if platform is None else platform
    home = os.path.expanduser("~") if home is None else home
    if platform == "win32":
        candidates = [
            os.path.join(base, d, "character_composer_result.svg")
            for base in _windows_profile_roots(home, local_app_data)
            for d in _WINDOWS_PRODUCT_DIRS
        ]
        existing = [p for p in candidates if os.path.isfile(p)]
        if existing:
            return max(existing, key=_mtime)
        return candidates[0]
    if platform == "darwin":
        base = os.path.join(home, "Library", "Application Support", "marinaMoji")
    elif platform.startswith("linux"):
        # Match the IME (system_util.cc): ~/.marinamoji if that directory exists,
        # else $XDG_CONFIG_HOME/marinamoji, else ~/.config/marinamoji. If more than
        # one result file exists (e.g. after a profile move), take the newest.
        xdg = os.environ.get("XDG_CONFIG_HOME")
        preferred = []
        legacy = os.path.join(home, ".marinamoji")
        if os.path.isdir(legacy):
            preferred.append(legacy)
        if xdg:
            preferred.append(os.path.join(xdg, "marinamoji"))
        preferred.append(os.path.join(home, ".config", "marinamoji"))
        candidates = [os.path.join(b, "character_composer_result.svg") for b in preferred]
        existing = [p for p in candidates if os.path.isfile(p)]
        if existing:
            return max(existing, key=_mtime)
        return candidates[0]
    else:
        return None
    return os.path.join(base, "character_composer_result.svg")


def text_path(platform=None, home=None, local_app_data=None):
    """Where the composer writes a Unicode character (.txt), same dirs as svg_path."""
    svg = svg_path(platform, home, local_app_data)
    if svg is None:
        return None
    if svg.endswith(".svg"):
        return svg[:-4] + ".txt"
    return svg + ".txt"


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


def _seen_text_path(cache_dir):
    return os.path.join(cache_dir, _SEEN_TEXT_FILE)


def _last_seen_text(cache_dir):
    try:
        with open(_seen_text_path(cache_dir), "r") as f:
            return float(f.read().strip())
    except (OSError, ValueError):
        return 0.0


def mark_seen_text(cache_dir, mtime):
    """Record that the Unicode .txt result with this mtime has been dealt with."""
    os.makedirs(cache_dir, exist_ok=True)
    try:
        with open(_seen_text_path(cache_dir), "w") as f:
            f.write(repr(mtime))
    except OSError:
        pass


def peek_fresh_text(cache_dir=None, now=None, path=None):
    """Return (text, mtime) for a Unicode composer result the input method left behind.

    A result younger than TEXT_GRACE_SECONDS is not returned yet (it is retried
    on the next poll): the input method normally types it and deletes the file.
    """
    import time

    path = text_path() if path is None else path
    if path is None:
        return None
    if cache_dir is None:
        cache_dir = os.path.join(tempfile.gettempdir(), "marinamoji_kaeriten")
    os.makedirs(cache_dir, exist_ok=True)
    now = time.time() if now is None else now
    try:
        mtime = os.path.getmtime(path)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except OSError:
        return None
    if not text or "<svg" in text:
        return None
    if len(text.encode("utf-8")) > 32:
        return None
    if mtime <= _last_seen_text(cache_dir):
        return None
    if now - mtime > FRESH_SECONDS:
        mark_seen_text(cache_dir, mtime)
        return None
    if now - mtime < TEXT_GRACE_SECONDS:
        return None  # the input method may still be committing it
    return text, mtime


def log(cache_dir, message):
    """Append a line to composer_handoff.log (an event job has no visible stderr)."""
    import time

    try:
        os.makedirs(cache_dir, exist_ok=True)
        with open(os.path.join(cache_dir, "composer_handoff.log"), "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (time.strftime("%H:%M:%S"), message))
    except OSError:
        pass
