# Mac GUI installers (maintainers)

Build double-click installers for **end users**. No Terminal required on their side.

See [../../docs/DISTRIBUTION.md](../../docs/DISTRIBUTION.md) for the overview and [../../docs/SELF_HOSTED_PUBLISHING_PLAN.md](../../docs/SELF_HOSTED_PUBLISHING_PLAN.md) for the step-by-step publish plan.

## One-shot release build (macOS)

```bash
cd plugin/packaging
export MARINAMOJI_RELEASE_VERSION="0.3.7"   # optional label
./build-release.sh
```

On macOS this also builds:

| Output | Purpose |
|--------|---------|
| `Install marinaMoji Kaeriten (LibreOffice).app` | Copies LO Python macros + opens `.oxt` |
| `marinamoji-kaeriten-libreoffice-mac.dmg` | DMG with installer + `.oxt` + readme |
| `Install marinaMoji Kaeriten (ONLYOFFICE).app` | Copies plugin into `sdkjs-plugins/{GUID}/` |
| `marinamoji-kaeriten-onlyoffice-mac.dmg` | DMG with installer + zip + readme |

## LibreOffice installer

```bash
./mac/build-libreoffice-installer-app.sh
./mac/build-libreoffice-dmg.sh
```

The `.app` bundles `MarinaMojiKaeriten.oxt` plus Python macro files. On macOS LibreOffice 26.x, bundled extension Python often fails to register; copying macros to the user profile fixes toolbar buttons.

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

Installers are **not notarized**. Document **Right-click → Open** on the website. Optional ad-hoc sign:

```bash
codesign --force --deep --sign - "Install marinaMoji Kaeriten (LibreOffice).app"
```
