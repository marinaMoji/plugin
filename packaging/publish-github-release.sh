#!/usr/bin/env bash
# Upload packaging/release/* to a GitHub Release (maintainers).
# Requires: brew install gh && gh auth login
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")" && pwd)"
RELEASE="${PACKAGING}/release"
TAG="${MARINAMOJI_RELEASE_TAG:-plugins-v0.3.7}"
REPO="${MARINAMOJI_GITHUB_REPO:-marinaMoji/marinaMozc}"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: brew install gh && gh auth login"
  exit 1
fi

if [[ ! -f "${RELEASE}/MarinaMojiKaeriten.oxt" ]]; then
  echo "Run ./build-release.sh first."
  exit 1
fi

NOTES="${RELEASE}/RELEASE_NOTES.md"
cat > "${NOTES}" <<EOF
# marinaMoji Kaeriten office plugins ${TAG#plugins-v}

**Recommended:** LibreOffice (alpha) — daily driver  
**Experimental:** ONLYOFFICE (alpha)  
**Word:** not included (development paused)

## Downloads

| File | Use |
|------|-----|
| \`MarinaMojiKaeriten.oxt\` | LibreOffice — all platforms |
| \`marinamoji-kaeriten-libreoffice-mac.dmg\` | LibreOffice — Mac GUI installer (no Terminal) |
| \`marinamoji-kaeriten-onlyoffice.zip\` | ONLYOFFICE — manual install |
| \`marinamoji-kaeriten-onlyoffice-mac.dmg\` | ONLYOFFICE — Mac GUI installer |
| \`INSTALL.txt\` | Plain-language install steps |
| \`SHA256SUMS.txt\` | Checksums |

Install the [marinaMoji IME](https://github.com/marinaMoji/marinaMozc) first, then the office plugin for your editor.

See \`plugin/docs/DISTRIBUTION.md\` in the source tree for full documentation.
EOF

if gh release view "${TAG}" --repo "${REPO}" >/dev/null 2>&1; then
  echo "Release ${TAG} exists — uploading assets"
  gh release upload "${TAG}" --repo "${REPO}" --clobber \
    "${RELEASE}/MarinaMojiKaeriten.oxt" \
    "${RELEASE}/marinamoji-kaeriten-libreoffice-mac.dmg" \
    "${RELEASE}/marinamoji-kaeriten-onlyoffice-mac.dmg" \
    "${RELEASE}/marinamoji-kaeriten-onlyoffice.zip" \
    "${RELEASE}/INSTALL.txt" \
    "${RELEASE}/SHA256SUMS.txt" \
    "${RELEASE}/VERSION.txt"
else
  gh release create "${TAG}" --repo "${REPO}" \
    --title "marinaMoji Kaeriten office plugins ${TAG#plugins-v}" \
    --notes-file "${NOTES}" \
    "${RELEASE}/MarinaMojiKaeriten.oxt" \
    "${RELEASE}/marinamoji-kaeriten-libreoffice-mac.dmg" \
    "${RELEASE}/marinamoji-kaeriten-onlyoffice-mac.dmg" \
    "${RELEASE}/marinamoji-kaeriten-onlyoffice.zip" \
    "${RELEASE}/INSTALL.txt" \
    "${RELEASE}/SHA256SUMS.txt" \
    "${RELEASE}/VERSION.txt"
fi

echo "Published: https://github.com/${REPO}/releases/tag/${TAG}"
