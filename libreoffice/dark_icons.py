#!/usr/bin/env python3
"""Recolor toolbar SVGs for dark toolbars.

Usage: dark_icons.py SRC_DIR DST_DIR   (DST_DIR may equal SRC_DIR)
"""
import sys
from pathlib import Path

# Light-toolbar foregrounds -> dark-toolbar foregrounds.
PALETTE = (
    ("#48484a", "#f2f2f7"),
    ("#005fef", "#75adff"),
    ("#005ced", "#75adff"),
    ("#0040dd", "#75adff"),
    ("#203758", "#f2f2f7"),
    ("#203859", "#f2f2f7"),
)


def darken(text):
    for old, new in PALETTE:
        text = text.replace(old, new)
    return text


def main(src, dst):
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for path in sorted(src.glob("*.svg")):
        text = darken(path.read_text(encoding="utf-8"))
        (dst / path.name).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
