#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if [[ "$(uname -s)" == "Darwin" ]]; then
  LO_USER="${HOME}/Library/Application Support/LibreOffice/4/user/Scripts/python"
else
  LO_USER="${HOME}/.config/libreoffice/4/user/Scripts/python"
fi
mkdir -p "${LO_USER}"
cp "${ROOT}/warichu_stage_b_corpus.py" "${LO_USER}/"
cp "${ROOT}/fixtures_stage_b.json" "${LO_USER}/" 2>/dev/null || true
# Also keep fixtures next to preferred artifact path (macro loads from Code path)
echo "Installed ${LO_USER}/warichu_stage_b_corpus.py"

osascript -e 'tell application "LibreOffice" to quit' 2>/dev/null || true
killall -9 soffice soffice.bin 2>/dev/null || true
sleep 2

OUT="${ROOT}/artifacts/stage_b"
rm -f "${OUT}/stage_b_report.json"
mkdir -p "${OUT}"

open -a LibreOffice --args --norestore --nofirststartwizard \
  'vnd.sun.star.script:warichu_stage_b_corpus.py$run_stage_b_corpus?language=Python&location=user'

echo "Waiting for ${OUT}/stage_b_report.json …"
for i in $(seq 1 90); do
  if [[ -f "${OUT}/stage_b_report.json" ]]; then
    age=$(( $(date +%s) - $(stat -f %m "${OUT}/stage_b_report.json") ))
    if [[ "${age}" -lt 120 ]] || [[ "${i}" -ge 8 ]]; then
      echo "Ready:"
      ls -la "${OUT}"
      python3 - <<'PY'
import json
from pathlib import Path
p=Path("/Users/daniel/Code/marinaMoji/plugin/libreoffice/spikes/warichu/artifacts/stage_b/stage_b_report.json")
d=json.loads(p.read_text())
print("LO:", d.get("lo_version"))
print("font:", d.get("font_selected"))
for w in ("horizontal","vertical"):
    s=d.get(w) or {}
    print(w, "cases", len(s.get("cases") or []), "odt", (s.get("save_odt") or {}).get("ok"),
          "pdf", (s.get("save_pdf") or {}).get("ok"), "docx", (s.get("save_docx") or {}).get("ok"))
    odf=s.get("odf") or {}
    print(" ", "bare", odf.get("bare_combine_styles"), "bracket", odf.get("bracket_combine_styles"))
print("integrity:", d.get("integrity_spotcheck"))
PY
      [[ -f "${OUT}/SUMMARY.md" ]] && cat "${OUT}/SUMMARY.md"
      exit 0
    fi
  fi
  sleep 1
done
echo "Timed out waiting for artifacts. Check LibreOffice window / Desktop/warichu_stage_b_artifacts"
exit 1
