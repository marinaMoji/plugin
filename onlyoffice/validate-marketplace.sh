#!/usr/bin/env bash
# Validate ONLYOFFICE plugin files against marketplace-oriented requirements.
# Does not submit anything. Safe to run in CI or before a manual PR.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CONFIG="${ROOT}/config.json"
ERR=0

fail() {
  echo "ERROR: $*" >&2
  ERR=1
}

warn() {
  echo "WARNING: $*" >&2
}

need_file() {
  [[ -f "$1" ]] || fail "missing file: ${1#"${ROOT}"/}"
}

echo "Validating ONLYOFFICE marketplace readiness in ${ROOT}"

need_file "${CONFIG}"
need_file "${ROOT}/index.html"
need_file "${ROOT}/CHANGELOG.md"
need_file "${ROOT}/scripts/kaeriten.js"
need_file "${ROOT}/scripts/exportCore.js"
need_file "${ROOT}/resources/light/icon.png"
need_file "${ROOT}/resources/dark/icon.png"
need_file "${ROOT}/resources/store/icons/icon.png"
need_file "${ROOT}/resources/store/icons/icon@2x.png"
need_file "${ROOT}/resources/store/screenshots/install.png"
need_file "${ROOT}/resources/store/screenshots/uninstall.png"

python3 - "${CONFIG}" "${ROOT}/CHANGELOG.md" <<'PY' || ERR=1
import json, re, sys
from pathlib import Path

config_path, changelog_path = Path(sys.argv[1]), Path(sys.argv[2])
cfg = json.loads(config_path.read_text(encoding="utf-8"))
errors = []

def need(cond, msg):
    if not cond:
        errors.append(msg)

name = cfg.get("name")
guid = cfg.get("guid", "")
version = cfg.get("version", "")
offered = cfg.get("offered", "")
need(name == "marinaMoji", f'name must be "marinaMoji" (got {name!r})')
need(re.fullmatch(r"asc\.\{[0-9A-Fa-f-]{36}\}", guid), f"guid must be asc.{{UUID}} (got {guid!r})")
need(re.fullmatch(r"\d+\.\d+\.\d+", version), f"version must be x.y.z (got {version!r})")
need(bool(offered), 'missing "offered" (publisher name for Plugin Manager)')
need(cfg.get("minVersion"), 'missing "minVersion"')

vars_ = cfg.get("variations") or []
need(vars_, "missing variations[]")
if vars_:
    v0 = vars_[0]
    desc = (v0.get("description") or "").strip()
    need(desc and desc != "marinaMoji", "variations[0].description must be real store copy, not just the brand name")
    need("Make room for character" in desc or "Make room for character" in (cfg.get("description") or ""),
         "slogan “Make room for character” missing from description")
    url = v0.get("url") or ""
    need(f"?v={version}" in url, f"url should cache-bust with ?v={version} (got {url!r})")
    editors = v0.get("EditorsSupport") or []
    need(editors == ["word"], f'EditorsSupport should be ["word"] only (got {editors!r})')
    store = v0.get("store") or {}
    for key in ("background", "categories", "icons", "screenshots"):
        need(key in store, f"variations[0].store missing {key!r}")
    shots = store.get("screenshots") or []
    need(len(shots) >= 1, "store.screenshots must list at least one image")

changelog = changelog_path.read_text(encoding="utf-8")
need(version in changelog, f"CHANGELOG.md must mention version {version}")

root = config_path.parent
for scale in ("", "@1.25x", "@1.5x", "@1.75x", "@2x"):
    for theme in ("light", "dark"):
        p = root / "resources" / theme / f"icon{scale}.png"
        need(p.is_file(), f"missing {p.relative_to(root)}")
for scale in ("", "@1.25x", "@1.5x", "@1.75x", "@2x"):
    p = root / "resources" / "store" / "icons" / f"icon{scale}.png"
    need(p.is_file(), f"missing {p.relative_to(root)}")

# Screenshot size heuristic (marketplace peers are large widescreen shots)
try:
    from PIL import Image
    for rel in shots:
        p = root / rel
        if not p.is_file():
            continue
        w, h = Image.open(p).size
        if w < 800 or h < 450:
            print(f"WARNING: {rel} is {w}x{h}; marketplace peers often use ~1280x720 or larger UI captures", file=sys.stderr)
except Exception as exc:
    print(f"WARNING: could not check screenshot dimensions ({exc})", file=sys.stderr)

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK: config version {version}, guid {guid}, offered {offered!r}")
PY

# Slogan in sidebar UI
if ! grep -q "Make room for character" "${ROOT}/index.html"; then
  fail "index.html missing slogan “Make room for character”"
fi

if [[ "${ERR}" -ne 0 ]]; then
  echo "Validation failed." >&2
  exit 1
fi
echo "Validation passed."
