#!/usr/bin/env bash
# Install + launch the Japanese-font controlled warichū retest macro.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if [[ "$(uname -s)" == "Darwin" ]]; then
  LO_USER="${HOME}/Library/Application Support/LibreOffice/4/user/Scripts/python"
else
  LO_USER="${HOME}/.config/libreoffice/4/user/Scripts/python"
fi
mkdir -p "${LO_USER}"
cp "${ROOT}/warichu_retest_jp.py" "${LO_USER}/"
rm -f "${LO_USER%/Scripts/python}/pack/Scripts/python/warichu_retest_jp.pack" 2>/dev/null || true
echo "Installed ${LO_USER}/warichu_retest_jp.py"
echo "Launching retest…"
open -a LibreOffice --args --norestore --nofirststartwizard \
  'vnd.sun.star.script:warichu_retest_jp.py$run_retest_jp?language=Python&location=user'

OUT="${ROOT}/artifacts/retest_jp"
echo "Waiting for ${OUT}/retest_jp_report.json …"
for i in $(seq 1 40); do
  if [[ -f "${OUT}/retest_jp_report.json" ]]; then
    # Prefer a freshly written file
    age=$(( $(date +%s) - $(stat -f %m "${OUT}/retest_jp_report.json") ))
    if [[ "${age}" -lt 90 ]] || [[ "${i}" -ge 5 ]]; then
      ls -la "${OUT}"
      echo "Done. Compare sections A / B / C in the open Writer document."
      exit 0
    fi
  fi
  sleep 1
done
echo "Timed out — if a dialog appeared, dismiss it and check ${OUT}"
exit 1
