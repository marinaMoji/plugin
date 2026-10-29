#!/usr/bin/env bash
# Install LibreOffice core build dependencies on Ubuntu 22.04/24.04.
# Safe to re-run. Does not start a compile.
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This script is for the Ubuntu VM, not macOS." >&2
  exit 1
fi

avail_gb=$(df -BG --output=avail / | tail -1 | tr -dc '0-9')
if [[ -n "${avail_gb}" && "${avail_gb}" -lt 100 ]]; then
  echo "WARNING: only ~${avail_gb} GiB free on /. Aim for 150–200 GiB before building." >&2
fi

export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y \
  git build-essential autoconf automake libtool pkg-config \
  g++ make ccache ninja-build \
  libgirepository1.0-dev libglib2.0-dev \
  python3 python-is-python3 \
  libcups2-dev libfontconfig1-dev libfreetype6-dev \
  libx11-dev libxext-dev libxrender-dev libxt-dev \
  libssl-dev libcurl4-openssl-dev \
  zlib1g-dev libicu-dev libxml2-dev libxslt1-dev \
  libpng-dev libjpeg-dev libtiff-dev \
  bison flex nasm \
  graphviz wget curl unzip xz-utils

# Optional: fuller dep set via TDF helper when network allows
if [[ "${INSTALL_LO_EXTRA_DEPS:-0}" == "1" ]]; then
  echo "Fetching TDF lo_extra_deps list (INSTALL_LO_EXTRA_DEPS=1)…"
  # Maintainers often use:
  #   ./bin/lo_download_external /  or distro packages from the wiki
  echo "See https://wiki.documentfoundation.org/Development/Linux for distro packages."
fi

echo "Dependencies installed. Next: ./02-clone-core.sh"
ccache -s 2>/dev/null || true
