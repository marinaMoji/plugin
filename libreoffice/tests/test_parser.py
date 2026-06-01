#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parser/mapping tests (no LibreOffice required)."""

import json
import os
import re
from collections import namedtuple

_CLUSTER_RE = re.compile(r"([^\u3190-\u319f\s])([\u3190-\u319f]+)")
KaeritenCluster = namedtuple("KaeritenCluster", ("base_char", "marks", "start", "end"))


def find_clusters(text):
    out = []
    for match in _CLUSTER_RE.finditer(text):
        out.append(KaeritenCluster(match.group(1), match.group(2), match.start(), match.end()))
    return out


def test_compound_cluster():
    text = "說㆒㆑者"
    clusters = find_clusters(text)
    assert len(clusters) == 1
    assert clusters[0].marks == "㆒㆑"
    assert clusters[0].end == 3


def test_mapping_file():
    root = os.path.join(os.path.dirname(__file__), "..", "marinamoji_kaeriten")
    path = os.path.join(root, "mapping.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data.get("marks", [])) >= 2


def main():
    test_compound_cluster()
    test_mapping_file()
    print("All tests passed.")


if __name__ == "__main__":
    main()
