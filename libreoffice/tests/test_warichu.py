#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Warichū helpers that do not need LibreOffice (unit + smoke logic)."""

import os
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "marinamoji_kaeriten"))

from warichu import (  # noqa: E402
    expand_combine_span_indices,
    selection_covers_whole_paragraph_text,
    text_unchanged_after_clear,
)


def test_whole_paragraph_exact():
    assert selection_covers_whole_paragraph_text("割注試験", "割注試験") is True


def test_partial_note_not_whole():
    assert selection_covers_whole_paragraph_text("割注", "本文割注") is False


def test_body_plus_note_selection_not_whole():
    assert (
        selection_covers_whole_paragraph_text(
            "割り注は、良いです。", "割り注割り注は、良いです。"
        )
        is False
    )


def test_empty():
    assert selection_covers_whole_paragraph_text("", "本文") is False
    assert selection_covers_whole_paragraph_text("本文", "") is False


def test_expand_caret_inside_run():
    # 本文[割注試験] — flags for note only; index into note string
    flags = [True, True, True, True]
    assert expand_combine_span_indices(flags, 2) == (0, 4)


def test_expand_caret_at_start():
    flags = [False, False, True, True, True]
    assert expand_combine_span_indices(flags, 2) == (2, 5)


def test_expand_caret_after_run_uses_left():
    flags = [True, True, True, False]
    assert expand_combine_span_indices(flags, 3) == (0, 3)


def test_expand_caret_at_end_of_string():
    flags = [True, True]
    assert expand_combine_span_indices(flags, 2) == (0, 2)


def test_expand_outside_returns_none():
    flags = [False, False, True, True]
    assert expand_combine_span_indices(flags, 0) is None
    assert expand_combine_span_indices(flags, 1) is None


def test_expand_empty():
    assert expand_combine_span_indices([], 0) is None


def test_text_preserved_contract():
    note = "割り注は、良いです。"
    assert text_unchanged_after_clear(note, note) is True
    assert text_unchanged_after_clear(note, note + " ") is False


def test_smoke_odt_fixture_has_bare_combine():
    """ODT round-trip smoke against Stage B corpus if present."""
    root = os.path.join(
        os.path.dirname(__file__),
        "..",
        "spikes",
        "warichu",
        "artifacts",
        "stage_b",
        "warichu_stage_b_horizontal.odt",
    )
    if not os.path.isfile(root):
        print("SKIP: stage_b horizontal ODT not present")
        return
    with zipfile.ZipFile(root) as zf:
        content = zf.read("content.xml").decode("utf-8")
    assert 'style:text-combine="lines"' in content
    assert "割り注は、良いです。" in content
    # Bare combine style exists; bracketed style may also exist for B16
    assert 'style:family="text"' in content


def test_smoke_odt_vs16_preserved():
    root = os.path.join(
        os.path.dirname(__file__),
        "..",
        "spikes",
        "warichu",
        "artifacts",
        "stage_b",
        "warichu_stage_b_horizontal.odt",
    )
    if not os.path.isfile(root):
        print("SKIP: stage_b horizontal ODT not present")
        return
    with zipfile.ZipFile(root) as zf:
        content = zf.read("content.xml").decode("utf-8")
    # U+845B U+E0100 sequence from B15
    assert "\u845b\U000e0100" in content


def main():
    test_whole_paragraph_exact()
    test_partial_note_not_whole()
    test_body_plus_note_selection_not_whole()
    test_empty()
    test_expand_caret_inside_run()
    test_expand_caret_at_start()
    test_expand_caret_after_run_uses_left()
    test_expand_caret_at_end_of_string()
    test_expand_outside_returns_none()
    test_expand_empty()
    test_text_preserved_contract()
    test_smoke_odt_fixture_has_bare_combine()
    test_smoke_odt_vs16_preserved()
    print("All warichū helper tests passed.")


if __name__ == "__main__":
    main()
