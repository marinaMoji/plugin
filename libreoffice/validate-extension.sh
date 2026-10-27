#!/usr/bin/env bash
# Validate LibreOffice .oxt package structure and marketplace-oriented metadata.
# Does not submit anything. Safe for CI and local pre-release checks.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="${ROOT}/marinamoji_kaeriten"
DIST="${ROOT}/dist"
OXT="${1:-${DIST}/MarinaMojiKaeriten.oxt}"
EXPECTED_ID="org.marinaMoji.kaeriten"
ERR=0

fail() {
  echo "ERROR: $*" >&2
  ERR=1
}

warn() {
  echo "WARNING: $*" >&2
}

need_file() {
  [[ -f "$1" ]] || fail "missing file: $1"
}

echo "Validating LibreOffice extension readiness"
echo "  source: ${SRC}"
echo "  package: ${OXT}"

need_file "${SRC}/description.xml"
need_file "${SRC}/META-INF/manifest.xml"
need_file "${SRC}/Addons.xcu"
need_file "${SRC}/ProtocolHandler.xcu"
need_file "${SRC}/Jobs.xcu"
need_file "${SRC}/composer_handoff.py"
need_file "${SRC}/MarinaMojiKaeriten.components"
need_file "${SRC}/marinamoji_kaeriten_dispatch.py"
need_file "${SRC}/marinamoji_kaeriten.py"
need_file "${SRC}/registration/license_en.txt"
need_file "${SRC}/description/desc_en.txt"
need_file "${SRC}/description/desc_fr.txt"
need_file "${SRC}/description/desc_ja.txt"
need_file "${SRC}/images/extension_icon.png"
need_file "${ROOT}/../pages/MarinaMojiKaeriten.update.xml"

# Build if missing so package checks can run
if [[ ! -f "${OXT}" ]]; then
  echo "No .oxt at ${OXT} — building…"
  chmod +x "${ROOT}/build.sh"
  "${ROOT}/build.sh"
fi
need_file "${OXT}"

python3 - "${SRC}/description.xml" "${ROOT}/../pages/MarinaMojiKaeriten.update.xml" "${OXT}" "${EXPECTED_ID}" <<'PY' || ERR=1
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

desc_path, update_path, oxt_path = map(Path, sys.argv[1:4])
expected_id = sys.argv[4]
errors = []
warnings = []

NS = {
    "d": "http://openoffice.org/extensions/description/2006",
    "u": "http://openoffice.org/extensions/update/2006",
    "lo": "http://libreoffice.org/extensions/description/2011",
    "xlink": "http://www.w3.org/1999/xlink",
}

def need(cond, msg):
    if not cond:
        errors.append(msg)

def warn(msg):
    warnings.append(msg)

# --- description.xml ---
try:
    tree = ET.parse(desc_path)
except ET.ParseError as exc:
    print(f"ERROR: description.xml is not well-formed XML: {exc}", file=sys.stderr)
    sys.exit(1)

root = tree.getroot()
ident = root.find("d:identifier", NS)
version = root.find("d:version", NS)
ident_val = ident.get("value") if ident is not None else None
ver_val = version.get("value") if version is not None else None

need(ident_val == expected_id, f"identifier must be {expected_id!r} (got {ident_val!r})")
need(bool(ver_val) and re.fullmatch(r"\d+\.\d+\.\d+", ver_val or ""), f"version must be x.y.z (got {ver_val!r})")

upd = root.find("d:update-information/d:src", NS)
need(upd is not None, "missing update-information/src")
if upd is not None:
    href = upd.get("{http://www.w3.org/1999/xlink}href") or ""
    need(href.startswith("https://"), f"update-information URL must be https (got {href!r})")
    need("MarinaMojiKaeriten.update.xml" in href, f"unexpected update-information URL: {href!r}")

lic = root.find("d:registration/d:simple-license/d:license-text", NS)
need(lic is not None, "missing registration/simple-license/license-text")
if lic is not None:
    lhref = lic.get("{http://www.w3.org/1999/xlink}href") or ""
    need(lhref.endswith("license_en.txt"), f"license-text href unexpected: {lhref!r}")

icon = root.find("d:icon/d:default", NS)
need(icon is not None, "missing icon/default")
platform = root.find("d:platform", NS)
need(platform is not None and platform.get("value") == "all", "platform should be 'all'")
dep = root.find("d:dependencies/lo:LibreOffice-minimal-version", NS)
need(dep is not None and dep.get("value") == "6.4", "LibreOffice-minimal-version should be 6.4")

names = root.findall("d:display-name/d:name", NS)
need(any((n.text or "").startswith("marinaMoji") for n in names), "display-name should include marinaMoji")
descs = root.findall("d:extension-description/d:src", NS)
langs = {(d.get("lang") or "") for d in descs}
need({"en", "fr", "ja"} <= langs, f"extension-description langs should include en/fr/ja (got {sorted(langs)})")

# --- update feed (checked-in pages copy; release sync may replace it) ---
try:
    utree = ET.parse(update_path)
except ET.ParseError as exc:
    print(f"ERROR: update XML is not well-formed: {exc}", file=sys.stderr)
    sys.exit(1)

uroot = utree.getroot()
uid = uroot.find("u:identifier", NS)
uver = uroot.find("u:version", NS)
udl = uroot.find("u:update-download/u:src", NS)
uid_val = uid.get("value") if uid is not None else None
uver_val = uver.get("value") if uver is not None else None
udl_href = udl.get("{http://www.w3.org/1999/xlink}href") if udl is not None else ""

need(uid_val == expected_id, f"update feed identifier mismatch: {uid_val!r}")
need(bool(udl_href) and udl_href.startswith("https://"), f"update-download must be https (got {udl_href!r})")
need(udl_href.endswith("MarinaMojiKaeriten.oxt") or "/MarinaMojiKaeriten.oxt" in udl_href,
     f"update-download should point at MarinaMojiKaeriten.oxt (got {udl_href!r})")
if "/latest/" in (udl_href or ""):
    warn("update-download uses GitHub /latest/ (prefer a versioned release tag URL for reproducibility)")
if uver_val != ver_val:
    warn(f"pages update feed version {uver_val!r} != description.xml {ver_val!r} "
         "(expected until the next release sync publishes the feed)")

# --- .oxt zip contents ---
required_members = [
    "description.xml",
    "META-INF/manifest.xml",
    "Addons.xcu",
    "ProtocolHandler.xcu",
    "Jobs.xcu",
    "MarinaMojiKaeriten.components",
    "marinamoji_kaeriten_dispatch.py",
    "Scripts/python/marinamoji_kaeriten.py",
    "Scripts/python/marinamoji_mapping.json",
    "Scripts/python/export_core.py",
    "Scripts/python/composer_handoff.py",
    "registration/license_en.txt",
    "description/desc_en.txt",
    "description/desc_fr.txt",
    "description/desc_ja.txt",
    "images/extension_icon.png",
    "icons/render_kaeriten.png",
]
with zipfile.ZipFile(oxt_path) as zf:
    names = set(zf.namelist())
    for member in required_members:
        need(member in names, f".oxt missing {member}")
    # Parse packaged description.xml
    with zf.open("description.xml") as fh:
        pkg_root = ET.parse(fh).getroot()
    pkg_id = pkg_root.find("d:identifier", NS)
    pkg_ver = pkg_root.find("d:version", NS)
    pkg_id_val = pkg_id.get("value") if pkg_id is not None else None
    pkg_ver_val = pkg_ver.get("value") if pkg_ver is not None else None
    need(pkg_id_val == expected_id, f"packaged identifier mismatch: {pkg_id_val!r}")
    need(pkg_ver_val == ver_val, f"packaged version {pkg_ver_val!r} != source {ver_val!r}")
    with zf.open("registration/license_en.txt") as fh:
        license_head = fh.read(80).decode("utf-8", errors="replace")
    need("GNU GENERAL PUBLIC LICENSE" in license_head, "packaged license does not look like GPL text")
    # Icon size heuristic
    try:
        from PIL import Image
        import io
        with zf.open("images/extension_icon.png") as fh:
            img = Image.open(io.BytesIO(fh.read()))
        w, h = img.size
        if (w, h) != (42, 42):
            warn(f"extension_icon.png is {w}x{h}; Extension Manager docs recommend 42x42")
    except Exception as exc:
        warn(f"could not check icon dimensions ({exc})")

for w in warnings:
    print(f"WARNING: {w}", file=sys.stderr)
if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK: identifier={expected_id} version={ver_val} package={oxt_path}")
PY

# XML well-formedness for key config files (xmllint optional)
if command -v xmllint >/dev/null 2>&1; then
  for xml in "${SRC}/description.xml" "${SRC}/META-INF/manifest.xml" \
             "${SRC}/Addons.xcu" "${SRC}/ProtocolHandler.xcu" \
             "${ROOT}/../pages/MarinaMojiKaeriten.update.xml"; do
    xmllint --noout "${xml}" || fail "xmllint failed: ${xml}"
  done
else
  warn "xmllint not installed — skipped extra XML checks (Python already parsed core XML)"
fi

# Slogan / branding in short descriptions
for f in "${SRC}/description/desc_en.txt" "${SRC}/description/desc_fr.txt" "${SRC}/description/desc_ja.txt"; do
  if ! grep -q "Make room for character" "${f}"; then
    fail "${f#"${ROOT}"/} missing slogan “Make room for character”"
  fi
  if ! grep -q "marinaMoji" "${f}"; then
    fail "${f#"${ROOT}"/} missing brand name marinaMoji"
  fi
done

if [[ "${ERR}" -ne 0 ]]; then
  echo "Validation failed." >&2
  exit 1
fi
echo "Validation passed."
