#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LO_USER="${HOME}/Library/Application Support/LibreOffice/4/user/Scripts/python"
mkdir -p "${LO_USER}"
cp "${ROOT}/ruby_align_spike.py" "${LO_USER}/"

osascript -e 'tell application "LibreOffice" to quit' 2>/dev/null || true
killall -9 soffice soffice.bin 2>/dev/null || true
sleep 2

OUT="${ROOT}/artifacts/align_spike"
rm -f "${OUT}/ruby_align_report.json"
mkdir -p "${OUT}"

open -a LibreOffice --args --norestore --nofirststartwizard \
  'vnd.sun.star.script:ruby_align_spike.py$run_ruby_align_spike?language=Python&location=user'

echo "Waiting for report…"
for i in $(seq 1 60); do
  if [[ -f "${OUT}/ruby_align_report.json" ]]; then
    age=$(( $(date +%s) - $(stat -f %m "${OUT}/ruby_align_report.json") ))
    if [[ "${age}" -lt 90 ]] || [[ "${i}" -ge 5 ]]; then
      SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"
      "${SOFFICE}" --headless --norestore --convert-to pdf --outdir "${OUT}" \
        "${OUT}/ruby_align_horizontal.odt" 2>&1 | tail -3
      "${SOFFICE}" --headless --norestore --convert-to pdf --outdir "${OUT}" \
        "${OUT}/ruby_align_vertical.odt" 2>&1 | tail -3
      python3 - <<'PY'
import json
from pathlib import Path
p=Path("/Users/daniel/Code/marinaMoji/plugin/libreoffice/spikes/ruby/artifacts/align_spike/ruby_align_report.json")
d=json.loads(p.read_text())
print("LO", d.get("lo_version"), "font", d.get("font"))
for w in ("horizontal","vertical"):
    s=d.get(w) or {}
    print(w, "cases", len(s.get("cases") or []), "odf_ruby", (s.get("odf") or {}).get("has_text_ruby"),
          "ruby_text_count", (s.get("odf") or {}).get("ruby_text_count"))
    for c in (s.get("cases") or [])[:3]:
        print(" ", c.get("id"), "adjust", c.get("RubyAdjust"), "set_ok", c.get("set_adjust_ok"))
PY
      ls -la "${OUT}"
      exit 0
    fi
  fi
  sleep 1
done
echo "Timed out"
exit 1
