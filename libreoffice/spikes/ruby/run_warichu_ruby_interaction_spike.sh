#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LO_USER="${HOME}/Library/Application Support/LibreOffice/4/user/Scripts/python"
mkdir -p "${LO_USER}"
cp "${ROOT}/warichu_ruby_interaction_spike.py" "${LO_USER}/"

osascript -e 'tell application "LibreOffice" to quit' 2>/dev/null || true
killall -9 soffice soffice.bin 2>/dev/null || true
sleep 2

OUT="${ROOT}/artifacts/warichu_interaction"
rm -f "${OUT}/warichu_ruby_interaction_report.json"
mkdir -p "${OUT}"

open -a LibreOffice --args --norestore --nofirststartwizard \
  'vnd.sun.star.script:warichu_ruby_interaction_spike.py$run_warichu_ruby_interaction_spike?language=Python&location=user'

echo "Waiting for warichū×ruby interaction report…"
for i in $(seq 1 60); do
  if [[ -f "${OUT}/warichu_ruby_interaction_report.json" ]]; then
    age=$(( $(date +%s) - $(stat -f %m "${OUT}/warichu_ruby_interaction_report.json") ))
    if [[ "${age}" -lt 90 ]]; then
      python3 - <<'PY'
import json
from pathlib import Path
p=Path("/Users/daniel/Code/marinaMoji/plugin/libreoffice/spikes/ruby/artifacts/warichu_interaction/warichu_ruby_interaction_report.json")
d=json.loads(p.read_text())
print("ok", d.get("ok"))
for c in d.get("cases") or []:
    if str(c.get("id","")).startswith("odf_"):
        print(c["id"], "combine_lines", c.get("text_combine_lines"),
              "empty_ruby", c.get("empty_ruby_text"))
    elif c.get("id","").startswith(("A_","B_","C_")):
        print(c.get("id"), {k:c[k] for k in c if k!="id"})
PY
      exit 0
    fi
  fi
  sleep 1
done
echo "Timed out"
exit 1
