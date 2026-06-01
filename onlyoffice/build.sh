#!/usr/bin/env bash
# Sync shared mapping.json into the plugin folder (icons are copied at release).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cp "${ROOT}/../mapping.json" "${ROOT}/mapping.json"
echo "Updated onlyoffice/mapping.json"
