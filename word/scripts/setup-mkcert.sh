#!/usr/bin/env bash
# Create certs/ with the real Homebrew mkcert (NOT npm's unrelated "mkcert" package).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CERTS="${ROOT}/certs"

find_real_mkcert() {
  if [[ -n "${MKCERT_PATH:-}" && -x "${MKCERT_PATH}" ]]; then
    if "${MKCERT_PATH}" -CAROOT >/dev/null 2>&1; then
      echo "${MKCERT_PATH}"
      return 0
    fi
  fi
  for p in /opt/homebrew/bin/mkcert /usr/local/bin/mkcert; do
    if [[ -x "${p}" ]] && "${p}" -CAROOT >/dev/null 2>&1; then
      echo "${p}"
      return 0
    fi
  done
  return 1
}

warn_fake_mkcert_in_path() {
  local w
  w="$(command -v mkcert 2>/dev/null || true)"
  if [[ -n "${w}" && "${w}" == *node_modules* ]]; then
    echo "NOTE: 'which mkcert' → ${w}"
    echo "      That is an npm package, not the real mkcert. Using Homebrew’s binary instead."
    echo ""
  fi
}

MKCERT="$(find_real_mkcert)" || {
  warn_fake_mkcert_in_path
  echo "Real mkcert is not installed."
  echo "  brew install mkcert"
  echo "  /opt/homebrew/bin/mkcert -install"
  echo "  npm run setup:certs"
  exit 1
}

warn_fake_mkcert_in_path

mkdir -p "${CERTS}"

echo "Using: ${MKCERT}"
echo ""
echo "Step 1 — install mkcert’s CA (needs your Mac password in THIS terminal):"
echo "  ${MKCERT} -install"
echo ""
if ! "${MKCERT}" -install; then
  echo ""
  echo "mkcert -install did not complete."
  echo "Run the command above yourself in Terminal.app, then run: npm run setup:certs"
  exit 1
fi

echo ""
echo "Step 2 — create localhost certificate…"
"${MKCERT}" -key-file "${CERTS}/key.pem" -cert-file "${CERTS}/cert.pem" localhost 127.0.0.1 ::1

echo ""
echo "Done. Next:"
echo "  npm run diagnose"
echo "  npm run serve        (must say: HTTPS trusted — OK for Word)"
echo "  npm run doctor"
echo "  npm run reset-word"
echo "  Quit Word (Cmd+Q), reopen Accueil → Kaeriten pane"
