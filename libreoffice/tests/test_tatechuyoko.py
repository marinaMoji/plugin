#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tate-chū-yoko validation helpers (no LibreOffice required)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "marinamoji_kaeriten"))

from tatechuyoko import (  # noqa: E402
    CONFIRM,
    OK,
    REFUSE,
    _ROTATION_90,
    _WM_CONTEXT,
    _WM_LR_TB,
    _WM_PAGE,
    _WM_TB_RL,
    classify_run,
    classify_selection,
    expand_tatechuyoko_span_indices,
    find_recommended_run_at_caret,
    grapheme_len,
    resolve_is_vertical,
    text_unchanged_after_tatechuyoko_change,
)


def test_grapheme_len_basic():
    assert grapheme_len("12") == 2
    assert grapheme_len("１２") == 2
    assert grapheme_len("令和") == 2
    assert grapheme_len("") == 0


def test_classify_recommended():
    for s in ("12", "25", "99", "AB", "１２"):
        d = classify_selection(s)
        assert d["verdict"] == OK, s
        assert d["length"] == 2


def test_classify_extended():
    for s in ("123", "2026", "ABC", "3.5", "10%"):
        d = classify_selection(s)
        assert d["verdict"] == CONFIRM, s


def test_classify_inappropriate():
    for s in ("令和", "日本", "こんにちは", "令和12年", "12年", "令"):
        d = classify_selection(s)
        assert d["verdict"] == REFUSE, s


def test_classify_length_edges():
    assert classify_selection("1")["verdict"] == REFUSE
    assert classify_selection("12345")["verdict"] == REFUSE
    assert classify_selection("")["verdict"] == REFUSE


def test_explicit_selection_not_shrunk():
    """Explicit 令和12年 must refuse — never silently become 12."""
    d = classify_selection("令和12年")
    assert d["verdict"] == REFUSE
    assert "12" in d["message_en"] or "digits" in d["message_en"].lower() or "Select" in d["message_en"]


def test_caret_finds_two_digits():
    text = "令和12年"
    # Indices: 令0 和1 1→2 2→3 年4
    assert find_recommended_run_at_caret(text, 2) == (2, 4)
    assert find_recommended_run_at_caret(text, 3) == (2, 4)
    assert find_recommended_run_at_caret(text, 4) == (2, 4)  # after digits
    assert find_recommended_run_at_caret(text, 2) == (2, 4)


def test_caret_before_digits():
    text = "令和12年"
    assert find_recommended_run_at_caret(text, 2) == (2, 4)


def test_caret_in_japanese_no_match():
    text = "令和12年"
    assert find_recommended_run_at_caret(text, 0) is None
    assert find_recommended_run_at_caret(text, 1) is None


def test_caret_inside_long_number_no_slice():
    text = "西暦2026年"
    # Must not pick 20 or 26 out of 2026
    for i in range(len(text)):
        found = find_recommended_run_at_caret(text, i)
        if found is not None:
            assert text[found[0] : found[1]] != "20"
            assert text[found[0] : found[1]] != "26"
            assert text[found[0] : found[1]] != "02"
    # Caret squarely in 2026 → None
    idx = text.index("2")
    assert find_recommended_run_at_caret(text, idx) is None
    assert find_recommended_run_at_caret(text, idx + 2) is None


def test_caret_latin_pair():
    text = "型AB式"
    assert find_recommended_run_at_caret(text, 1) == (1, 3)
    assert find_recommended_run_at_caret(text, 2) == (1, 3)


def test_expand_span_indices():
    flags = [False, True, True, False]
    assert expand_tatechuyoko_span_indices(flags, 2) == (1, 3)


def test_base_preserved():
    assert text_unchanged_after_tatechuyoko_change("12", "12") is True
    assert text_unchanged_after_tatechuyoko_change("12", "1 2") is False


def test_rotation_constant():
    assert _ROTATION_90 == 900


def test_classify_run_kinds():
    assert classify_run("12")[0] == "digits"
    assert classify_run("AB")[0] == "latin"
    assert classify_run("3.5")[0] == "numeric"
    assert classify_run("令和")[0] == "japanese"


def test_resolve_vertical_trusts_page_over_stale_lr_tb():
    """False-alert case: paragraph reports LR_TB while page is TB_RL."""
    assert resolve_is_vertical(_WM_LR_TB, _WM_TB_RL) is True
    assert resolve_is_vertical(_WM_PAGE, _WM_TB_RL) is True
    assert resolve_is_vertical(_WM_CONTEXT, _WM_TB_RL) is True
    assert resolve_is_vertical(_WM_TB_RL, _WM_LR_TB) is True
    assert resolve_is_vertical(_WM_LR_TB, _WM_LR_TB) is False
    assert resolve_is_vertical(None, _WM_TB_RL) is True
    assert resolve_is_vertical(_WM_LR_TB, None) is False


def test_alnum_pairs_are_recommended():
    from tatechuyoko import classify_selection, find_recommended_run_at_caret

    for run in ("A4", "5G", "H2"):
        assert classify_selection(run)["verdict"] == "ok", run
    assert classify_selection("A4B")["verdict"] == "confirm"
    assert classify_selection("A4B5C")["verdict"] == "refuse"
    # caret detection picks up a letter/digit pair but not a slice of a longer run
    assert find_recommended_run_at_caret("用紙A4判", 3) == (2, 4)
    assert find_recommended_run_at_caret("西暦2026年", 4) is None


def main():
    test_grapheme_len_basic()
    test_classify_recommended()
    test_classify_extended()
    test_classify_inappropriate()
    test_classify_length_edges()
    test_explicit_selection_not_shrunk()
    test_caret_finds_two_digits()
    test_caret_before_digits()
    test_caret_in_japanese_no_match()
    test_caret_inside_long_number_no_slice()
    test_caret_latin_pair()
    test_expand_span_indices()
    test_base_preserved()
    test_rotation_constant()
    test_classify_run_kinds()
    test_alnum_pairs_are_recommended()
    test_resolve_vertical_trusts_page_over_stale_lr_tb()
    print("All tate-chū-yoko helper tests passed.")


if __name__ == "__main__":
    main()
