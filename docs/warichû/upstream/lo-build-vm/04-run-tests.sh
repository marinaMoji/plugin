#!/usr/bin/env bash
# Run Writer-related checks after a U1 patch. Expand once a Cppunit/UITest exists.
set -euo pipefail

LO_SRC="${LO_SRC:-${HOME}/lo/core}"
cd "${LO_SRC}"

echo "No marinaMoji-specific Cppunit is checked in yet."
echo "Until then, manual regression:"
echo "  1. ./05-run-instdir.sh"
echo "  2. Open u1_text_combine_brackets_collapse.odt"
echo "  3. Confirm CONTROL readable; FAIL-with-brackets fixed"
echo "  4. Export PDF and compare"
echo ""
echo "Optional LO make check targets (examples — enable as appropriate):"
echo "  make check                    # very heavy"
echo "  make -C sw check              # if configured"
echo "  make Screenshot_*             # where available"
echo ""
echo "When adding a regression test, prefer a small UITest or layout dump"
echo "that opens the U1 ODT and asserts multiportion width / no overlap."
