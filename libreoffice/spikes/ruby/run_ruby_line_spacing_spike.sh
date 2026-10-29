#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LO_USER="${HOME}/Library/Application Support/LibreOffice/4/user/Scripts/python"
mkdir -p "${LO_USER}"
cp "${ROOT}/ruby_line_spacing_spike.py" "${LO_USER}/"

osascript -e 'tell application "LibreOffice" to quit' 2>/dev/null || true
killall -9 soffice soffice.bin 2>/dev/null || true
sleep 2

OUT="${ROOT}/artifacts/line_spacing"
rm -f "${OUT}/line_spacing_report.json"
mkdir -p "${OUT}"

open -a LibreOffice --args --norestore --nofirststartwizard \
  'vnd.sun.star.script:ruby_line_spacing_spike.py$run_ruby_line_spacing_spike?language=Python&location=user'

echo "Waiting for line-spacing report…"
for i in $(seq 1 90); do
  if [[ -f "${OUT}/line_spacing_report.json" ]]; then
    age=$(( $(date +%s) - $(stat -f %m "${OUT}/line_spacing_report.json") ))
    if [[ "${age}" -lt 120 ]]; then
      python3 "${ROOT}/measure_line_spacing.py"
      exit 0
    fi
  fi
  sleep 1
done
echo "Timed out"
exit 1
