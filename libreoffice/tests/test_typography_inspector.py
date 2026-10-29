#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for Stage E2 typography analysis (no LibreOffice required)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "marinamoji_kaeriten"))

from typography_analysis import (  # noqa: E402
    RULE_EXPLICIT_BREAK_BEFORE_NOTSTART,
    RULE_PARA_FORBIDDEN_OFF,
    RULE_PUNCTUATION_MIXED_WIDTH,
    DocumentSnapshot,
    InspectionScope,
    ParagraphSnapshot,
    find_soft_break_offsets,
    run_inspection,
)


def _para(**kwargs):
    defaults = dict(
        index=0,
        text="あいうえお。",
        para_is_forbidden_rules=True,
        para_is_hanging_punctuation=True,
        para_is_character_distance=True,
        lang_asian="ja-JP",
    )
    defaults.update(kwargs)
    text = defaults["text"]
    if "soft_break_offsets" not in kwargs:
        defaults["soft_break_offsets"] = find_soft_break_offsets(text)
    if "body_text" not in kwargs:
        defaults["body_text"] = text
    return ParagraphSnapshot(**defaults)


def _run(paragraphs, document=None):
    scope = InspectionScope(
        selection_kind="caret_paragraph",
        paragraphs=list(paragraphs),
        document=document or DocumentSnapshot(),
    )
    return run_inspection(scope)


def test_forbidden_rules_off_informational():
    report = _run([_para(para_is_forbidden_rules=False)])
    ids = [d.rule_id for d in report.diagnostics]
    assert RULE_PARA_FORBIDDEN_OFF in ids
    diag = next(d for d in report.diagnostics if d.rule_id == RULE_PARA_FORBIDDEN_OFF)
    assert diag.severity == "information"


def test_forbidden_rules_on_no_finding():
    report = _run([_para(para_is_forbidden_rules=True)])
    assert RULE_PARA_FORBIDDEN_OFF not in [d.rule_id for d in report.diagnostics]


def test_forbidden_unavailable_no_false_disabled():
    report = _run([_para(para_is_forbidden_rules=None)])
    assert RULE_PARA_FORBIDDEN_OFF not in [d.rule_id for d in report.diagnostics]
    setting = next(s for s in report.settings if s.key == "kinsoku_rules")
    assert setting.display == "unavailable"


def test_mixed_width_lists_each_occurrence():
    # Halfwidth JP stop + Western stops in Japanese prose → one finding each
    text = "第一｡第二.第三.終わり。"
    report = _run([_para(text=text)])
    punct = [d for d in report.diagnostics if d.rule_id == RULE_PUNCTUATION_MIXED_WIDTH]
    assert len(punct) >= 3  # ｡ . .
    variants = {d.message_parameters.get("variant") for d in punct}
    assert "halfwidth_jp" in variants
    assert "western" in variants
    assert any("Halfwidth Japanese full stop" in d.evidence for d in punct)
    assert any("Western full stop" in d.evidence for d in punct)


def test_ascii_punct_in_latin_quote_suppressed():
    # Mostly Latin with ASCII period — should not fire mixed-width as JP issue
    text = 'He said "ok." Then 彼は続けた。'
    report = _run([_para(text=text, lang_asian="en-US")])
    # Low CJK ratio / non-ja locale → no mixed width
    assert RULE_PUNCTUATION_MIXED_WIDTH not in [d.rule_id for d in report.diagnostics]


def test_url_false_positive_suppressed():
    text = "詳細は https://example.com/path.html を見よ。また、注記。"
    report = _run([_para(text=text)])
    # May still flag nothing for '.' inside URL when urlish; ensure no flood
    western = [
        d
        for d in report.diagnostics
        if d.rule_id == RULE_PUNCTUATION_MIXED_WIDTH
        and d.message_parameters.get("char") == "."
    ]
    assert western == []


def test_explicit_break_before_notstart():
    text = "これは行末。\n、続きの文である。"
    report = _run([_para(text=text)])
    assert RULE_EXPLICIT_BREAK_BEFORE_NOTSTART in [d.rule_id for d in report.diagnostics]


def test_explicit_break_before_allowed_char():
    text = "これは行末。\n続きの文である。"
    report = _run([_para(text=text)])
    assert RULE_EXPLICIT_BREAK_BEFORE_NOTSTART not in [
        d.rule_id for d in report.diagnostics
    ]


def test_paragraph_boundary_not_soft_break():
    # Two paragraphs analyzed separately: leading 、 on para 2 is NOT an explicit break finding
    p0 = _para(index=0, text="第一段落。")
    p1 = _para(index=1, text="、第二段落は意図的な行頭かもしれない。")
    report = _run([p0, p1])
    assert RULE_EXPLICIT_BREAK_BEFORE_NOTSTART not in [
        d.rule_id for d in report.diagnostics
    ]


def test_soft_break_offsets_detection():
    assert find_soft_break_offsets("a\nb") == (1,)
    assert find_soft_break_offsets("ab") == ()


def test_settings_mixed_across_paragraphs():
    report = _run(
        [
            _para(index=0, para_is_forbidden_rules=True),
            _para(index=1, text="別の段落。", para_is_forbidden_rules=False),
        ]
    )
    setting = next(s for s in report.settings if s.key == "kinsoku_rules")
    assert setting.display == "mixed"


def test_compression_labels():
    for code, label in ((0, "none"), (1, "punctuation_only"), (2, "punctuation_and_kana")):
        report = _run(
            [_para()],
            document=DocumentSnapshot(character_compression_type=code),
        )
        setting = next(s for s in report.settings if s.key == "punctuation_compression")
        assert setting.display == label


def test_non_japanese_skips_forbidden_off():
    report = _run(
        [
            _para(
                text="Hello world.",
                lang_asian="en-US",
                para_is_forbidden_rules=False,
            )
        ]
    )
    assert RULE_PARA_FORBIDDEN_OFF not in [d.rule_id for d in report.diagnostics]


def test_deterministic_ordering():
    text = "彼は言った｡\n、そして（注）もある。"
    report = _run([_para(text=text, para_is_forbidden_rules=False)])
    ids = [d.rule_id for d in report.diagnostics]
    # forbidden off before mixed / explicit when all present
    if RULE_PARA_FORBIDDEN_OFF in ids and RULE_PUNCTUATION_MIXED_WIDTH in ids:
        assert ids.index(RULE_PARA_FORBIDDEN_OFF) < ids.index(RULE_PUNCTUATION_MIXED_WIDTH)


def test_variation_selector_not_normalized():
    # Ideographic full stop + VS should still be recognizable as not-start head
    text = "終わり。\n、次"
    report = _run([_para(text=text)])
    assert RULE_EXPLICIT_BREAK_BEFORE_NOTSTART in [d.rule_id for d in report.diagnostics]


if __name__ == "__main__":
    # Simple runner without pytest
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
    print("all passed")
