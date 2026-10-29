# -*- coding: utf-8 -*-
"""
Pure math for jidori approximation (no UNO).

Assumes fullwidth-style advances: each grapheme ≈ 1 em.
Target width = N_cells * em.
Current width = n_graphemes * em  (CJK-oriented approximation).

Expand → CharKerning (extra space per gap).
Shrink → CharScaleWidth (percent).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class JidoriPlan:
    mode: str  # "expand" | "shrink" | "noop" | "invalid"
    target_cells: int
    grapheme_count: int
    scale_width_percent: int  # 100 = unchanged
    # Extra spacing to apply between characters, in the same unit as em_size
    # (caller converts to CharKerning UNO units).
    extra_per_gap_em: float
    note: str


def count_graphemes(text: str) -> int:
    """Approximate grapheme count without unicodedata.normalize changes.

    Uses a simple code-point walk; skips VS (U+FE00–FE0F). Good enough for
    CJK spike strings; not a full GraphemeBreak implementation.
    """
    if not text:
        return 0
    n = 0
    i = 0
    while i < len(text):
        o = ord(text[i])
        # Skip variation selectors
        if 0xFE00 <= o <= 0xFE0F:
            i += 1
            continue
        n += 1
        i += 1
        # Skip following VS attached to this base
        while i < len(text) and 0xFE00 <= ord(text[i]) <= 0xFE0F:
            i += 1
    return n


def plan_jidori(
    text: str, target_cells: int, *, vertical: bool = False
) -> JidoriPlan:
    """Return how to approximate jidori for text into target_cells.

    ``vertical=True``: expand via spacing is allowed; shrink via scale is
    refused (live LO 26.8: Scale width thins glyphs and shoves the run to
    the line head in 縦書き).
    """
    if target_cells < 1:
        return JidoriPlan("invalid", target_cells, 0, 100, 0.0, "target_cells < 1")
    n = count_graphemes(text)
    if n < 1:
        return JidoriPlan("invalid", target_cells, n, 100, 0.0, "empty text")
    if n == target_cells:
        return JidoriPlan("noop", target_cells, n, 100, 0.0, "already N cells")

    # Widths in em under fullwidth assumption
    current = float(n)
    target = float(target_cells)

    if target > current:
        # Expand: distribute extra ems across (n-1) gaps.
        # Single grapheme: JLREQ leaves space after the character; Writer
        # CharKerning has no clean "trailing pad only" model — refuse.
        if n == 1:
            return JidoriPlan(
                "invalid",
                target_cells,
                n,
                100,
                0.0,
                "single grapheme expand unsupported (no inter-character gap)",
            )
        extra_total = target - current
        per_gap = extra_total / float(n - 1)
        return JidoriPlan(
            "expand",
            target_cells,
            n,
            100,
            per_gap,
            "expand gaps via CharKerning",
        )

    # Shrink: scale width down (horizontal only — see vertical gate)
    if vertical:
        return JidoriPlan(
            "invalid",
            target_cells,
            n,
            100,
            0.0,
            "vertical compress unsupported (CharScaleWidth distorts)",
        )
    pct = max(1, int(round(100.0 * target / current)))
    return JidoriPlan(
        "shrink",
        target_cells,
        n,
        pct,
        0.0,
        "compress via CharScaleWidth",
    )


def em_to_char_kerning_twips(extra_per_gap_em: float, em_size_pt: float) -> int:
    """
    Convert extra gap in em to LibreOffice CharKerning (twips).

    Writer maps CharKerning with CONVERT_TWIPS (1 pt = 20 twips).
    Position dialog Spacing in pt ≈ ``extra_per_gap_em * em_size_pt``.

    Live calibration 2026-10-29 (10.5 pt face): ~10 pt Spacing ≈ 1 em/gap
    for 3→5 cells (formula 10.5 pt → 210 twips).
    """
    return int(round(extra_per_gap_em * em_size_pt * 20))


# Back-compat alias for older spike imports / docs.
em_to_char_kerning_hmm = em_to_char_kerning_twips


def plan_to_uno_values(
    plan: JidoriPlan, em_size_pt: float
) -> Tuple[Optional[int], Optional[int]]:
    """Return (CharScaleWidth or None, CharKerning or None) for apply."""
    if plan.mode == "invalid":
        return None, None
    if plan.mode == "noop":
        return 100, 0
    if plan.mode == "expand":
        return 100, em_to_char_kerning_twips(plan.extra_per_gap_em, em_size_pt)
    if plan.mode == "shrink":
        return plan.scale_width_percent, 0
    return None, None
