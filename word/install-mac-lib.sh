# Shared by install-mac.sh and install-mac-production.sh (sourced, not run).
#
# macOS (TCC) refuses to let Terminal, even with sudo, write into Word's sandbox
# container: "cp: ... Operation not permitted". Try the copy; if it is refused, stage a
# correctly named copy on the Desktop and open Finder on it and on Word's add-in folder,
# so the user can drag it across (Finder is allowed to). Or grant the terminal app Full
# Disk Access (System Settings → Privacy & Security) and run the script again.

WEF="${HOME}/Library/Containers/com.microsoft.Word/Data/Documents/wef"
MANIFEST_NAME="marinamoji-kaeriten.xml"

# install_manifest SOURCE_FILE — returns 0 if copied, 1 if the user must drag it.
install_manifest() {
  local src="$1"
  if mkdir -p "${WEF}" 2>/dev/null \
     && rm -f "${WEF}/${MANIFEST_NAME}" 2>/dev/null \
     && cp "${src}" "${WEF}/${MANIFEST_NAME}" 2>/dev/null; then
    echo "Installed ${MANIFEST_NAME} in:"
    echo "  ${WEF}"
    return 0
  fi

  local staged="${HOME}/Desktop/${MANIFEST_NAME}"
  cp -f "${src}" "${staged}"
  echo "macOS does not let Terminal write into Word's add-in folder (Operation not permitted)."
  echo "Do this by hand instead (takes a few seconds):"
  echo "  1. Finder now shows ${MANIFEST_NAME} (on your Desktop) and Word's add-in folder."
  echo "     If the 'wef' folder does not exist, create it inside .../com.microsoft.Word/Data/Documents/."
  echo "  2. Drag ${MANIFEST_NAME} into the 'wef' folder. Choose Replace if asked."
  echo "Or give your terminal app Full Disk Access (System Settings → Privacy & Security)"
  echo "and run this script again."
  open -R "${staged}" 2>/dev/null || true
  open "${WEF}" 2>/dev/null || true
  return 1
}
