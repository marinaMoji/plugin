#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export tests (no LibreOffice required)."""

import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "marinamoji_kaeriten")
sys.path.insert(0, ROOT)

import export_core  # noqa: E402


def test_plain_unchanged():
    text = "說㆒㆑者"
    assert export_core.export_plain_text(text) == text


def test_tei_cluster():
    text = "說㆒㆑者"
    xml = export_core.export_tei_xml(text)
    assert '<kanbun char="說" kaeriten="㆒㆑"/>' in xml
    assert "者" in xml
    assert 'xmlns="http://www.tei-c.org/ns/1.0"' in xml


def test_tei_escapes_xml():
    xml = export_core.export_tei_xml("a & b")
    assert "&amp;" in xml


def test_latex_cluster():
    text = "說㆒㆑者"
    tex = export_core.export_latex(text)
    assert "\\marinamojiKaeriten{㆒㆑}" in tex
    assert "\\begin{document}" in tex


def test_tei_fragment():
    frag = export_core.export_tei_for_clipboard("說㆒㆑者", full_document=False)
    assert frag.startswith("<p ")
    assert "<kanbun" in frag
    assert "<TEI" not in frag


def test_tei_full_document():
    full = export_core.export_tei_for_clipboard("說㆒㆑者", full_document=True)
    assert "<TEI" in full


def test_latex_fragment():
    frag = export_core.export_latex_for_clipboard("說㆒㆑者", full_document=False)
    assert "\\marinamojiKaeriten" in frag
    assert "\\begin{document}" not in frag


def test_latex_full_document():
    full = export_core.export_latex_for_clipboard("說㆒㆑者", full_document=True)
    assert "\\begin{document}" in full


def test_latex_display_comment():
    mapping = {
        "marks": [
            {"char": "㆒", "display_glyph": "一", "stack_order": 0},
            {"char": "㆑", "display_glyph": "レ", "stack_order": 10},
        ]
    }
    tex = export_core.export_latex("說㆒㆑者", mapping)
    assert "Display glyphs" in tex
    assert "一" in tex and "レ" in tex


def main():
    test_plain_unchanged()
    test_tei_cluster()
    test_tei_escapes_xml()
    test_tei_fragment()
    test_tei_full_document()
    test_latex_cluster()
    test_latex_fragment()
    test_latex_full_document()
    test_latex_display_comment()
    print("All export tests passed.")


if __name__ == "__main__":
    main()
