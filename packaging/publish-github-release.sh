#!/usr/bin/env bash
# Upload packaging/release/* to a GitHub Release (maintainers).
# Requires: brew install gh && gh auth login
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")" && pwd)"
RELEASE="${PACKAGING}/release"
TAG="${MARINAMOJI_RELEASE_TAG:-plugins-v0.0.2}"
# Prefer explicit repo, then Actions GITHUB_REPOSITORY, then the public default.
REPO="${MARINAMOJI_GITHUB_REPO:-${GITHUB_REPOSITORY:-marinaMoji/plugin}}"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: brew install gh && gh auth login"
  exit 1
fi

if [[ ! -f "${RELEASE}/MarinaMojiKaeriten.oxt" ]]; then
  echo "Run ./build-release.sh first (or the Release plugins GitHub Action)."
  exit 1
fi

NOTES="${RELEASE}/RELEASE_NOTES.md"
cat > "${NOTES}" <<EOF
# marinaMoji Kaeriten office plugins ${TAG#plugins-v}

**Recommended:** LibreOffice (alpha) — daily driver  
**Experimental:** ONLYOFFICE (alpha)  
**Word:** included by default (Mac pre-publish QA passed; Windows QA pending)

## Downloads

| File | Use |
|------|-----|
| \`MarinaMojiKaeriten.oxt\` | LibreOffice — all platforms |
| \`marinamoji-kaeriten-libreoffice-mac.dmg\` | LibreOffice — Mac GUI installer (no Terminal) |
| \`marinamoji-kaeriten-onlyoffice.zip\` | ONLYOFFICE — manual install |
| \`marinamoji-kaeriten.plugin\` | ONLYOFFICE — Plugin Manager sideload |
| \`marinamoji-onlyoffice-marketplace.zip\` | ONLYOFFICE — files for marketplace PR (maintainers) |
| \`marinamoji-kaeriten-onlyoffice-mac.dmg\` | ONLYOFFICE — Mac GUI installer |
| \`word-dist.zip\` | Word — hosted add-in files (already live on GitHub Pages) |
| \`marinamoji-kaeriten-word-mac.dmg\` | Word — Mac GUI installer |
| \`marinamoji-kaeriten-word.xml\` | Word — Windows manifest upload |
| \`INSTALL.txt\` | Plain-language install steps |
| \`SHA256SUMS.txt\` | Checksums |

Install the [marinaMoji IME](https://github.com/marinaMoji/marinaMoji) first, then the office plugin for your editor.

See \`plugin/docs/DISTRIBUTION.md\` in the source tree for full documentation.
EOF

REQUIRED=(
  "${RELEASE}/MarinaMojiKaeriten.oxt"
  "${RELEASE}/marinamoji-kaeriten-onlyoffice.zip"
  "${RELEASE}/INSTALL.txt"
  "${RELEASE}/SHA256SUMS.txt"
  "${RELEASE}/VERSION.txt"
)
OPTIONAL=(
  "${RELEASE}/marinamoji-kaeriten-libreoffice-mac.dmg"
  "${RELEASE}/marinamoji-kaeriten-onlyoffice-mac.dmg"
  "${RELEASE}/marinamoji-kaeriten.plugin"
  "${RELEASE}/marinamoji-onlyoffice-marketplace.zip"
  "${RELEASE}/word-dist.zip"
  "${RELEASE}/marinamoji-kaeriten-word-mac.dmg"
  "${RELEASE}/marinamoji-kaeriten-word.xml"
)

ASSETS=()
for f in "${REQUIRED[@]}"; do
  if [[ ! -f "${f}" ]]; then
    echo "Missing required release asset: ${f}"
    exit 1
  fi
  ASSETS+=("${f}")
done
for f in "${OPTIONAL[@]}"; do
  if [[ -f "${f}" ]]; then
    ASSETS+=("${f}")
  else
    echo "Note: optional asset not present (skipped): $(basename "${f}")"
  fi
done

if gh release view "${TAG}" --repo "${REPO}" >/dev/null 2>&1; then
  echo "Release ${TAG} exists — uploading assets"
  gh release upload "${TAG}" --repo "${REPO}" --clobber "${ASSETS[@]}"
else
  # Creates the git tag from the current commit when the tag does not exist yet
  # (useful for workflow_dispatch on main).
  gh release create "${TAG}" --repo "${REPO}" \
    --title "marinaMoji Kaeriten office plugins ${TAG#plugins-v}" \
    --notes-file "${NOTES}" \
    "${ASSETS[@]}"
fi

echo "Published: https://github.com/${REPO}/releases/tag/${TAG}"
