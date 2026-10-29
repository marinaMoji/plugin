#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if [[ "$(uname -s)" == "Darwin" ]]; then
  LO_USER="${HOME}/Library/Application Support/LibreOffice/4/user/Scripts/python"
else
  LO_USER="${HOME}/.config/libreoffice/4/user/Scripts/python"
fi
mkdir -p "${LO_USER}"
cp "${ROOT}/warichu_span_spike.py" "${LO_USER}/"
rm -f "${LO_USER%/Scripts/python}/pack/Scripts/python/warichu_span_spike.pack" 2>/dev/null || true
echo "Installed ${LO_USER}/warichu_span_spike.py"

# Prefer a clean LO instance so the macro URL is honored
osascript -e 'tell application "LibreOffice" to quit' 2>/dev/null || true
killall -9 soffice soffice.bin 2>/dev/null || true
sleep 2

OUT="${ROOT}/artifacts/span_spike"
rm -f "${OUT}/span_spike_report.json"
mkdir -p "${OUT}"

open -a LibreOffice --args --norestore --nofirststartwizard \
  'vnd.sun.star.script:warichu_span_spike.py$run_span_spike?language=Python&location=user'

echo "Waiting for ${OUT}/span_spike_report.json …"
for i in $(seq 1 45); do
  if [[ -f "${OUT}/span_spike_report.json" ]]; then
    age=$(( $(date +%s) - $(stat -f %m "${OUT}/span_spike_report.json") ))
    if [[ "${age}" -lt 90 ]] || [[ "${i}" -ge 5 ]]; then
      echo "Ready:"
      ls -la "${OUT}"
      if [[ -f "${OUT}/odf_analysis.json" ]]; then
        echo "--- ODF analysis ---"
        python3 - <<'PY'
import json
from pathlib import Path
p=Path("/Users/daniel/Code/marinaMoji/plugin/libreoffice/spikes/warichu/artifacts/span_spike/odf_analysis.json")
d=json.loads(p.read_text())
print("span_ok:", d.get("span_ok"), "no_para_combine:", d.get("no_para_combine"))
print("text styles:", len(d.get("text_span_combine_styles") or []))
print("para combine styles:", len(d.get("paragraph_combine_styles") or []))
for s in (d.get("body_snippets") or [])[:3]:
    print("BODY:", s[:200])
PY
      fi
      cat "${OUT}/capability_matrix.md"
      exit 0
    fi
  fi
  sleep 1
done
echo "Timed out waiting for artifacts."
exit 1
