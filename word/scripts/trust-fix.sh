#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CA="${HOME}/.office-addin-dev-certs/ca.crt"
LEAF="${HOME}/.office-addin-dev-certs/localhost.crt"
LOGIN_KC="${HOME}/Library/Keychains/login.keychain-db"

if [[ ! -f "${CA}" ]]; then
  (cd "${ROOT}" && npx office-addin-dev-certs install)
fi

echo "This installs the developer CA where Word looks for trust."
echo "You will be asked for your Mac login password."
echo ""
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "${CA}"

security add-trusted-cert -d -r trustRoot -k "${LOGIN_KC}" "${CA}" 2>/dev/null || true
security add-certificates -k "${LOGIN_KC}" "${LEAF}" 2>/dev/null || true

echo ""
echo ""
echo "If npm run serve still says FATAL, use mkcert instead:"
echo "  brew install mkcert"
echo "  npm run setup:certs"
echo "  npm run serve"
echo ""
echo "Then: npm run doctor  |  npm run reset-word  |  restart Word"
