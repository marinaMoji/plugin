#!/usr/bin/env bash
# Clone LibreOffice core into ~/lo/core (override with LO_SRC).
set -euo pipefail

LO_SRC="${LO_SRC:-${HOME}/lo/core}"
BRANCH="${LO_BRANCH:-libreoffice-26-8}"

mkdir -p "$(dirname "${LO_SRC}")"
if [[ -d "${LO_SRC}/.git" ]]; then
  echo "Already cloned: ${LO_SRC}"
  git -C "${LO_SRC}" fetch --tags --prune
else
  echo "Cloning into ${LO_SRC} (large)…"
  git clone --config core.compression=0 \
    https://git.libreoffice.org/core "${LO_SRC}"
fi

cd "${LO_SRC}"
echo "Checking out branch/tag: ${BRANCH}"
git checkout "${BRANCH}" || {
  echo "Branch ${BRANCH} missing; listing recent tags matching 26.8:" >&2
  git tag -l '*26.8*' | tail -20 >&2
  exit 1
}
echo "HEAD=$(git rev-parse HEAD)"
echo "Next: review README, then ./03-autogen-make.sh when build is approved."
