#!/usr/bin/env bash
# Launch the experimental instdir soffice with an isolated user profile.
# Does not touch the system / distro LibreOffice profile.
set -euo pipefail

LO_SRC="${LO_SRC:-${HOME}/lo/core}"
SOFFICE="${LO_SRC}/instdir/program/soffice"
PROFILE="${LO_USER_PROFILE:-${HOME}/lo-user-profile-u1}"
DOC="${1:-}"

if [[ ! -x "${SOFFICE}" ]]; then
  echo "Missing ${SOFFICE}. Finish ./03-autogen-make.sh first." >&2
  exit 1
fi

mkdir -p "${PROFILE}"
export UserInstallation="file://${PROFILE}"

echo "Using isolated profile: ${PROFILE}"
echo "Binary: ${SOFFICE}"

args=(--norestore --nofirststartwizard)
if [[ -n "${DOC}" ]]; then
  args+=("${DOC}")
fi

exec "${SOFFICE}" "${args[@]}"
