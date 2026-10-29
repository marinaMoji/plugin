#!/usr/bin/env bash
# Copy the spike into the LibreOffice user Scripts folder so it can run as a macro
# inside soffice (avoids launching LibreOfficePython as a Cursor child process).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if [[ "$(uname -s)" == "Darwin" ]]; then
  LO_USER="${HOME}/Library/Application Support/LibreOffice/4/user/Scripts/python"
else
  LO_USER="${HOME}/.config/libreoffice/4/user/Scripts/python"
fi
mkdir -p "${LO_USER}"
cp "${ROOT}/warichu_spike_macro.py" "${LO_USER}/"
cp "${ROOT}/fixtures.json" "${LO_USER}/warichu_spike_fixtures.json"
# Drop stale pack cache if present
rm -f "${LO_USER%/Scripts/python}/pack/Scripts/python/warichu_spike_macro.pack" 2>/dev/null || true
echo "Installed:"
echo "  ${LO_USER}/warichu_spike_macro.py"
echo "  ${LO_USER}/warichu_spike_fixtures.json"
echo ""
echo "Run from GUI: Tools → Macros → Run Macro → My Macros → warichu_spike_macro → run_spike"
echo "Or CLI (after quitting other LO windows):"
echo "  soffice 'vnd.sun.star.script:warichu_spike_macro.py\$run_spike?language=Python&location=user'"
