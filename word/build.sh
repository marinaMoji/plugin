#!/usr/bin/env bash
# Build marinaMoji Kaeriten Word add-in into dist/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "${ROOT}"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required. Install Node.js, then run: npm install && ./build.sh"
  exit 1
fi

if [[ ! -d node_modules ]]; then
  npm install
fi

npm run build
npm test
echo "Built ${ROOT}/dist/"
echo "Sideload: npm start  (then Word → Insert → Add-ins → Upload My Add-in → manifest.xml)"
