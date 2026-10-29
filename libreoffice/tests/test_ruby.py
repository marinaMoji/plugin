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


def test_default_adjust_is_indent_block():
    """Group-ruby product default: Fig.124 → ODF distribute-space."""
    assert _RUBY_ADJUST_DEFAULT == _RUBY_ADJUST_INDENT_BLOCK
    assert _RUBY_ADJUST_INDENT_BLOCK == 4
    assert _RUBY_ADJUST_BLOCK == 3
    assert _RUBY_ADJUST_CENTER == 1


def test_adjust_for_base_mono_vs_group():
    assert _adjust_for_base("文") == _RUBY_ADJUST_CENTER
    assert _adjust_for_base("本") == _RUBY_ADJUST_CENTER
    assert _adjust_for_base("本文") == _RUBY_ADJUST_INDENT_BLOCK
    assert _adjust_for_base("国際") == _RUBY_ADJUST_INDENT_BLOCK


def main():
    test_expand_inside()
    test_expand_caret_after()
    test_expand_outside()
    test_base_preserved_contract()
    test_default_adjust_is_indent_block()
    test_adjust_for_base_mono_vs_group()
    print("All ruby helper tests passed.")


if __name__ == "__main__":
    main()
