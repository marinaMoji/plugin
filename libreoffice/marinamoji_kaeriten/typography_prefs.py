# -*- coding: utf-8 -*-
"""
Per-document Japanese typography preferences (ODT-backed).

Stored as namespaced UserDefinedProperties on DocumentProperties so they
survive save/reopen without rewriting body text. Only written when the user
explicitly changes a preference (or another marinaMoji operation requires it).

Conceptual model (only EmphasisDefault is used today):

    DocumentTypographyPreferences
        ├── EmphasisDefault
        ├── RubyDefaultAlignment       [future]
        ├── RubyDefaultSize            [future]
        ├── WarichuLayout              [future]
        └── TypographyProfile          [future]
"""

from __future__ import annotations

# Namespaced keys — keep stable for ODT portability.
PROP_EMPHASIS_DEFAULT = "marinaMoji.Typography.EmphasisDefault"

# Built-in default when the document has no preference yet.
EMPHASIS_BUILTIN_DEFAULT = "BLACK_SESAME"

# Semantic ids that map to native Writer CharEmphasis (see emphasis.py).
EMPHASIS_STYLE_IDS = (
    "BLACK_SESAME",
    "BLACK_DOT",
    "WHITE_CIRCLE",
    "DOT",
)


def normalize_emphasis_style_id(value):
    """Return a known style id, or None if missing/invalid."""
    if value is None:
        return None
    if isinstance(value, dict) and "error" in value:
        return None
    text = str(value).strip()
    if not text:
        return None
    key = text.upper().replace("-", "_").replace(" ", "_")
    # Accept a few aliases from docs / older drafts.
    aliases = {
        "ACCENT": "BLACK_SESAME",
        "ACCENT_ABOVE": "BLACK_SESAME",
        "SESAME": "BLACK_SESAME",
        "DISK": "BLACK_DOT",
        "DISC": "BLACK_DOT",
        "DISK_ABOVE": "BLACK_DOT",
        "CIRCLE": "WHITE_CIRCLE",
        "CIRCLE_ABOVE": "WHITE_CIRCLE",
        "DOT_ABOVE": "DOT",
    }
    if key in aliases:
        key = aliases[key]
    if key in EMPHASIS_STYLE_IDS:
        return key
    return None


def resolve_emphasis_default(stored):
    """Resolve stored metadata → style used for Apply.

    Invalid/unsupported stored values are preserved by the caller for display,
    but Apply falls back to the built-in default.
    """
    normalized = normalize_emphasis_style_id(stored)
    if normalized is None:
        return EMPHASIS_BUILTIN_DEFAULT
    return normalized


def _user_defined_properties(doc):
    try:
        props = doc.getDocumentProperties()
    except Exception:
        try:
            props = doc.DocumentProperties
        except Exception:
            return None
    try:
        return props.UserDefinedProperties
    except Exception:
        return None


def get_raw_emphasis_default(doc):
    """Return the raw stored string, or None if absent."""
    udp = _user_defined_properties(doc)
    if udp is None:
        return None
    try:
        info = udp.getPropertySetInfo()
        if info is None or not info.hasPropertyByName(PROP_EMPHASIS_DEFAULT):
            return None
        return udp.getPropertyValue(PROP_EMPHASIS_DEFAULT)
    except Exception:
        return None


def get_emphasis_default(doc):
    """Style id used when applying the document default (always valid)."""
    return resolve_emphasis_default(get_raw_emphasis_default(doc))


def set_emphasis_default(doc, style_id):
    """Persist the document default. Returns (ok, message).

    Does not rewrite existing CharEmphasis on passages.
    """
    normalized = normalize_emphasis_style_id(style_id)
    if normalized is None:
        return False, "Unsupported emphasis style."
    udp = _user_defined_properties(doc)
    if udp is None:
        return False, "Could not access document properties."
    try:
        info = udp.getPropertySetInfo()
        has = info is not None and info.hasPropertyByName(PROP_EMPHASIS_DEFAULT)
        if not has:
            # REMOVEABLE lets users clear it later; value is a string.
            try:
                from com.sun.star.beans.PropertyAttribute import REMOVEABLE
            except Exception:
                REMOVEABLE = 1  # fallback if enum unavailable in tests
            udp.addProperty(PROP_EMPHASIS_DEFAULT, REMOVEABLE, normalized)
        else:
            udp.setPropertyValue(PROP_EMPHASIS_DEFAULT, normalized)
        try:
            doc.setModified(True)
        except Exception:
            pass
        return True, normalized
    except Exception as exc:
        return False, "%s" % type(exc).__name__
