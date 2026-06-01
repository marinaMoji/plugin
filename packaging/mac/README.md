# Mac GUI installers (maintainers)

Build double-click installers for **end users**. No Terminal required on their side.

See [../../docs/DISTRIBUTION.md](../../docs/DISTRIBUTION.md) for the full distribution strategy.

## Word add-in installer

**Prerequisite:** Host `plugin/word/dist/` on your website with valid HTTPS, then:

```bash
cd plugin/packaging
export MARINAMOJI_PLUGIN_BASE="https://your-domain/word"
./build-release.sh
./mac/build-word-installer-app.sh
./mac/build-word-dmg.sh
```

Upload `release/marinamoji-kaeriten-word-mac.dmg` to GitHub Releases and your website.

The `.app` copies `manifest.production.xml` into Word’s `wef` folder. Word loads the add-in from your URL — **no** `npm run serve` on the user’s Mac.

## ONLYOFFICE installer

1. Run `./build-release.sh` (creates `marinamoji-kaeriten-onlyoffice.zip`).
2. Unzip into `release/marinamoji-kaeriten-onlyoffice/` for bundling, or adapt `build-onlyoffice-installer-app.sh` (same pattern as Word).

Compile AppleScript:

```bash
osacompile -o "Install marinaMoji Kaeriten (ONLYOFFICE).app" install-onlyoffice-plugin.applescript
# Copy unzipped plugin into MyApp.app/Contents/Resources/marinamoji-kaeriten-onlyoffice/
```

## Gatekeeper

Installers are **not notarized**. Document **Right-click → Open** on the website. Optional ad-hoc sign:

```bash
codesign --force --deep --sign - "Install marinaMoji Kaeriten.app"
```

## LibreOffice

No `.app` required: ship **`MarinaMojiKaeriten.oxt`** only. Users double-click to install via Extension Manager.
