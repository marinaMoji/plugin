#!/usr/bin/env python3
# Stage E1 Prototype B — textual punctuation diagnostics (no layout, no writes).
"""Scan a string for mixed-width Japanese punctuation and explicit-break issues."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Iterable, List

# Fullwidth vs halfwidth pairs commonly mixed in JP scholarly typing
FULL_HALF = {
    "、": "､",
    "。": "｡",
    "「": "｢",
    "」": "｣",
    "（": "(",
    "）": ")",
    "［": "[",
    "］": "]",
    "｛": "{",
    "｝": "}",
    "・": "･",
}

# Subset of LO ja_JP ForbiddenLineBeginCharacters (Japanese-relevant)
DEFAULT_NOT_START = set("、。々〉》」』】〕ぁぃぅぇぉっゃゅょゎ゛゜ゝゞァィゥェォッャュョヮヵヶ・ーヽヾ｡｣､･")
DEFAULT_NOT_END = set("〈《「『【〔｢（［｛")


@dataclass
class Finding:
    rule_id: str
    severity: str
    message: str
    start: int
    end: int
    evidence: str
    confidence: str = "confirmed"


def find_mixed_width(text: str) -> List[Finding]:
    findings = []
    # Pairwise: same role present in both widths
    for full, half in FULL_HALF.items():
        if full in text and half in text:
            findings.append(
                Finding(
                    rule_id="PUNCTUATION_MIXED_WIDTH",
                    severity="advisory",
                    message="Passage mixes full-width and half-width forms of related punctuation.",
                    start=0,
                    end=len(text),
                    evidence=f"{full!r} and {half!r}",
                    confidence="confirmed",
                )
            )
    # Cross-pair: any fullwidth JP punct + any halfwidth JP punct (common scholarly mix)
    half_set = set(FULL_HALF.values())
    full_set = set(FULL_HALF.keys())
    if any(ch in text for ch in full_set) and any(ch in text for ch in half_set):
        if not findings:
            findings.append(
                Finding(
                    rule_id="PUNCTUATION_MIXED_WIDTH",
                    severity="advisory",
                    message="Passage mixes full-width and half-width Japanese punctuation styles.",
                    start=0,
                    end=len(text),
                    evidence="fullwidth+halfwidth punct both present",
                    confidence="confirmed",
                )
            )
    seen = set()
    out = []
    for f in findings:
        if f.evidence in seen:
            continue
        seen.add(f.evidence)
        out.append(f)
    return out


_EXPLICIT_BREAK = re.compile(r"[\n\u000b\u2028\u2029]")  # LF, VT, line/para sep


def find_explicit_break_before_not_start(
    text: str, not_start: Iterable[str] = DEFAULT_NOT_START
) -> List[Finding]:
    forbidden = set(not_start)
    findings = []
    for m in _EXPLICIT_BREAK.finditer(text):
        i = m.end()
        if i < len(text) and text[i] in forbidden:
            findings.append(
                Finding(
                    rule_id="EXPLICIT_BREAK_BEFORE_NOTSTART",
                    severity="advisory",
                    message="An explicit break is followed by a conventional not-start character.",
                    start=m.start(),
                    end=i + 1,
                    evidence=repr(text[m.start() : i + 1]),
                    confidence="confirmed",
                )
            )
    return findings


def find_not_end_before_explicit_break(
    text: str, not_end: Iterable[str] = DEFAULT_NOT_END
) -> List[Finding]:
    forbidden = set(not_end)
    findings = []
    for m in _EXPLICIT_BREAK.finditer(text):
        if m.start() == 0:
            continue
        ch = text[m.start() - 1]
        if ch in forbidden:
            findings.append(
                Finding(
                    rule_id="EXPLICIT_BREAK_AFTER_NOTEND",
                    severity="advisory",
                    message="An explicit break follows a conventional not-end character.",
                    start=m.start() - 1,
                    end=m.end(),
                    evidence=repr(text[m.start() - 1 : m.end()]),
                    confidence="confirmed",
                )
            )
    return findings


def analyze(text: str) -> List[dict]:
    findings = []
    findings.extend(find_mixed_width(text))
    findings.extend(find_explicit_break_before_not_start(text))
    findings.extend(find_not_end_before_explicit_break(text))
    return [asdict(f) for f in findings]


def _self_test():
    samples = [
        "これは「テスト｣です。",  # mixed 「 and ｣
        "行末。\n、行頭",  # explicit break before 、
        "始め「\n続き",  # break after 「
    ]
    for s in samples:
        print("---", repr(s))
        for f in analyze(s):
            print(f)


if __name__ == "__main__":
    _self_test()
