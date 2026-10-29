#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offline JLREQ-oriented division heuristics for Stage B.

This does NOT claim LibreOffice's actual split. It scores candidate mid-breaks
for comparison after visual inspection of Writer output.

Not-start (kinsoku-ish): closing punct, small kana, prolonged sound, etc.
Not-end: opening brackets / quotes (simplified).
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

# Simplified sets — not a full JLREQ class table
NOT_START = set("、。，．・！？‥…ーァィゥェォッャュョヮヵヶぁぃぅぇぉっゃゅょゎ゛゜」』）］｝〉》】〕〗〙〛〉")
NOT_END = set("「『（［｛〈《【〔〖〘〚〈")


def candidates(note: str):
    n = len(note)
    if n < 2:
        return []
    # Prefer breaks near midpoint by character count (glyph advance unknown offline)
    mid = n // 2
    out = []
    for i in range(1, n):
        upper, lower = note[:i], note[i:]
        score = abs(i - mid)  # lower better
        flags = []
        if lower and lower[0] in NOT_START:
            score += 10
            flags.append("lower_starts_kinsoku")
        if upper and upper[-1] in NOT_END:
            score += 10
            flags.append("upper_ends_open")
        # Prefer second line not longer (JLREQ conventional)
        if len(lower) > len(upper):
            score += 3
            flags.append("lower_longer")
        out.append(
            {
                "index": i,
                "upper": upper,
                "lower": lower,
                "score": score,
                "flags": flags,
            }
        )
    out.sort(key=lambda x: (x["score"], x["index"]))
    return out


def main():
    root = Path(__file__).resolve().parent
    fixtures = json.loads((root / "fixtures_stage_b.json").read_text(encoding="utf-8"))
    rows = []
    for case in fixtures["cases"]:
        note = case["note"]
        # NFC for display only — also record NFD length if different
        nfc = unicodedata.normalize("NFC", note)
        cands = candidates(note)
        best = cands[0] if cands else None
        mid_i = len(note) // 2
        mid = {
            "index": mid_i,
            "upper": note[:mid_i],
            "lower": note[mid_i:],
        }
        rows.append(
            {
                "id": case["id"],
                "note": note,
                "len": len(note),
                "nfc_same": nfc == note,
                "codepoints": ["U+%04X" % ord(ch) for ch in note],
                "naive_midpoint": mid,
                "preferred_heuristic": best,
                "midpoint_flags": [
                    f
                    for f in (
                        ["lower_starts_kinsoku"]
                        if mid["lower"] and mid["lower"][0] in NOT_START
                        else []
                    )
                    + (
                        ["upper_ends_open"]
                        if mid["upper"] and mid["upper"][-1] in NOT_END
                        else []
                    )
                    + (["lower_longer"] if len(mid["lower"]) > len(mid["upper"]) else [])
                ],
            }
        )

    out_dir = root / "artifacts" / "stage_b"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "division_heuristics.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Division heuristics (offline — not Writer output)",
        "",
        "Compare these preferred breaks to **observed** Writer splits after viewing the corpus ODT/PDF.",
        "",
        "| Case | Note | Naive mid | Mid flags | Preferred | Pref flags |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        mid = r["naive_midpoint"]
        best = r["preferred_heuristic"] or {}
        md.append(
            "| {id} | `{note}` | `{u}` / `{l}` | {mf} | `{pu}` / `{pl}` | {pf} |".format(
                id=r["id"],
                note=r["note"],
                u=mid["upper"],
                l=mid["lower"],
                mf=",".join(r["midpoint_flags"]) or "—",
                pu=best.get("upper", ""),
                pl=best.get("lower", ""),
                pf=",".join(best.get("flags") or []) or "—",
            )
        )
    (out_dir / "division_heuristics.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("Wrote", out)
    print("Wrote", out_dir / "division_heuristics.md")


if __name__ == "__main__":
    main()
