#!/usr/bin/env bash
# Trust HTTPS for Word on macOS (Safari « unsecured » bypass ≠ Word trust).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

CERT_DIR="${HOME}/.office-addin-dev-certs"
CA="${CERT_DIR}/ca.crt"
LEAF="${CERT_DIR}/localhost.crt"
LOGIN_KC="${HOME}/Library/Keychains/login.keychain-db"

echo "=== marinaMoji Word — certificate setup ==="
echo ""
echo "You do NOT need to click « + » in Keychain or pick « session »."
echo "npm already installed a CA in your « login / Connexion » keychain."
echo ""

npx office-addin-dev-certs install

if [[ ! -f "${CA}" || ! -f "${LEAF}" ]]; then
  echo "Missing files in ${CERT_DIR}"
  exit 1
fi

echo ""
echo "Step A — trust the developer CA (admin password may be required)…"
if sudo npx office-addin-dev-certs install --machine 2>/dev/null; then
  echo "  CA installed for all users (System keychain)."
else
  echo "  (Skipped system install — continuing with login keychain only.)"
fi

echo ""
echo "Step B — add the localhost site certificate to login keychain…"
security add-certificates -k "${LOGIN_KC}" "${LEAF}" 2>/dev/null || true

echo ""
echo "Step C — manual trust (macOS often requires this for Word):"
echo "  1. Keychain Access opens (Trousseau d'accès)."
echo "  2. Select keychain « login » / « Connexion » in the LEFT sidebar (not « session »)."
echo "  3. Search: Developer CA for Microsoft Office Add-ins"
echo "  4. Double-click → Trust / Confiance → « Always Trust » for SSL."
echo "  5. Search: 127.0.0.1 (or localhost) — same « Always Trust » if present."
echo ""
open -a "Keychain Access" "${LOGIN_KC}" 2>/dev/null || open -a "Keychain Access"

echo ""
echo "Step D — Safari test (after trusting):"
echo "  https://localhost:3000/taskpane.html"
echo "  (Should load WITHOUT a red « not secure » warning.)"
echo ""
echo "Step E — reset Word add-in cache and reinstall manifest:"
echo "  ./scripts/reset-word-mac.sh"
echo "  npm run serve"
echo "  Quit Word (Cmd+Q), reopen, Compléments → marinaMoji Kaeriten"
