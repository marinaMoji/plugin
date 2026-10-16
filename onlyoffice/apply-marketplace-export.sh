#!/usr/bin/env bash
# Copy the marketplace export into a local clone of ONLYOFFICE/onlyoffice.github.io.
#
# Usage:
#   ./apply-marketplace-export.sh /path/to/onlyoffice.github.io
#
# Does NOT commit, push, or open a pull request.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "${ROOT}/.." && pwd)"
FOLDER_NAME="marinamoji"

if [[ "${1:-}" == "" ]]; then
  echo "Usage: $0 /path/to/onlyoffice.github.io" >&2
  exit 2
fi

DEST_ROOT="$(cd "$1" && pwd)"
CONTENT="${DEST_ROOT}/sdkjs-plugins/content"
STORE_CONFIG="${DEST_ROOT}/store/config.json"

if [[ ! -d "${CONTENT}" ]]; then
  echo "ERROR: not an onlyoffice.github.io tree (missing sdkjs-plugins/content): ${DEST_ROOT}" >&2
  exit 1
fi
if [[ ! -f "${STORE_CONFIG}" ]]; then
  echo "ERROR: missing store/config.json in ${DEST_ROOT}" >&2
  exit 1
fi

EXPORT_OUT="${MARINAMOJI_MARKETPLACE_OUT:-${PLUGIN}/packaging/release}"
STAGE="${EXPORT_OUT}/marketplace/${FOLDER_NAME}"

if [[ ! -d "${STAGE}" ]]; then
  echo "== No staged export; running export-marketplace.sh"
  chmod +x "${ROOT}/export-marketplace.sh"
  MARINAMOJI_MARKETPLACE_OUT="${EXPORT_OUT}" "${ROOT}/export-marketplace.sh"
fi

if [[ ! -d "${STAGE}" ]]; then
  echo "ERROR: export missing at ${STAGE}" >&2
  exit 1
fi

TARGET="${CONTENT}/${FOLDER_NAME}"
echo "== Install plugin tree → ${TARGET}"
rm -rf "${TARGET}"
mkdir -p "${CONTENT}"
cp -R "${STAGE}" "${TARGET}"

echo "== Ensure store/config.json lists ${FOLDER_NAME}"
python3 - "${STORE_CONFIG}" "${FOLDER_NAME}" <<'PY'
import json, sys
from pathlib import Path

path = Path(sys.argv[1])
name = sys.argv[2]
data = json.loads(path.read_text(encoding="utf-8"))
if not isinstance(data, list):
    raise SystemExit(f"ERROR: {path} is not a JSON array")
names = {item.get("name") for item in data if isinstance(item, dict)}
if name in names:
    print(f"store/config.json already contains {name!r}")
else:
    data.append({"name": name, "discussion": ""})
    path.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
    print(f"Appended {name!r} to store/config.json")
PY

VERSION="$(python3 -c "import json; print(json.load(open('${TARGET}/config.json'))['version'])")"

echo ""
echo "Applied marinaMoji v${VERSION} into local marketplace clone."
echo "Next (only when authorized to submit):"
echo "  cd ${DEST_ROOT}"
echo "  git status"
echo "  git add sdkjs-plugins/content/${FOLDER_NAME} store/config.json"
echo "  git commit -m \"Add ${FOLDER_NAME} plugin (v${VERSION})\""
echo "  git push origin HEAD"
echo "  gh pr create --repo ONLYOFFICE/onlyoffice.github.io --title \"Add ${FOLDER_NAME} plugin (v${VERSION})\""
echo ""
echo "This script did not commit or push."
