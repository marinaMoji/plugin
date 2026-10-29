#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post-process vertical ruby geometry spike:

1. Font metrics: square-em advance vs ink bbox for 本/文/も/と (Mincho + Gothic).
2. PDF text positions via PyMuPDF (layout positions ≈ character frames / advances).
3. Compare measured centres to JLREQ theoretical frame model.

Does not modify the extension.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Need pymupdf: pip3 install --user pymupdf", file=sys.stderr)
    sys.exit(1)

try:
    from fontTools.ttLib import TTCollection, TTFont
except ImportError:
    print("Need fonttools: pip3 install --user fonttools", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts" / "vertical_geometry"

FONT_FILES = {
    "mincho": "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
    "gothic": "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
}

CHARS = ("本", "文", "も", "と")
BODY_PT = 28.0


def _load_font(path):
    if path.lower().endswith(".ttc"):
        return TTCollection(path).fonts[0]
    return TTFont(path)


def glyph_metrics(font_path, chars=CHARS):
    """Return advance (em) and ink bbox relative to em-square for each char.

    Japanese full-width glyphs typically have advance ≈ unitsPerEm (square frame).
    Ink bbox is the drawn outline — optical, not the layout frame.
    """
    font = _load_font(font_path)
    upem = font["head"].unitsPerEm
    cmap = font.getBestCmap() or {}
    glyf = font["glyf"] if "glyf" in font else None
    hmtx = font["hmtx"].metrics
    # Vertical metrics if present
    vmtx = font["vmtx"].metrics if "vmtx" in font else None

    out = {"font_path": font_path, "unitsPerEm": upem, "glyphs": {}}
    for ch in chars:
        gname = cmap.get(ord(ch))
        if not gname:
            out["glyphs"][ch] = {"error": "missing cmap"}
            continue
        adv_h, lsb = hmtx[gname]
        adv_v = None
        tsb = None
        if vmtx and gname in vmtx:
            adv_v, tsb = vmtx[gname]

        ink = None
        if glyf is not None:
            g = glyf[gname]
            if g.isComposite():
                # Expand composite bounds roughly via fontTools
                try:
                    g.recalcBounds(glyf)
                except Exception:
                    pass
            if hasattr(g, "xMin"):
                ink = {
                    "xMin": g.xMin / upem,
                    "yMin": g.yMin / upem,
                    "xMax": g.xMax / upem,
                    "yMax": g.yMax / upem,
                    "width": (g.xMax - g.xMin) / upem,
                    "height": (g.yMax - g.yMin) / upem,
                    "ink_centre_x": ((g.xMin + g.xMax) / 2) / upem,
                    "ink_centre_y": ((g.yMin + g.yMax) / 2) / upem,
                }

        # Square character frame for full-width CJK: [0,1]×[0,1] in em,
        # with geometric centre (0.5, 0.5) in font design space after
        # mapping. Horizontal advance ≈ 1em.
        frame_centre_x = (adv_h / upem) / 2.0
        frame = {
            "advance_h_em": adv_h / upem,
            "advance_v_em": (adv_v / upem) if adv_v is not None else None,
            "lsb_em": lsb / upem,
            "tsb_em": (tsb / upem) if tsb is not None else None,
            "frame_centre_x_em": frame_centre_x,
            "frame_centre_y_em": 0.5,  # conventional em-box centre
        }
        optical_vs_frame = None
        if ink:
            optical_vs_frame = {
                "dx_ink_minus_frame_x": ink["ink_centre_x"] - frame_centre_x,
                "dy_ink_minus_frame_y": ink["ink_centre_y"] - 0.5,
            }
        out["glyphs"][ch] = {
            "glyph": gname,
            "frame": frame,
            "ink": ink,
            "optical_vs_frame_em": optical_vs_frame,
        }
    return out


def convert_odt_to_pdf(odt: Path):
    soffice = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    subprocess.run(
        [
            soffice,
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


def extract_pdf_chars(pdf_path: Path):
    """Extract per-character positions from PDF (layout boxes ≈ frames)."""
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        # Rawdict gives individual chars with bbox
        raw = page.get_text("rawdict")
        chars = []
        for block in raw.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = span.get("size")
                    font = span.get("font")
                    for ch in span.get("chars", []):
                        c = ch.get("c")
                        bbox = ch.get("bbox")  # x0,y0,x1,y1
                        if not c or not bbox:
                            continue
                        x0, y0, x1, y1 = bbox
                        chars.append(
                            {
                                "c": c,
                                "bbox": [x0, y0, x1, y1],
                                "centre": [(x0 + x1) / 2, (y0 + y1) / 2],
                                "w": x1 - x0,
                                "h": y1 - y0,
                                "size": size,
                                "font": font,
                            }
                        )
        pages.append({"width": page.rect.width, "height": page.rect.height, "chars": chars})
    doc.close()
    return pages


def find_ruby_clusters(chars):
    """Find sequences 本,文 near も,と — vertical PDF: y increases downward.

    Heuristic: locate '本' followed soon by '文' with similar x (same column),
    then find 'も'/'と' with x slightly to the right (smaller x in RL? —
    in PDF coords x increases rightward; vertical Japanese columns run
    right-to-left so ruby on the 'right' of the line is often smaller x
    when the column faces left… measure both).
    """
    clusters = []
    bases = [i for i, ch in enumerate(chars) if ch["c"] == "本"]
    for i in bases:
        # find 文 after 本 in reading order (nearby index or similar x, larger y)
        j = None
        for k in range(i + 1, min(i + 40, len(chars))):
            if chars[k]["c"] == "文":
                j = k
                break
        if j is None:
            continue
        b0, b1 = chars[i], chars[j]
        # ruby candidates near this column
        col_x = (b0["centre"][0] + b1["centre"][0]) / 2
        y0 = min(b0["bbox"][1], b1["bbox"][1])
        y1 = max(b0["bbox"][3], b1["bbox"][3])
        rubies = []
        for ch in chars:
            if ch["c"] not in ("も", "と"):
                continue
            cx, cy = ch["centre"]
            if abs(cx - col_x) > 40:  # points; ruby sits beside column
                # allow either side
                if abs(cx - col_x) > 80:
                    continue
            if cy < y0 - 10 or cy > y1 + 10:
                continue
            rubies.append(ch)
        # dedupe by character keeping closest to column
        by_c = {}
        for r in rubies:
            prev = by_c.get(r["c"])
            if prev is None or abs(r["centre"][0] - col_x) < abs(prev["centre"][0] - col_x):
                by_c[r["c"]] = r
        if "も" in by_c and "と" in by_c:
            clusters.append({"本": b0, "文": b1, "も": by_c["も"], "と": by_c["と"]})
    return clusters


def analyse_cluster(cluster, body_pt=BODY_PT):
    """Compute frame-like centres from PDF bboxes and compare pairing."""
    b_hon = cluster["本"]
    b_bun = cluster["文"]
    r_mo = cluster["も"]
    r_to = cluster["と"]

    # Block axis in vertical writing ≈ PDF y (top→bottom)
    base_top = b_hon["bbox"][1]
    base_bot = b_bun["bbox"][3]
    base_len = base_bot - base_top
    # Prefer measured base cell height from first char
    cell = b_hon["h"] or (base_len / 2)

    def y_centre(ch):
        return ch["centre"][1]

    def x_centre(ch):
        return ch["centre"][0]

    hon_c = y_centre(b_hon)
    bun_c = y_centre(b_bun)
    mo_c = y_centre(r_mo)
    to_c = y_centre(r_to)

    # Normalize to em along block axis: 0 at base top, units of cell height
    def em_y(y):
        return (y - base_top) / cell if cell else None

    # Cross-axis: distance from base column centre to ruby centre (points)
    base_x = (x_centre(b_hon) + x_centre(b_bun)) / 2
    mo_dx = x_centre(r_mo) - base_x
    to_dx = x_centre(r_to) - base_x

    return {
        "pdf_points": {
            "base_top": base_top,
            "base_bot": base_bot,
            "base_len": base_len,
            "cell_h": cell,
            "hon_centre_y": hon_c,
            "bun_centre_y": bun_c,
            "mo_centre_y": mo_c,
            "to_centre_y": to_c,
            "mo_dx_from_base_col": mo_dx,
            "to_dx_from_base_col": to_dx,
            "dx_mo_minus_to": mo_dx - to_dx,
        },
        "frame_em_along_column": {
            "本_centre": em_y(hon_c),
            "文_centre": em_y(bun_c),
            "も_centre": em_y(mo_c),
            "と_centre": em_y(to_c),
            "delta_も_vs_本": em_y(mo_c) - em_y(hon_c) if cell else None,
            "delta_と_vs_文": em_y(to_c) - em_y(bun_c) if cell else None,
        },
        "sizes": {
            "本_wh": [b_hon["w"], b_hon["h"]],
            "文_wh": [b_bun["w"], b_bun["h"]],
            "も_wh": [r_mo["w"], r_mo["h"]],
            "と_wh": [r_to["w"], r_to["h"]],
            "ruby_over_base_h": (r_mo["h"] / b_hon["h"]) if b_hon["h"] else None,
        },
        "interpretation": {
            "cross_axis_note": (
                "dx_mo_minus_to ≠ 0 means も and と sit at different distances "
                "from the base column — often optical side-bearing / ink, while "
                "PDF bbox centres still track layout frames."
            ),
            "block_axis_note": (
                "delta_*_vs_* near 0 ⇒ ruby frame centre matches base frame centre "
                "(INDENT_BLOCK theory for 2×½ on 2×1). "
                "BLOCK theory expects ≈ −0.25em for も vs 本 and ≈ +0.25em for と vs 文."
            ),
        },
    }


def classify_layout(analysis):
    """Guess CENTER / BLOCK / INDENT_BLOCK from measured centre deltas."""
    fe = analysis["frame_em_along_column"]
    d0 = fe.get("delta_も_vs_本")
    d1 = fe.get("delta_と_vs_文")
    if d0 is None or d1 is None:
        return "unknown"
    # Theory:
    # INDENT: ~0, ~0
    # BLOCK:  ~-0.25, ~+0.25
    # CENTER: も centre near 0.75em from top → vs 本(0.5) ≈ +0.25;
    #         と near 1.25 → vs 文(1.5) ≈ -0.25
    if abs(d0) < 0.12 and abs(d1) < 0.12:
        return "matches_INDENT_BLOCK_frames"
    if d0 < -0.12 and d1 > 0.12:
        return "matches_BLOCK_frames"
    if d0 > 0.12 and d1 < -0.12:
        return "matches_CENTER_frames"
    return "ambiguous"


def main():
    ART.mkdir(parents=True, exist_ok=True)
    report_path = ART / "vertical_geometry_report.json"
    if not report_path.exists():
        print("Missing spike report:", report_path, file=sys.stderr)
        print("Run run_ruby_vertical_geometry_spike.sh first.", file=sys.stderr)
        sys.exit(1)

    spike = json.loads(report_path.read_text(encoding="utf-8"))
    out = {
        "based_on": str(report_path),
        "lo_version": spike.get("lo_version"),
        "font_metrics": {},
        "pdf_measurements": [],
        "theory_em": spike.get("theory_em"),
        "verdict_draft": {},
    }

    for key, path in FONT_FILES.items():
        if os.path.exists(path):
            out["font_metrics"][key] = glyph_metrics(path)
        else:
            out["font_metrics"][key] = {"error": "missing %s" % path}

    for doc in spike.get("documents") or []:
        odt = Path(doc["odt"])
        pdf = convert_odt_to_pdf(odt)
        if not pdf.exists():
            out["pdf_measurements"].append({"tag": doc["tag"], "error": "pdf missing"})
            continue
        pages = extract_pdf_chars(pdf)
        page0 = pages[0] if pages else {"chars": []}
        clusters = find_ruby_clusters(page0["chars"])
        measured = []
        for cl in clusters:
            an = analyse_cluster(cl)
            an["layout_guess"] = classify_layout(an)
            measured.append(an)
        # Map by reading order to CENTER, BLOCK, INDENT_BLOCK (insertion order)
        order = ["CENTER", "BLOCK", "INDENT_BLOCK"]
        mapped = []
        for i, name in enumerate(order):
            entry = {"RubyAdjust": name}
            if i < len(measured):
                entry.update(measured[i])
            else:
                entry["error"] = "cluster not found"
            mapped.append(entry)
        # PNG preview
        try:
            doc_pdf = fitz.open(pdf)
            pix = doc_pdf[0].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            png = pdf.with_suffix(".pdf.png")
            pix.save(str(png))
            doc_pdf.close()
            png_path = str(png)
        except Exception as exc:
            png_path = "png failed: %s" % exc

        out["pdf_measurements"].append(
            {
                "tag": doc["tag"],
                "font_key": doc.get("font_key"),
                "font_resolved": doc.get("font_resolved"),
                "grid": doc.get("grid"),
                "pdf": str(pdf),
                "png": png_path,
                "n_chars_extracted": len(page0["chars"]),
                "n_clusters": len(clusters),
                "by_adjust": mapped,
            }
        )

    # Summarise optical vs frame from font metrics
    optical_summary = {}
    for key, metrics in out["font_metrics"].items():
        if "glyphs" not in metrics:
            continue
        optical_summary[key] = {}
        for ch, g in metrics["glyphs"].items():
            ov = g.get("optical_vs_frame_em") or {}
            optical_summary[key][ch] = {
                "advance_h_em": (g.get("frame") or {}).get("advance_h_em"),
                "dx_ink_frame": ov.get("dx_ink_minus_frame_x"),
                "dy_ink_frame": ov.get("dy_ink_minus_frame_y"),
            }
    out["optical_vs_frame_summary"] = optical_summary

    # Verdict helper from measurements
    out["verdict_draft"] = {
        "jlreq_for_本文_もと": (
            "Group-ruby shorter than base: JLREQ permits (1) Fig.124 / JIS 1:2:1 "
            "end spacing ≈ INDENT_BLOCK, and (2) Fig.125 edge-align ≈ BLOCK. "
            "Rules operate on character frames / advances, not glyph ink centres."
        ),
        "theory_2x2_half": {
            "INDENT_BLOCK": "ruby frame centres == base frame centres (Δ≈0)",
            "BLOCK": "も Δ≈−0.25em vs 本; と Δ≈+0.25em vs 文 (edge stretch)",
            "CENTER": "solid ruby; も Δ≈+0.25em; と Δ≈−0.25em",
        },
        "uno_fixable": (
            "Choosing among CENTER/BLOCK/INDENT_BLOCK is UNO-fixable. "
            "Correcting optical ink within frames is NOT exposed via UNO — "
            "that is font design + Writer's use of advances/frames."
        ),
        "do_not_change_default_yet": True,
    }

    out_path = ART / "vertical_geometry_measurements.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", out_path)
    for m in out["pdf_measurements"]:
        print(
            m["tag"],
            "clusters",
            m.get("n_clusters"),
            "→",
            [b.get("layout_guess") or b.get("error") for b in m.get("by_adjust") or []],
        )


if __name__ == "__main__":
    main()
