#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure inter-line distances from line-spacing spike PDFs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    print("need pymupdf", file=sys.stderr)
    sys.exit(1)

ART = Path(__file__).resolve().parent / "artifacts" / "line_spacing"
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"


def convert(odt: Path):
    subprocess.run(
        [
            SOFFICE,
            "--headless",
            "--norestore",
            "--convert-to",
            "pdf",
            "--outdir",
            str(odt.parent),
            str(odt),
        ],
        check=False,
        capture_output=True,
    )
    return odt.with_suffix(".pdf")


def line_centres_y(page, needles):
    """Return sorted unique y-centres for lines containing needles."""
    ys = []
    for needle in needles:
        for r in page.search_for(needle):
            ys.append((r.y0 + r.y1) / 2)
    ys = sorted(ys)
    # cluster near-duplicates
    out = []
    for y in ys:
        if not out or abs(y - out[-1]) > 2.0:
            out.append(y)
    return out


def line_centres_x(page, needles):
    """Vertical writing: columns progress in x; within a column, y grows.
    For vertical page, successive *lines* are successive columns (x),
    or successive characters in one column — we want successive paragraphs
    as separate columns or stacked blocks.

    Our spike uses separate paragraphs; in vertical RL_TB they become
    successive columns right-to-left. Measure x centres of paragraph markers.
    """
    xs = []
    for needle in needles:
        for r in page.search_for(needle):
            xs.append((r.x0 + r.x1) / 2)
    xs = sorted(xs, reverse=True)  # RL: first para further right
    out = []
    for x in xs:
        if not out or abs(x - out[-1]) > 2.0:
            out.append(x)
    return out


def gaps(vals):
    return [round(vals[i + 1] - vals[i], 3) for i in range(len(vals) - 1)]


def analyse_pdf(pdf: Path, writing: str):
    doc = fitz.open(pdf)
    page = doc[0]
    # Plain block markers 一/二/三/四 appear in both sections — search longer strings
    plain_needles = ["あいうえお一", "かきくけこ二", "さしすせそ三", "たちつてと四"]
    ruby_needles = ["漢字", "日本", "文字", "試験"]  # may match labels too

    if writing == "horizontal":
        plain_pos = line_centres_y(page, plain_needles)
        # For ruby lines, search unique suffixes 一/二 with 漢字 nearby — use かんじ not in PDF text layer often
        # Body base still in text layer:
        ruby_pos = []
        for ch in ("一", "二", "三", "四"):
            # Prefer hits that are on ruby section: search "漢字一" etc won't work if split
            pass
        for base in ("漢字", "日本", "文字", "試験"):
            rects = page.search_for(base)
            # take first occurrence after mid-page or all and pick 4 largest y after plain
            for r in rects:
                ruby_pos.append((r.y0 + r.y1) / 2)
        ruby_pos = sorted(set(round(y, 1) for y in ruby_pos))
        # filter to those below plain block roughly
        if plain_pos:
            y_cut = plain_pos[-1] + 5
            ruby_pos = [y for y in ruby_pos if y > y_cut][:4]
            # re-expand precision
            ruby_pos2 = []
            for base in ("漢字", "日本", "文字", "試験"):
                for r in page.search_for(base):
                    cy = (r.y0 + r.y1) / 2
                    if cy > y_cut:
                        ruby_pos2.append(cy)
            ruby_pos = []
            for y in sorted(ruby_pos2):
                if not ruby_pos or abs(y - ruby_pos[-1]) > 2:
                    ruby_pos.append(y)
            ruby_pos = ruby_pos[:4]
        axis = "y"
        plain_gaps = gaps(plain_pos)
        ruby_gaps = gaps(ruby_pos)
    else:
        # vertical: paragraphs as columns — measure x of first char of each plain line
        plain_pos = line_centres_x(page, plain_needles)
        ruby_pos = []
        for base in ("漢字", "日本", "文字", "試験"):
            for r in page.search_for(base):
                ruby_pos.append((r.x0 + r.x1) / 2)
        # cluster
        tmp = []
        for x in sorted(ruby_pos, reverse=True):
            if not tmp or abs(x - tmp[-1]) > 2:
                tmp.append(x)
        # take 4 to the left of plain block if needed
        ruby_pos = tmp[:4]
        axis = "x"
        # gaps in reading order (R→L): decreasing x → positive gap = plain_pos[i]-plain_pos[i+1]
        plain_gaps = [
            round(plain_pos[i] - plain_pos[i + 1], 3)
            for i in range(len(plain_pos) - 1)
        ]
        ruby_gaps = [
            round(ruby_pos[i] - ruby_pos[i + 1], 3)
            for i in range(len(ruby_pos) - 1)
        ]

    # Expected fixed pitch in PDF points ≈ FIXED_LINE_PT
    expected = 28.0
    doc.close()
    return {
        "axis": axis,
        "plain_pos": [round(v, 2) for v in plain_pos],
        "ruby_pos": [round(v, 2) for v in ruby_pos],
        "plain_gaps_pt": plain_gaps,
        "ruby_gaps_pt": ruby_gaps,
        "expected_fixed_pt": expected,
        "plain_mean_gap": round(sum(plain_gaps) / len(plain_gaps), 3) if plain_gaps else None,
        "ruby_mean_gap": round(sum(ruby_gaps) / len(ruby_gaps), 3) if ruby_gaps else None,
        "ruby_inflates": (
            None
            if not plain_gaps or not ruby_gaps
            else round(
                (sum(ruby_gaps) / len(ruby_gaps))
                - (sum(plain_gaps) / len(plain_gaps)),
                3,
            )
        ),
    }


def main():
    report_path = ART / "line_spacing_report.json"
    if not report_path.exists():
        print("missing", report_path, file=sys.stderr)
        sys.exit(1)
    spike = json.loads(report_path.read_text(encoding="utf-8"))
    out = {
        "based_on": str(report_path),
        "measurements": [],
        "verdict_notes": [],
    }
    for doc in spike.get("documents") or []:
        odt = Path(doc["odt"])
        pdf = convert(odt)
        if not pdf.exists():
            out["measurements"].append({"tag": doc["tag"], "error": "no pdf"})
            continue
        m = analyse_pdf(pdf, doc["writing"])
        m["tag"] = doc["tag"]
        m["writing"] = doc["writing"]
        m["align_name"] = doc["align_name"]
        # thumbnail
        try:
            d = fitz.open(pdf)
            d[0].get_pixmap(matrix=fitz.Matrix(1.3, 1.3)).save(str(pdf) + ".png")
            d.close()
        except Exception:
            pass
        out["measurements"].append(m)
        print(
            m["tag"],
            "plain_gap",
            m["plain_mean_gap"],
            "ruby_gap",
            m["ruby_mean_gap"],
            "delta",
            m["ruby_inflates"],
        )

    # Summary
    deltas = [
        (m["tag"], m["ruby_inflates"])
        for m in out["measurements"]
        if m.get("ruby_inflates") is not None
    ]
    out["verdict_notes"].append(
        "Positive ruby_inflates ⇒ ruby lines sit farther apart than plain under same fixed spacing."
    )
    out["verdict_notes"].append(
        "Ideal scholarly result: ruby_inflates ≈ 0 (ruby in the gap, pitch unchanged)."
    )
    path = ART / "line_spacing_measurements.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
