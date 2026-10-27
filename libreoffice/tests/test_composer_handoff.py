#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Composer hand-off tests (no LibreOffice required)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "marinamoji_kaeriten"))
import composer_handoff as h  # noqa: E402

SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="60" height="40" viewBox="0 0 60 40"></svg>'


def test_svg_path_per_platform(tmp_path):
    assert h.svg_path("darwin", "/Users/a").endswith(
        "Library/Application Support/marinaMoji/character_composer_result.svg"
    )
    assert h.svg_path("linux", "/home/a") == "/home/a/.config/marinamoji/character_composer_result.svg"
    assert h.svg_path("win32", "C:/u") is None


def test_svg_dimensions():
    assert h.svg_dimensions(SVG) == (60.0, 40.0)
    assert h.svg_dimensions('<svg viewBox="0 0 24 12"></svg>') == (24.0, 12.0)
    assert h.svg_dimensions("<svg></svg>") == (1.0, 1.0)


def test_fresh_result_is_taken_once(tmp_path):
    svg = tmp_path / "r.svg"
    svg.write_text(SVG, encoding="utf-8")
    cache = str(tmp_path / "cache")
    mtime = os.path.getmtime(svg)
    first = h.take_fresh_svg(cache, now=mtime + 5, path=str(svg))
    assert first == (SVG, mtime)
    assert h.take_fresh_svg(cache, now=mtime + 6, path=str(svg)) is None


def test_new_result_after_an_old_one_is_taken(tmp_path):
    svg = tmp_path / "r.svg"
    svg.write_text(SVG, encoding="utf-8")
    cache = str(tmp_path / "cache")
    m1 = os.path.getmtime(svg)
    assert h.take_fresh_svg(cache, now=m1 + 1, path=str(svg)) is not None
    os.utime(svg, (m1 + 10, m1 + 10))
    assert h.take_fresh_svg(cache, now=m1 + 11, path=str(svg)) is not None


def test_stale_result_is_ignored_and_not_retried(tmp_path):
    svg = tmp_path / "r.svg"
    svg.write_text(SVG, encoding="utf-8")
    cache = str(tmp_path / "cache")
    mtime = os.path.getmtime(svg)
    assert h.take_fresh_svg(cache, now=mtime + h.FRESH_SECONDS + 1, path=str(svg)) is None
    assert h.take_fresh_svg(cache, now=mtime + 1, path=str(svg)) is None


def test_missing_or_non_svg_file(tmp_path):
    cache = str(tmp_path / "cache")
    assert h.take_fresh_svg(cache, path=str(tmp_path / "none.svg")) is None
    bad = tmp_path / "bad.svg"
    bad.write_text("hello", encoding="utf-8")
    assert h.take_fresh_svg(cache, path=str(bad)) is None
