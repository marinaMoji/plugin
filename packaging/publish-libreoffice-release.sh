#!/usr/bin/env bash
# Upload LibreOffice-only release assets to GitHub (maintainers).
# Requires: gh auth login. Does not touch ONLYOFFICE/Word artifacts.
set -euo pipefail
PACKAGING="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "${PACKAGING}/.." && pwd)"
RELEASE="${PACKAGING}/release-libreoffice"
TAG="${MARINAMOJI_RELEASE_TAG:-}"
REPO="${MARINAMOJI_GITHUB_REPO:-${GITHUB_REPOSITORY:-marinaMoji/plugin}}"

if [[ -z "${TAG}" ]]; then
  LO_VER="$(sed -n 's/.*<version value="\([^"]*\)".*/\1/p' \
    "${PLUGIN}/libreoffice/marinamoji_kaeriten/description.xml" | head -1)"
  TAG="libreoffice-v${LO_VER}"
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: brew install gh && gh auth login"
  exit 1
fi

OXT="${RELEASE}/MarinaMojiKaeriten.oxt"
if [[ ! -f "${OXT}" ]]; then
  echo "Missing ${OXT} — run packaging/build-libreoffice-release.sh first."
  exit 1
fi

NOTES="${RELEASE}/RELEASE_NOTES.md"
LO_VER="$(sed -n 's/.*<version value="\([^"]*\)".*/\1/p' \
  "${PLUGIN}/libreoffice/marinamoji_kaeriten/description.xml" | head -1)"
cat > "${NOTES}" <<EOF
# marinaMoji LibreOffice extension ${LO_VER}

LibreOffice-only release (\`${TAG}\`). Other office hosts are unchanged.

## Downloads

| File | Use |
|------|-----|
| \`MarinaMojiKaeriten.oxt\` | LibreOffice — all platforms |
| \`marinamoji-kaeriten-libreoffice-mac.dmg\` | LibreOffice — Mac GUI installer (when present) |
| \`INSTALL.txt\` | Install steps |
| \`SHA256SUMS.txt\` | Checksums |
| \`MarinaMojiKaeriten.update.xml\` | Review copy of the Extension Manager update feed |

**Identifier:** \`org.marinaMoji.kaeriten\` (do not change).  
**Update feed (after authorization):** https://marinamoji.github.io/plugin/MarinaMojiKaeriten.update.xml

Install the [marinaMoji IME](https://github.com/marinaMoji/marinaMoji) for typing convenience; the extension itself only needs Unicode kaeriten marks in the document.

Maintainer guide: \`plugin/docs/LIBREOFFICE_MARKETPLACE.md\`
EOF

REQUIRED=(
  "${OXT}"
  "${RELEASE}/INSTALL.txt"
  "${RELEASE}/SHA256SUMS.txt"
  "${RELEASE}/VERSION.txt"
  "${RELEASE}/MarinaMojiKaeriten.update.xml"
)
OPTIONAL=(
  "${RELEASE}/marinamoji-kaeriten-libreoffice-mac.dmg"
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
  gh release create "${TAG}" --repo "${REPO}" \
    --title "marinaMoji LibreOffice extension ${LO_VER}" \
    --notes-file "${NOTES}" \
    "${ASSETS[@]}"
fi

echo "Published: https://github.com/${REPO}/releases/tag/${TAG}"
