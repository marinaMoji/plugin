#!/usr/bin/env bash
# Emit a production Word manifest with your hosted plugin URL (no localhost).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="${ROOT}/word/manifest.production.xml"
OUT="${1:-${ROOT}/packaging/release/marinamoji-kaeriten-word.xml}"

BASE="${MARINAMOJI_PLUGIN_BASE:-}"
if [[ -z "${BASE}" ]]; then
  echo "Set MARINAMOJI_PLUGIN_BASE, e.g.:"
  echo "  export MARINAMOJI_PLUGIN_BASE=https://plugins.example.org/word"
  exit 1
fi
BASE="${BASE%/}"

mkdir -p "$(dirname "${OUT}")"
sed "s|MARINAMOJI_PLUGIN_BASE|${BASE}|g" "${TEMPLATE}" > "${OUT}"
echo "Wrote ${OUT}"
