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

**Bootstrap note (LibreOffice):** installs that pre-date the `update-information` line cannot discover updates until the user installs **once** from a build that includes that line. After that, Tools → Extension Manager → Check for Updates can use the feed.

**Word behaviour reminder:** formatting JavaScript still reloads from GitHub Pages automatically. The banner appears when hosted `word` or `word_manifest` is newer than the values baked into the loaded build (stale cache, or a required manifest reinstall).

---

## Leftovers

| Item | Why it remains | Suggested next step |
|------|----------------|---------------------|
| **ONLYOFFICE check-for-updates** | Desktop has no update feed; plugin is a local folder | Sidebar button that fetches `version.json` and opens `release_url`, or publish to ONLYOFFICE Plugin Marketplace |
| **LibreOffice Mac after online update** | Extension Manager installs `.oxt` only; LO 26.x Mac sometimes needs the Mac `.dmg` macro copy for a working toolbar | Verify online update on Mac LO 26.x; if toolbar dies, fold macro install into `.oxt` or document “use `.dmg` on Mac” |
| **Word Windows QA** | Never run; blocks “finalised” announce | Run [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) section B checklist on Windows (upload production manifest) |
| **LO / OO in-plugin About** | No menu item yet | Optional “Check for updates” that reads `version.json` |
| **Bump `version.json` from build script** | Still hand-edited with host versions | Have `build-release.sh` rewrite `pages/version.json` + LO update XML from host version files |
| **AppSource / Marketplace** | Deferred on purpose | Partner Center (Word) or ONLYOFFICE Marketplace when public discovery matters |

---

## Maintainer checklist (each release that changes versions)

1. Bump host version fields (`description.xml`, `onlyoffice/config.json`, Word `package.json` + manifest `<Version>`).
2. Update `pages/version.json` (`plugins`, `word`, `word_manifest`, `libreoffice`, `onlyoffice`).
3. Update `pages/MarinaMojiKaeriten.update.xml` `<version>` to match LibreOffice.
4. Commit and push to `main` (Pages workflow deploys `version.json` / LO feed / Word).
5. Push a tag `plugins-vX.Y.Z` (or Actions → **Release plugins** → Run workflow with that tag). CI builds installers on macOS and creates the GitHub Release. Keep asset name `MarinaMojiKaeriten.oxt` so `/latest/download/` works.

---

## Related

- [INSTALLERS_AND_UPDATES.md](INSTALLERS_AND_UPDATES.md)
- [GITHUB_PAGES.md](GITHUB_PAGES.md)
- [STATUS.md](STATUS.md)
- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md)
