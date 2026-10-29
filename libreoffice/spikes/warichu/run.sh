#!/usr/bin/env bash
# Install the spike as a LibreOffice user macro and run it inside soffice.
# (LibreOfficePython launched as a Cursor/Terminal child is killed by macOS
# codesign launch constraints on this machine — macros run in-process instead.)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
"${ROOT}/install_user_macro.sh"

echo "Launching LibreOffice with warichū spike macro…"
open -a LibreOffice --args --norestore --nofirststartwizard \
  'vnd.sun.star.script:warichu_spike_macro.py$run_spike?language=Python&location=user'

echo "Waiting for artifacts…"
for i in $(seq 1 30); do
  if [[ -f "${ROOT}/artifacts/spike_report.json" ]]; then
    # Prefer a fresh report (mtime within last 60s)
    if [[ "$(find "${ROOT}/artifacts/spike_report.json" -mtime -60s 2>/dev/null | wc -l | tr -d ' ')" != "0" ]] \
      || [[ $i -ge 3 ]]; then
      echo "Artifacts ready:"
      ls -la "${ROOT}/artifacts"
      echo ""
      echo "Open capability_matrix.md and the ODT (left open in Writer) for T04/T07 visual checks."
      exit 0
    fi
  fi
  sleep 1
done
echo "Timed out waiting for artifacts. If Writer showed an error dialog, check Tools → Macros."
exit 1
