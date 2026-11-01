#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for toolbar theme helpers (no LibreOffice)."""

import os
import re
import sys

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "..", "marinamoji_kaeriten")
sys.path.insert(0, SRC)

import marinamoji_theme as theme  # noqa: E402


def test_variant_for_face_color():
    assert theme.variant_for_face_color(0xFFFFFF) == theme.LIGHT
    assert theme.variant_for_face_color(0x1E1E1E) == theme.DARK
    assert theme.variant_for_face_color(0xFF1E1E1E) == theme.DARK  # alpha byte ignored


def test_variant_for_appearance_value():
    assert theme.variant_for_appearance_value(0) is None
    assert theme.variant_for_appearance_value(1) == theme.LIGHT
    assert theme.variant_for_appearance_value(2) == theme.DARK
    assert theme.variant_for_appearance_value("2") == theme.DARK
    assert theme.variant_for_appearance_value("nope") is None


def test_icon_files():
    assert theme.icon_file("apply_ruby", theme.LIGHT) == "icons/apply_ruby.svg"
    assert theme.icon_file("apply_ruby", theme.DARK) == "icons-dark/apply_ruby.svg"
    assert theme.icon_file("copy_plain_text", theme.DARK) == "icons-dark/export_txt.svg"


def test_commands_match_addons_and_icons_exist():
    xcu = open(os.path.join(SRC, "Addons.xcu"), encoding="utf-8").read()
    in_images = set(re.findall(
        r"<value>%origin%/icons/([a-z_]+)\.svg</value>", xcu))
    for command in theme.COMMANDS:
        stem = theme._ICON_STEM.get(command, command)
        assert stem in in_images, command
        assert os.path.isfile(os.path.join(SRC, "icons", stem + ".svg")), command


def test_dark_icons_recolor():
    sys.path.insert(0, os.path.join(HERE, ".."))
    import dark_icons

    out = dark_icons.darken('<path stroke="#48484a"/><path stroke="#005fef"/>')
    assert "#48484a" not in out and "#005fef" not in out
    assert "#f2f2f7" in out and "#75adff" in out


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
