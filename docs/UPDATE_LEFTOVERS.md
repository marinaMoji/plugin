# Update channel — done tonight vs leftovers

What shipped in the **update channel** work (October 2026), and what still needs a human later.

Live URLs (GitHub Pages for `marinaMoji/plugin`):

| URL | Role |
|-----|------|
| `https://marinamoji.github.io/plugin/version.json` | Shared version metadata for all hosts |
| `https://marinamoji.github.io/plugin/MarinaMojiKaeriten.update.xml` | LibreOffice Extension Manager update feed |

---

## Done

| Piece | Where |
|-------|--------|
| **Shared `version.json`** | [`pages/version.json`](../pages/version.json) — deployed with the Word Pages workflow |
| **LibreOffice update XML** | [`pages/MarinaMojiKaeriten.update.xml`](../pages/MarinaMojiKaeriten.update.xml) — download via GitHub Releases `/latest/download/MarinaMojiKaeriten.oxt` |
| **LO `update-information` hook** | [`libreoffice/marinamoji_kaeriten/description.xml`](../libreoffice/marinamoji_kaeriten/description.xml) |
| **Word in-pane notice** | [`word/src/updateCheck.js`](../word/src/updateCheck.js) — fetches `version.json` after Ready; session-dismissible banner |
| **Maintainer bump list** | See [INSTALLERS_AND_UPDATES.md](INSTALLERS_AND_UPDATES.md) §1.1 and §2 |
| **CI GitHub Release** | [`.github/workflows/release.yml`](../.github/workflows/release.yml) — tag `plugins-v*` (or Run workflow) builds on macOS and publishes assets |
| **Sync `version.json` + LO feed** | [`packaging/sync-version-channel.sh`](../packaging/sync-version-channel.sh) — called from `build-release.sh`; CI also pushes the synced files to `main` for Pages |

**Bootstrap note (LibreOffice):** installs that pre-date the `update-information` line cannot discover updates until the user installs **once** from a build that includes that line. After that, Tools → Extension Manager → Check for Updates can use the feed.

**Word behaviour reminder:** formatting JavaScript still reloads from GitHub Pages automatically. The banner appears when hosted `word` or `word_manifest` is newer than the values baked into the loaded build (stale cache, or a required manifest reinstall).

---

## Leftovers

| Item | Why it remains | Tracking |
|------|----------------|----------|
| **ONLYOFFICE check-for-updates** | Desktop has no update feed; plugin is a local folder | [plugin#1](https://github.com/marinaMoji/plugin/issues/1) · calendar `onlyoffice-update-check` |
| **LibreOffice Mac after online update** | Extension Manager installs `.oxt` only; LO 26.x Mac sometimes needs the Mac `.dmg` macro copy | [plugin#2](https://github.com/marinaMoji/plugin/issues/2) · calendar `lo-mac-online-update` |
| **Word Windows QA** | Never run; blocks “finalised” announce | calendar `windows-word-plugin` · [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) §B |
| **LO / OO in-plugin About** | No menu item yet (Word banner ships) | [plugin#3](https://github.com/marinaMoji/plugin/issues/3) · calendar `lo-oo-update-menu` |
| **AppSource / Marketplace** | Deferred on purpose (not a hard gate) | [plugin#4](https://github.com/marinaMoji/plugin/issues/4) · calendar `plugin-store-listings` |

---

## Maintainer checklist (each release that changes versions)

1. Bump host version fields (`description.xml`, `onlyoffice/config.json`, Word `package.json` + manifest `<Version>`). Optionally set default `MARINAMOJI_RELEASE_VERSION` in `build-release.sh`.
2. Commit and push to `main` (Pages deploys Word).
3. Push a tag `plugins-vX.Y.Z` (or Actions → **Release plugins**). CI runs `sync-version-channel.sh` via `build-release.sh`, pushes synced `pages/` to `main`, builds installers, and creates the GitHub Release. Keep asset name `MarinaMojiKaeriten.oxt` so `/latest/download/` works.

Local preview of the sync: `MARINAMOJI_RELEASE_VERSION=0.0.2 ./packaging/sync-version-channel.sh`

---

## Related

- [INSTALLERS_AND_UPDATES.md](INSTALLERS_AND_UPDATES.md)
- [GITHUB_PAGES.md](GITHUB_PAGES.md)
- [STATUS.md](STATUS.md)
- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md)
