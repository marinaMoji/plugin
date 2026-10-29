#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for jidori policy / restore payload (no LibreOffice)."""

import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "marinamoji_kaeriten")
)

from jidori import (  # noqa: E402
    bookmark_name_for_id,
    classify_jidori_length,
    decode_restore_payload,
    encode_restore_payload,
    id_from_bookmark_name,
    initial_n,
    is_cjk_jidori_text,
    udp_key_for_id,
)
from jidori_math import plan_jidori  # noqa: E402


def test_cjk_ok():
    assert is_cjk_jidori_text("日本")
    assert is_cjk_jidori_text("あいう")
    assert is_cjk_jidori_text("漢𠮷")


def test_latin_refused():
    assert not is_cjk_jidori_text("ABC")
    assert not is_cjk_jidori_text("12")
    assert not is_cjk_jidori_text("日A本")


def test_newline_refused():
    assert not is_cjk_jidori_text("日\n本")


def test_initial_n_no_surprise_compress():
    assert initial_n(8, 5) == 8
    assert initial_n(3, 5) == 5
    assert initial_n(3, None) == 5
    assert initial_n(7, None) == 7


def test_length_policy():
    assert classify_jidori_length(3)[0] == "ok"
    assert classify_jidori_length(9)[0] == "confirm"
    assert classify_jidori_length(17)[0] == "refuse"


def test_bookmark_roundtrip():
    name = bookmark_name_for_id("abc123")
    assert id_from_bookmark_name(name) == "abc123"
    assert udp_key_for_id("abc123").startswith("marinaMoji.Typography.Jidori.")


def test_payload_json():
    raw = encode_restore_payload({"scale": 90, "kern": 40, "N": 5})
    data = decode_restore_payload(raw)
    assert data["scale"] == 90
    assert data["N"] == 5


def test_vertical_shrink_invalid():
    p = plan_jidori("あいうえお", 3, vertical=True)
    assert p.mode == "invalid"


def test_horizontal_shrink_ok():
    p = plan_jidori("あいうえお", 3, vertical=False)
    assert p.mode == "shrink"
    assert p.scale_width_percent == 60


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
    print("all passed")
