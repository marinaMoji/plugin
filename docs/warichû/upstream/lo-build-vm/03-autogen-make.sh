#!/usr/bin/env bash
# Configure and build LibreOffice. LONG-RUNNING — requires explicit CONFIRM_BUILD=1.
set -euo pipefail

LO_SRC="${LO_SRC:-${HOME}/lo/core}"
JOBS="${JOBS:-$(nproc 2>/dev/null || echo 8)}"

if [[ "${CONFIRM_BUILD:-0}" != "1" ]]; then
  cat <<EOF >&2
Refusing to start a full build without CONFIRM_BUILD=1.

Example (after deps + clone):
  CONFIRM_BUILD=1 JOBS=8 ./03-autogen-make.sh

Expected first build: several hours; disk 150–200 GiB class.
EOF
  exit 2
fi

if [[ ! -d "${LO_SRC}/.git" ]]; then
  echo "Missing ${LO_SRC}. Run 02-clone-core.sh first." >&2
  exit 1
fi

avail_gb=$(df -BG --output=avail "${LO_SRC}" | tail -1 | tr -dc '0-9')
if [[ -n "${avail_gb}" && "${avail_gb}" -lt 80 ]]; then
  echo "ERROR: only ~${avail_gb} GiB free under ${LO_SRC}. Aborting." >&2
  exit 1
fi

cd "${LO_SRC}"
export CCACHE_DIR="${CCACHE_DIR:-${HOME}/.ccache}"
mkdir -p "${CCACHE_DIR}"

# Minimal developer build focused on Writer; adjust per wiki as needed.
./autogen.sh \
  --with-distro=LibreOfficeVanilla \
  --disable-odk \
  --without-junit \
  --enable-python=fully-internal \
  --with-parallelism="${JOBS}"

echo "Starting make -j${JOBS} …"
make -j"${JOBS}"

echo "Build finished. instdir: ${LO_SRC}/instdir"
echo "Next: copy U1 ODT onto the VM, then ./05-run-instdir.sh"
