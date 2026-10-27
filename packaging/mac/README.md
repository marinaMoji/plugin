# Mac GUI installers (maintainers)

Build double-click installers for **end users**. No Terminal required on their side.

See [../../docs/DISTRIBUTION.md](../../docs/DISTRIBUTION.md) for the overview and [../../docs/SELF_HOSTED_PUBLISHING_PLAN.md](../../docs/SELF_HOSTED_PUBLISHING_PLAN.md) for the step-by-step publish plan.

## One-shot release build (macOS)

**Usual path:** push a `plugins-v*` tag — GitHub Actions (macOS) runs `build-release.sh` and publishes the Release. See [../../docs/INSTALLERS_AND_UPDATES.md](../../docs/INSTALLERS_AND_UPDATES.md) §1.7.

**Local:**

```bash
cd plugin/packaging
export MARINAMOJI_RELEASE_VERSION="0.0.2"   # optional; defaults in the script
export MARINAMOJI_PLUGIN_BASE="https://marinamoji.github.io/plugin/word"
./build-release.sh
```

On macOS this also builds:

| Output | Purpose |
|--------|---------|
| `Install marinaMoji Kaeriten (LibreOffice).app` | Copies LO Python macros + installs `.oxt` via `unopkg` |
| `marinamoji-kaeriten-libreoffice-mac.dmg` | DMG with installer + `.oxt` + readme |
| `Install marinaMoji Kaeriten (ONLYOFFICE).app` | Copies plugin into `sdkjs-plugins/{GUID}/` |
| `marinamoji-kaeriten-onlyoffice-mac.dmg` | DMG with installer + zip + readme |

## LibreOffice installer

```bash
./mac/build-libreoffice-installer-app.sh
./mac/build-libreoffice-dmg.sh
```

The `.app` bundles `MarinaMojiKaeriten.oxt` plus Python macro files. On macOS LibreOffice 26.x, bundled extension Python often fails to register; copying macros to the user profile fixes toolbar buttons.

The installer must **not** rely on bare `open file.oxt` (Launch Services often returns `kLSApplicationNotFoundErr` even when LibreOffice is installed). It locates `LibreOffice.app` and runs `Contents/MacOS/unopkg add --force`, with `open -a LibreOffice …` as fallback.

## ONLYOFFICE installer

```bash
./mac/build-onlyoffice-installer-app.sh
./mac/build-onlyoffice-dmg.sh
```

Install path (must match `onlyoffice/install-mac.sh`):

```text
~/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/sdkjs-plugins/{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}/
```

**Wrong:** `…/plugins/marinamoji-kaeriten/` — ONLYOFFICE will not load the plugin there.

## Word add-in installer

Word is **opt-in** — run the dedicated script (does not rebuild LO/ONLYOFFICE):

```bash
cp packaging/word-release.env.example packaging/word-release.env
# edit MARINAMOJI_PLUGIN_BASE=https://your-site/word
./packaging/build-word-release.sh
```

Or include Word in a full release:

```bash
export MARINAMOJI_INCLUDE_WORD=1
export MARINAMOJI_PLUGIN_BASE="https://your-domain/word"
./build-release.sh
```

## Gatekeeper

CI signs (Developer ID) and notarizes the dmgs via `sign-and-notarize.sh` when the `APPLE_*` secrets exist. Without them, builds are ad-hoc signed and users must use System Settings → Privacy & Security → Open Anyway. Ad-hoc sign by hand:

```bash
codesign --force --deep --sign - "Install marinaMoji Kaeriten (LibreOffice).app"
```

## Windows Word installer (sign after the release)

CI builds `marinamoji-kaeriten-word-setup.exe` (Inno Setup, `packaging/windows/`) and attaches it to the Release **unsigned**. Sign it from the maintainer machine with Certum SimplySign running and logged in:

```bash
node packaging/sign-windows-release.mjs plugins-vX.Y.Z --upload
```

Without `--upload` it only stages the signed file for review. The script verifies the signature, rewrites the exe line in `SHA256SUMS.txt`, re-uploads both and re-checks them. Needs `gh`, `osslsigncode` and `sign-windows` on `PATH` (same setup as marinaMoji's `scripts/sign-windows-release.mjs`).
