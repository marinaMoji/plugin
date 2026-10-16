# ONLYOFFICE Plugin Marketplace — maintainer guide

How to list **marinaMoji** in the official [ONLYOFFICE Plugin Marketplace](https://github.com/ONLYOFFICE/onlyoffice.github.io) and keep it updated.

**Audience:** maintainers.  
**Plugin code:** [onlyoffice/](../onlyoffice/)  
**Host overview:** [ONLYOFFICE.md](ONLYOFFICE.md) · **GitHub Releases:** [INSTALLERS_AND_UPDATES.md](INSTALLERS_AND_UPDATES.md)

**Do not** open a marketplace pull request or publish a release without an explicit go-ahead.

---

## Mental model (important)

The marketplace is **not** a package registry that pulls from our GitHub Releases.

```text
marinaMoji/plugin  (source of truth)
        │
        ├─► GitHub Releases (.plugin, zip, Mac .dmg)   ← sideload / Mac installer
        │
        └─► copy built files into ONLYOFFICE/onlyoffice.github.io
              sdkjs-plugins/content/marinamoji/
            then open a PR                              ← Plugin Manager install/update
```

- Plugin Manager installs and updates from the **copy** hosted under `sdkjs-plugins/content/<folder>/`.
- Every **initial** listing and every **update** is a pull request against [ONLYOFFICE/onlyoffice.github.io](https://github.com/ONLYOFFICE/onlyoffice.github.io).
- Our Releases remain useful for Mac DMG users and offline `.plugin` install; they do **not** by themselves update marketplace users.

Official docs:

- [Preparing for release](https://api.onlyoffice.com/docs/plugins/development-workflow/publishing/preparing-for-release/)
- [Submit to marketplace](https://api.onlyoffice.com/docs/plugins/development-workflow/publishing/submit-to-marketplace/)
- [Versioning and updates](https://api.onlyoffice.com/docs/plugins/development-workflow/publishing/versioning-and-updates/)
- Marketplace repo [store/README.md](https://github.com/ONLYOFFICE/onlyoffice.github.io/blob/master/store/README.md)

---

## Stable identifiers (do not change)

| Field | Value | Why |
|-------|--------|-----|
| **Folder / store `name`** | `marinamoji` | Matches `store/config.json` entry; lowercase like other plugins |
| **Display name** | `marinaMoji` | Brand |
| **GUID** | `asc.{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}` | Permanent; changing it creates a *new* plugin |
| **Slogan** | Make room for character | Use in UI / store copy where a slogan fits |
| **Editors** | `word` only | Document Editor (Writer) |

Host version (`onlyoffice/config.json` → `version`) is **independent** of the umbrella tag `plugins-v*` and of LibreOffice / Word versions. Marketplace update detection uses **only** that `version` field (and the same GUID).

---

## What is already in good shape

- Manifest shape: `guid`, `version`, `minVersion`, `store` (background, categories, icons, screenshots paths)
- Light/dark toolbar icons at 100%–200% scales
- Store tile icons at 120×60 … 240×120
- Local `mapping.json` (no marinaMoji network service / telemetry)
- CDN load of `plugins.js` (same pattern as other marketplace plugins)
- Build: `onlyoffice/build.sh` → `dist/marinamoji-kaeriten.plugin`
- CI already builds ONLYOFFICE artifacts on `plugins-v*` tags

---

## Compliance checklist

### Documented requirements

| Requirement | Status |
|-------------|--------|
| `config.json`, `index.html`, scripts | Required |
| Light/dark icons + scale variants | Required |
| `resources/store/icons/` | Required for marketplace |
| `version` as `x.x.x` | Required for updates |
| `offered` (publisher name) | Required for Plugin Manager (store README) |
| `CHANGELOG.md` in plugin folder | Required (store README) |
| `store` block (background, icons, screenshots, categories) | Required / strongly recommended |
| Copy into `sdkjs-plugins/content/<name>/` | Submission step |
| Entry in root `store/config.json` | Submission step |
| PR to ONLYOFFICE marketplace repo | Submission step |

### Conventions (inferred from listed plugins)

| Convention | Notes |
|------------|--------|
| Marketplace listing text | Uses **`variations[0].description`**, not a top-level-only description |
| Screenshots | Peers often use ~2480×1416 UI captures; logo tiles alone look weak |
| Broad `nameLocale` / `descriptionLocale` | Ascensio plugins ship many languages; we keep EN + FR (+ optional JA) |
| `plugins.js` from `onlyoffice.github.io` CDN | Normal; not a privacy red flag by itself |

### Still needs a human

| Item | Why | Tracking |
|------|-----|----------|
| **Real screenshots** | Capture Writer + marinaMoji sidebar + a rendered paragraph; approve before packaging | [plugin#5](https://github.com/marinaMoji/plugin/issues/5) |
| **Desktop QA** | Install via Plugin Manager, activate/deactivate, uninstall, update path | [plugin#6](https://github.com/marinaMoji/plugin/issues/6) |
| **Upstream PR** | Explicit authorization; ONLYOFFICE reviews | — |
| **License comfort** | Plugin repo is GPL-3.0; marketplace host repo is AGPL-3.0 | — |

Validate / export locally anytime:

```bash
cd plugin/onlyoffice
./validate-marketplace.sh
./build.sh
./export-marketplace.sh
# → packaging/release/marketplace/marinamoji/
# → packaging/release/marinamoji-onlyoffice-marketplace.zip
# → packaging/release/marketplace/SUBMIT.txt
```

CI: [`.github/workflows/onlyoffice-marketplace.yml`](../.github/workflows/onlyoffice-marketplace.yml) runs on `onlyoffice/**` changes and uploads the zip as an Actions artifact. Tag releases (`plugins-v*`) also attach the zip via `build-release.sh` when export succeeds.

---

## Version numbers

1. Bump `onlyoffice/config.json` → `"version"` **and** the `?v=` on `variations[0].url`.
2. Add a section to `onlyoffice/CHANGELOG.md`.
3. On release, `packaging/sync-version-channel.sh` copies the OO version into `pages/version.json` → `"onlyoffice"`.

Always increment `version` when submitting a marketplace update. Same version → Plugin Manager cannot see an update. **Never** change the GUID for an update.

---

## Initial marketplace submission

1. Finish compliance checklist; run `./export-marketplace.sh` (builds + validates + stages).
2. Smoke-test the `.plugin` in ONLYOFFICE Desktop (Plugin Manager → My plugins → Install manually). See [plugin#6](https://github.com/marinaMoji/plugin/issues/6).
3. Replace placeholder screenshots with approved UI captures ([plugin#5](https://github.com/marinaMoji/plugin/issues/5)).
4. Fork [ONLYOFFICE/onlyoffice.github.io](https://github.com/ONLYOFFICE/onlyoffice.github.io) when authorized; enable GitHub Pages on the fork if you want web testing.
5. After forking/cloning the marketplace repo locally, apply the export (no commit/push):

   ```bash
   cd plugin/onlyoffice
   ./apply-marketplace-export.sh /path/to/onlyoffice.github.io
   ```

   Or copy `packaging/release/marketplace/marinamoji/` by hand to `sdkjs-plugins/content/marinamoji/` and append `store-config-snippet.json` to `store/config.json`.

6. Follow `marketplace/SUBMIT.txt`. Review `git status` in the fork.
7. Open a PR to `ONLYOFFICE/onlyoffice.github.io` only with explicit authorization. Mention: no API keys required; Desktop + Writer only.
8. After merge, confirm the plugin appears in Plugin Manager and installs cleanly.

**Review time:** ONLYOFFICE says they review “as soon as possible.” There is **no** documented SLA.

**Rejected PR:** fix issues in our repo, rebuild, update the fork, push again (or open a new PR). Ask in the marketplace repo issues if requirements are unclear.

---

## Subsequent updates

1. Change code / assets in `marinaMoji/plugin` as usual.
2. Bump OO `version` + `CHANGELOG.md`.
3. Tag `plugins-v*` if you want GitHub Release assets (optional for marketplace-only fixes).
4. Sync your marketplace fork with upstream `master`.
5. Replace `sdkjs-plugins/content/marinamoji/` with the new built files (same GUID, new version).
6. Open a PR (title like `Update marinamoji to vX.Y.Z`).
7. After merge, users see an update in Plugin Manager and choose to install it.

Marketplace version **may lag** a GitHub Release by days while the PR waits. That is expected.

---

## What is automated vs manual

| Step | Automated today? |
|------|------------------|
| Build `.plugin` / zip / Mac DMG on `plugins-v*` | Yes — [release.yml](../.github/workflows/release.yml) |
| Validate manifest + marketplace assets | Yes — `validate-marketplace.sh` (end of `build.sh`; CI workflow) |
| Export `marinamoji/` tree + zip | Yes — `export-marketplace.sh` (CI artifact + soft-fail in `build-release.sh`) |
| Copy export into a local marketplace clone | Yes — `apply-marketplace-export.sh` (still no push/PR) |
| Attach marketplace zip to GitHub Releases | Yes when export succeeds — optional asset |
| Open PR against ONLYOFFICE | **Manual** — never automated without authorization |
| ONLYOFFICE review + merge | **Manual** (them) |
| User clicks Update in Plugin Manager | **Manual** (them) |

Do **not** auto-submit upstream PRs without authorization. Marketplace export failure is a **warning** in `build-release.sh` so LibreOffice/Word assets still publish.

---

## Verifying an update reached users

1. Confirm the PR is merged on `ONLYOFFICE/onlyoffice.github.io` and `sdkjs-plugins/content/marinamoji/config.json` shows the new `version`.
2. In Desktop Editors: Plugins → Plugin Manager → find marinaMoji → update/install.
3. Open the sidebar and confirm behaviour; optionally check that `index.html?v=…` matches the new version.

Sideloaded Mac DMG installs do **not** auto-switch to the marketplace copy; those users keep updating via Releases until they install from Plugin Manager (or you document one preferred path).

---

## Related

- [ONLYOFFICE.md](ONLYOFFICE.md) — Desktop vs Document Server
- [INSTALLERS_AND_UPDATES.md](INSTALLERS_AND_UPDATES.md) — GitHub Releases and host update paths
- [UPDATE_LEFTOVERS.md](UPDATE_LEFTOVERS.md) — OO in-plugin update check still open
- [STATUS.md](STATUS.md) — pre-publish QA gates
- [onlyoffice/README.md](../onlyoffice/README.md) — install commands for testers
