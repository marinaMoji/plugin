#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ruby helpers that do not need LibreOffice."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "marinamoji_kaeriten"))

from ruby import (  # noqa: E402
    _RUBY_ADJUST_BLOCK,
    _RUBY_ADJUST_CENTER,
    _RUBY_ADJUST_DEFAULT,
    _RUBY_ADJUST_INDENT_BLOCK,
    _RUBY_ADJUST_LEFT,
    _adjust_for_base,
    expand_ruby_span_indices,
    text_unchanged_after_ruby_change,
)


def test_expand_inside():
    flags = [False, True, True, True, False]
    assert expand_ruby_span_indices(flags, 2) == (1, 4)


def test_expand_caret_after():
    flags = [True, True, False]
    assert expand_ruby_span_indices(flags, 2) == (0, 2)


def test_expand_outside():
    flags = [False, True, True]
    assert expand_ruby_span_indices(flags, 0) is None


def test_base_preserved_contract():
    assert text_unchanged_after_ruby_change("漢字", "漢字") is True
    assert text_unchanged_after_ruby_change("漢字", "漢 字") is False


def test_default_adjust_is_left():
    """LEFT = Writer native default; stable beside vertical warichū."""
    assert _RUBY_ADJUST_DEFAULT == _RUBY_ADJUST_LEFT
    assert _RUBY_ADJUST_LEFT == 0
    assert _RUBY_ADJUST_INDENT_BLOCK == 4  # kept for future Fig.124 UI
    assert _RUBY_ADJUST_BLOCK == 3
    assert _RUBY_ADJUST_CENTER == 1


def test_adjust_for_base_uses_left():
    assert _adjust_for_base("文") == _RUBY_ADJUST_LEFT
    assert _adjust_for_base("本文") == _RUBY_ADJUST_LEFT
    assert _adjust_for_base("国際") == _RUBY_ADJUST_LEFT


def main():
    test_expand_inside()
    test_expand_caret_after()
    test_expand_outside()
    test_base_preserved_contract()
    test_default_adjust_is_left()
    test_adjust_for_base_uses_left()
    print("All ruby helper tests passed.")


def test_adjacent_ruby_words_with_different_readings_stay_separate():
    from ruby import expand_ruby_span_by_reading

    r = ["とう", "とう", "きょう", "きょう"]  # 2 chars + 2 chars, different readings
    assert expand_ruby_span_by_reading(r, 0) == (0, 2)
    assert expand_ruby_span_by_reading(r, 1) == (0, 2)
    assert expand_ruby_span_by_reading(r, 2) == (2, 4)
    assert expand_ruby_span_by_reading(r, 4) == (2, 4)  # caret after last char
    assert expand_ruby_span_by_reading(["", "あ", "あ", ""], 3) == (1, 3)
    assert expand_ruby_span_by_reading(["", ""], 1) is None
    assert expand_ruby_span_by_reading(["あ", "あ"], 1) == (0, 2)


if __name__ == "__main__":
    main()
