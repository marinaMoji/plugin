# -*- coding: utf-8 -*-
"""
Canonical-text exporters for marinaMoji kaeriten (no LibreOffice dependency).
Input is Unicode source text (說㆒㆑者), not rendered frames.
"""

import re
import xml.sax.saxutils as saxutils

_CLUSTER_RE = re.compile(r"([^\u3190-\u319f\s])([\u3190-\u319f]+)")


def find_clusters(text):
    """Return list of (base_char, marks, start, end) for each kaeriten cluster."""
    out = []
    for match in _CLUSTER_RE.finditer(text):
        out.append((match.group(1), match.group(2), match.start(), match.end()))
    return out


def export_plain_text(text):
    return text


def _glyphs_for_marks(marks, by_char):
    chars = list(marks)
    chars.sort(
        key=lambda c: (int(by_char.get(c, {}).get("stack_order", 0)), marks.index(c))
    )
    return "".join(by_char.get(c, {}).get("display_glyph", c) for c in chars)


def export_tei_fragment(text):
    """TEI paragraph snippet for pasting into an existing file."""
    body = _tei_body_content(text)
    if not body:
        return ""
    return '<p xml:lang="ja-Hani">{0}</p>'.format(body)


def export_tei_for_clipboard(text, full_document=False, title="marinaMoji kaeriten export"):
    """Fragment for selection; full TEI document when exporting whole document."""
    if full_document:
        return export_tei_xml(text, title=title)
    return export_tei_fragment(text)


def export_tei_xml(text, title="marinaMoji kaeriten export"):
    """Minimal TEI document with <kanbun char=\"…\" kaeriten=\"…\"/> elements."""
    body = _tei_body_content(text)
    title_esc = saxutils.escape(title)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<TEI xmlns="http://www.tei-c.org/ns/1.0">\n'
        "  <teiHeader>\n"
        "    <fileDesc>\n"
        "      <titleStmt>\n"
        "        <title>{title}</title>\n"
        "      </titleStmt>\n"
        "    </fileDesc>\n"
        "  </teiHeader>\n"
        "  <text>\n"
        "    <body>\n"
        '      <p xml:lang="ja-Hani">{body}</p>\n'
        "    </body>\n"
        "  </text>\n"
        "</TEI>\n"
    ).format(title=title_esc, body=body)


def _tei_body_content(text):
    if not text:
        return ""
    parts = []
    pos = 0
    for base, marks, start, end in find_clusters(text):
        if start > pos:
            parts.append(saxutils.escape(text[pos:start]))
        parts.append(
            '<kanbun char="{base}" kaeriten="{marks}"/>'.format(
                base=saxutils.escape(base),
                marks=saxutils.escape(marks),
            )
        )
        pos = end
    if pos < len(text):
        parts.append(saxutils.escape(text[pos:]))
    return "".join(parts)


def _mapping_by_char(mapping_data):
    by_char = {}
    if mapping_data:
        for entry in mapping_data.get("marks", []):
            ch = entry.get("char")
            if ch:
                by_char[ch] = entry
    return by_char


def export_latex_fragment(text, mapping_data=None):
    """Body-only LaTeX for pasting into an existing xelatex/lualatex file."""
    by_char = _mapping_by_char(mapping_data)
    body = _latex_body(text, by_char)
    lines = [
        "% marinaMoji kaeriten — paste into a document that defines \\marinamojiKaeriten",
        "% \\newcommand{\\marinamojiKaeriten}[1]{{\\small #1}}",
    ]
    if by_char and find_clusters(text):
        lines.append(
            "% Display glyphs: {0}".format(_plain_with_display_glyphs(text, by_char))
        )
    lines.append(body)
    return "\n".join(lines) + "\n"


def export_latex_for_clipboard(text, mapping_data=None, full_document=False):
    """Fragment for selection; full .tex scaffold for whole document."""
    if full_document:
        return export_latex(text, mapping_data=mapping_data)
    return export_latex_fragment(text, mapping_data=mapping_data)


def export_latex(text, mapping_data=None):
    """
    Experimental LaTeX (xelatex/lualatex). Canonical marks in \\marinamojiKaeriten{…};
    comment line lists display glyphs when mapping_data is provided.
    """
    by_char = _mapping_by_char(mapping_data)
    body = _latex_body(text, by_char)
    display_hint = ""
    if by_char and find_clusters(text):
        display_hint = "% Display glyphs: {0}\n".format(
            _plain_with_display_glyphs(text, by_char)
        )

    return (
        "% marinaMoji kaeriten export — compile with xelatex or lualatex\n"
        "\\documentclass{article}\n"
        "\\usepackage{fontspec}\n"
        "\\usepackage{xeCJK}\n"
        "\\newcommand{\\marinamojiKaeriten}[1]{{\\small #1}}\n"
        + display_hint
        + "\\begin{document}\n\n"
        + body
        + "\n\n\\end{document}\n"
    )


def _plain_with_display_glyphs(text, by_char):
    pos = 0
    parts = []
    for base, marks, start, end in find_clusters(text):
        if start > pos:
            parts.append(text[pos:start])
        parts.append(base + _glyphs_for_marks(marks, by_char))
        pos = end
    if pos < len(text):
        parts.append(text[pos:])
    return "".join(parts)


def _latex_body(text, by_char):
    if not text:
        return ""
    parts = []
    pos = 0
    for base, marks, start, end in find_clusters(text):
        if start > pos:
            parts.append(_latex_escape(text[pos:start]))
        parts.append(
            "{base}\\marinamojiKaeriten{{{marks}}}".format(
                base=_latex_escape(base),
                marks=_latex_escape(marks),
            )
        )
        pos = end
    if pos < len(text):
        parts.append(_latex_escape(text[pos:]))
    return "".join(parts)


def _latex_escape(s):
    out = []
    for ch in s:
        if ch in "\\{}#$%&_~^":
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)
