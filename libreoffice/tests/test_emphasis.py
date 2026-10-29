#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emphasis + typography preference helpers (no LibreOffice required)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "marinamoji_kaeriten"))

from emphasis import (  # noqa: E402
    _EMPHASIS_ACCENT_ABOVE,
    _EMPHASIS_CIRCLE_ABOVE,
    _EMPHASIS_DISK_ABOVE,
    _EMPHASIS_DOT_ABOVE,
    _EMPHASIS_NONE,
    expand_emphasis_span_indices,
    short_name,
    style_ids,
    style_to_uno,
    text_unchanged_after_emphasis_change,
    uno_to_style,
)
from typography_prefs import (  # noqa: E402
    EMPHASIS_BUILTIN_DEFAULT,
    normalize_emphasis_style_id,
    resolve_emphasis_default,
)


def test_expand_inside():
    flags = [False, True, True, True, False]
    assert expand_emphasis_span_indices(flags, 2) == (1, 4)


def test_expand_caret_after():
    flags = [True, True, False]
    assert expand_emphasis_span_indices(flags, 2) == (0, 2)


def test_expand_outside():
    flags = [False, True, True]
    assert expand_emphasis_span_indices(flags, 0) is None


def test_base_preserved_contract():
    assert text_unchanged_after_emphasis_change("漢字", "漢字") is True
    assert text_unchanged_after_emphasis_change("漢字", "漢 字") is False


def test_semantic_mapping():
    assert style_to_uno("BLACK_SESAME") == _EMPHASIS_ACCENT_ABOVE
    assert style_to_uno("BLACK_DOT") == _EMPHASIS_DISK_ABOVE
    assert style_to_uno("WHITE_CIRCLE") == _EMPHASIS_CIRCLE_ABOVE
    assert style_to_uno("DOT") == _EMPHASIS_DOT_ABOVE
    assert style_to_uno("WHITE_SESAME") is None
    assert uno_to_style(_EMPHASIS_ACCENT_ABOVE) == "BLACK_SESAME"
    assert uno_to_style(_EMPHASIS_NONE) is None


def test_builtin_default_is_black_sesame():
    assert EMPHASIS_BUILTIN_DEFAULT == "BLACK_SESAME"
    assert "BLACK_SESAME" in style_ids()
    assert short_name("BLACK_SESAME", "ja") == "黒ゴマ"


def test_preference_normalize_and_fallback():
    assert normalize_emphasis_style_id("black_sesame") == "BLACK_SESAME"
    assert normalize_emphasis_style_id("ACCENT") == "BLACK_SESAME"
    assert normalize_emphasis_style_id("WHITE_SESAME") is None
    assert normalize_emphasis_style_id("") is None
    assert resolve_emphasis_default(None) == "BLACK_SESAME"
    assert resolve_emphasis_default("bogus") == "BLACK_SESAME"
    assert resolve_emphasis_default("WHITE_CIRCLE") == "WHITE_CIRCLE"


def test_passage_override_does_not_equal_default_change():
    """Document default resolution is independent of a passage UNO value."""
    doc_default = resolve_emphasis_default("BLACK_SESAME")
    passage = uno_to_style(_EMPHASIS_CIRCLE_ABOVE)
    assert doc_default == "BLACK_SESAME"
    assert passage == "WHITE_CIRCLE"
    assert doc_default != passage


def main():
    test_expand_inside()
    test_expand_caret_after()
    test_expand_outside()
    test_base_preserved_contract()
    test_semantic_mapping()
    test_builtin_default_is_black_sesame()
    test_preference_normalize_and_fallback()
    test_passage_override_does_not_equal_default_change()
    print("All emphasis helper tests passed.")


if __name__ == "__main__":
    main()
