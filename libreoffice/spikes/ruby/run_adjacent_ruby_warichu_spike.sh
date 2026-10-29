#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LO_USER="${HOME}/Library/Application Support/LibreOffice/4/user/Scripts/python"
mkdir -p "${LO_USER}"
cp "${ROOT}/adjacent_ruby_warichu_spike.py" "${LO_USER}/"

osascript -e 'tell application "LibreOffice" to quit' 2>/dev/null || true
killall -9 soffice soffice.bin 2>/dev/null || true
sleep 2

OUT="${ROOT}/artifacts/adjacent_ruby_warichu"
rm -f "${OUT}/adjacent_report.json"
mkdir -p "${OUT}"

open -a LibreOffice --args --norestore --nofirststartwizard \
  'vnd.sun.star.script:adjacent_ruby_warichu_spike.py$run_adjacent_ruby_warichu_spike?language=Python&location=user'

echo "Waiting…"
for i in $(seq 1 60); do
  if [[ -f "${OUT}/adjacent_report.json" ]]; then
    age=$(( $(date +%s) - $(stat -f %m "${OUT}/adjacent_report.json") ))
    if [[ "${age}" -lt 90 ]]; then
      SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"
      "${SOFFICE}" --headless --norestore --convert-to pdf --outdir "${OUT}" \
        "${OUT}/adjacent_horizontal.odt" "${OUT}/adjacent_vertical.odt" 2>&1 | tail -5
      python3 - <<'PY'
import json
from pathlib import Path
import fitz
p=Path('/Users/daniel/Code/marinaMoji/plugin/libreoffice/spikes/ruby/artifacts/adjacent_ruby_warichu')
d=json.loads((p/'adjacent_report.json').read_text())
print('ok', d.get('ok'))
for w in ('horizontal','vertical'):
    s=d.get(w) or {}
    odf=s.get('odf') or {}
    print(w, 'combine', odf.get('combine_lines'), 'empty_ruby', odf.get('empty_ruby'), 'ruby_mon', odf.get('ruby_mon'))
    for para in (odf.get('paras') or [])[:4]:
        print(' ', para[:180])
    for c in s.get('cases') or []:
        print(' ', c.get('label'), {k:c[k] for k in c if k!='label'})
for pdf in p.glob('adjacent_*.pdf'):
    doc=fitz.open(pdf)
    doc[0].get_pixmap(matrix=fitz.Matrix(2,2)).save(str(pdf)+'.png')
    doc.close()
    print('png', pdf.name)
PY
      exit 0
    fi
  fi
  sleep 1
done
echo timed out
exit 1
