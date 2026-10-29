#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for jidori approximation math (no LibreOffice)."""

import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "spikes", "jidori")
)

from jidori_math import count_graphemes, plan_jidori, plan_to_uno_values  # noqa: E402


def test_count_simple():
    assert count_graphemes("あいう") == 3
    assert count_graphemes("") == 0


def test_noop():
    p = plan_jidori("あい", 2)
    assert p.mode == "noop"
    assert p.scale_width_percent == 100


def test_expand():
    p = plan_jidori("あいう", 5)
    assert p.mode == "expand"
    assert p.scale_width_percent == 100
    # (5-3)/(3-1) = 1.0 em per gap
    assert abs(p.extra_per_gap_em - 1.0) < 1e-6
    scale, kern = plan_to_uno_values(p, 12.0)
    assert scale == 100
    assert kern == 240  # 1.0 em * 12 pt * 20 twips/pt


def test_shrink():
    p = plan_jidori("あいうえお", 3)
    assert p.mode == "shrink"
    assert p.scale_width_percent == 60  # 3/5
    scale, kern = plan_to_uno_values(p, 12.0)
    assert scale == 60
    assert kern == 0


def test_single_expand_refused():
    p = plan_jidori("あ", 3)
    assert p.mode == "invalid"


def test_vertical_expand_ok():
    p = plan_jidori("あいう", 5, vertical=True)
    assert p.mode == "expand"


def test_vertical_shrink_refused():
    p = plan_jidori("あいうえお", 3, vertical=True)
    assert p.mode == "invalid"


def test_ivs_and_combining_attach_to_base():
    assert count_graphemes("葛\U000E0100城") == 2
    assert count_graphemes("葛\uFE00城") == 2
    assert count_graphemes("か\u3099") == 1
    assert count_graphemes("\U000E0100") == 1  # orphan selector counts once


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
    print("all passed")
