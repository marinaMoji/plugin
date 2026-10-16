# Installers, publication, and updates

How to **build release-quality installers**, **publish** them, and **tell users when a new version exists** — including what can be automated today and what cannot (yet).

**Audience:** maintainers (you) and curious power users.  
**End-user install overview:** [DISTRIBUTION.md](DISTRIBUTION.md).  
**Step-by-step first release:** [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md).

---

## The big picture

marinaMoji ships **three separate office plugins** plus the **IME** (input method) from another repo. Each host has a different install shape and a different update story.

| Host | What users install once | What must stay online | Updates to *code* |
|------|-------------------------|------------------------|-------------------|
| **LibreOffice** | `.oxt` or Mac `.dmg` | Update feed on **GitHub Pages** (optional check) | Extension Manager can offer update; or re-install `.oxt` / Mac `.dmg` |
| **Word** | Mac `.dmg` or Windows manifest `.xml` | **GitHub Pages** (`/word/` + `version.json`) | **Mostly automatic** — Word reloads JS from the web; pane may show a notice |
| **ONLYOFFICE** | `.plugin` / zip or Mac `.dmg` | Nothing (Desktop) | Re-install plugin folder (no auto-check yet) |

**Done vs leftovers:** [UPDATE_LEFTOVERS.md](UPDATE_LEFTOVERS.md).

The IME is updated separately from [github.com/marinaMoji/marinaMoji](https://github.com/marinaMoji/marinaMoji). Office plugins only **format** text the IME already typed.

---

## Part 1 — Building proper installers

“Proper” here means: **no Terminal for end users**, **checksums on GitHub**, **Gatekeeper instructions**, and **version numbers bumped** in the right files before you build.

### 1.1 Version numbers (keep in sync)

Before every public release, bump versions in the places users and tools actually read:

| Product | File | Field |
|---------|------|--------|
| **LibreOffice** | `libreoffice/marinamoji_kaeriten/description.xml` | `<version value="…"/>` |
| **ONLYOFFICE** | `onlyoffice/config.json` | `"version"` (+ cache-bust `?v=` in `index.html` url) |
| **Word manifest** | `word/manifest.xml` and `word/manifest.production.xml` | `<Version>…</Version>` |
| **Word npm package** | `word/package.json` | `"version"` (baked into task pane for update notice) |
| **Shared channel** | `pages/version.json` | Written by `packaging/sync-version-channel.sh` from host versions + release label |
| **LO update feed** | `pages/MarinaMojiKaeriten.update.xml` | Same sync script (LibreOffice `<version>`) |
| **Release label** | `MARINAMOJI_RELEASE_VERSION` env var / tag `plugins-v*` | e.g. `0.4.0` → `plugins-v0.4.0` |

Word **add-in JavaScript** does not carry a separate store version once hosted: users load whatever is on GitHub Pages. The manifest `<Version>` mainly helps Word **drop cached add-in metadata** when you change ribbon or manifest URLs. `build-release.sh` (and the Release CI job) regenerates the channel files; you do not edit them by hand.

### 1.2 One-shot release build (macOS maintainer machine)

From the plugin repo:

```bash
cd plugin/packaging

export MARINAMOJI_RELEASE_VERSION="0.4.0"
export MARINAMOJI_RELEASE_TAG="plugins-v0.4.0"
export MARINAMOJI_GITHUB_REPO="marinaMoji/plugin"

# Word (optional — include when Word QA is green):
export MARINAMOJI_INCLUDE_WORD=1
export MARINAMOJI_PLUGIN_BASE="https://marinamoji.github.io/plugin/word"

./build-release.sh
```

**Outputs** in `packaging/release/`:

| Artifact | Platform | Purpose |
|----------|----------|---------|
| `MarinaMojiKaeriten.oxt` | All | LibreOffice Extension Manager |
| `marinamoji-kaeriten-libreoffice-mac.dmg` | Mac | GUI installer + `.oxt` + readme |
| `marinamoji-kaeriten-onlyoffice.zip` | All | Manual ONLYOFFICE folder install |
| `marinamoji-kaeriten.plugin` | All | ONLYOFFICE Plugin Manager (7.4+) |
| `marinamoji-kaeriten-onlyoffice-mac.dmg` | Mac | GUI installer |
| `word-dist.zip` | — | Archive of hosted files (when Word included) |
| `marinamoji-kaeriten-word.xml` | Windows / reference | Production manifest |
| `marinamoji-kaeriten-word-mac.dmg` | Mac | Copies manifest into Word `wef/` |
| `INSTALL.txt`, `SHA256SUMS.txt`, `VERSION.txt` | All | Human readme + integrity |

On **Linux/Windows** without a Mac, you still get `.oxt`, ONLYOFFICE zip/`.plugin`, and Word zip/manifest — but not the `.dmg` GUI wrappers (build those on a Mac before publishing).

Details per host: [packaging/mac/README.md](../packaging/mac/README.md).

### 1.3 Word-only release (faster iteration)

When only the Word add-in changed:

```bash
cp packaging/word-release.env.example packaging/word-release.env
# MARINAMOJI_PLUGIN_BASE=https://marinamoji.github.io/plugin/word
./packaging/build-word-release.sh
```

Then push to `main` — the [GitHub Pages workflow](../.github/workflows/word-pages.yml) rebuilds and deploys `word/dist/` automatically. You often **do not** need a new Mac `.dmg` if the manifest URL and `<Version>` are unchanged.

**Important:** `./word/install-mac.sh` installs the **dev** manifest (`127.0.0.1:3000`). For publication testing use:

```bash
./word/install-mac-production.sh
```

See [GITHUB_PAGES.md](GITHUB_PAGES.md).

### 1.4 ONLYOFFICE plugin package

```bash
cd plugin/onlyoffice
./build.sh
# → dist/marinamoji-kaeriten.plugin
```

Bump `config.json` `version` and the `?v=` query on `index.html` so Desktop clients refresh cached plugin files.

### 1.5 LibreOffice `.oxt`

```bash
cd plugin/libreoffice
./build.sh
# → dist/MarinaMojiKaeriten.oxt
```

Bump `description.xml` `<version>`. The Mac GUI installer bundles this `.oxt` plus Python macros (required on LO 26.x).

### 1.6 Quality checklist before you publish

- [ ] Fresh machine or VM: each installer path tested once
- [ ] Mac: **Right-click → Open** documented ([INSTALL-MAC-GATEKEEPER.md](INSTALL-MAC-GATEKEEPER.md))
- [ ] `SHA256SUMS.txt` matches uploaded files
- [ ] Word: `https://marinamoji.github.io/plugin/word/taskpane.html` loads in Safari
- [ ] Word: production manifest in `wef/` (not localhost dev manifest)
- [ ] Website / release notes say **install IME first**
- [ ] Git tag matches `MARINAMOJI_RELEASE_TAG`

### 1.7 Publishing to GitHub Releases

**Preferred (CI):** after version bumps are on `main`, create and push a tag:

```bash
git tag plugins-v0.0.2
git push origin plugins-v0.0.2
```

Or: GitHub → Actions → **Release plugins** → **Run workflow** → enter `plugins-v0.0.2`.

The [release workflow](../.github/workflows/release.yml) runs on **macOS** (needed for `.dmg` / `.app`), builds with `packaging/build-release.sh`, and uploads assets via `publish-github-release.sh`.

**Local fallback** (same scripts CI uses):

```bash
cd plugin/packaging
export MARINAMOJI_PLUGIN_BASE="https://marinamoji.github.io/plugin/word"
./build-release.sh
./publish-github-release.sh
```

Requires `gh auth login` locally. Mirror download links on your **website** (`/install/libreoffice/`, etc.) pointing at the latest GitHub Release assets.

---

## Part 2 — What “updates” mean per host

### 2.1 Word — **semi-automatic** (best case)

Architecture:

```text
User’s Mac/PC                    GitHub Pages (always current)
────────────────                 ─────────────────────────────
manifest.xml  ──points to──►     /word/taskpane.html
(in wef/ once)                   /word/taskpane.js
                                 /word/mapping.json
                                 …
```

After the one-time manifest install:

- **JavaScript, CSS, and mapping.json** updates deploy when you push to `main` (GitHub Actions).
- Users get new behaviour the **next time** Word loads the task pane or ribbon functions run — **no re-download** for most bugfix releases.
- **No background updater** runs inside Word; Office simply fetches the hosted files again (subject to cache).

**When users must re-install the manifest:**

- You change `<Id>`, `<SourceLocation>` base URL, or ribbon structure in a breaking way → bump `<Version>` and ship a new `.xml` / Mac `.dmg`.
- Word caches add-ins aggressively; a manifest version bump clears stale registration.

**When users see nothing new:**

- Word or WebView cached old JS — quit Word (Cmd+Q), reopen, or bump manifest `<Version>`.
- They still have the **dev** manifest (`127.0.0.1`) — run `install-mac-production.sh`.

### 2.2 LibreOffice — Extension Manager feed + manual reinstall

The extension lives **inside** the user profile after install. Builds that include `update-information` in `description.xml` point at:

```text
https://marinamoji.github.io/plugin/MarinaMojiKaeriten.update.xml
```

That file lists the latest version and downloads `MarinaMojiKaeriten.oxt` from GitHub Releases `/latest/download/`.

**Update path for users:**

1. **Preferred (after one bootstrap install):** Tools → Extension Manager → Check for Updates (wording varies by LO version / language).
2. Or download new `.oxt` or Mac `.dmg` from GitHub Releases / website.
3. Quit Writer → install → restart Writer. Removing the old extension first avoids version confusion.

**Bootstrap:** users on an older `.oxt` without `update-information` must install once from a release that includes the hook before Check for Updates works.

**Mac caveat:** online update installs the `.oxt` only. On LibreOffice 26.x Mac, if the toolbar dies after an online update, run the Mac `.dmg` installer (macro copy). See [UPDATE_LEFTOVERS.md](UPDATE_LEFTOVERS.md).

### 2.3 ONLYOFFICE — **manual** reinstall

Desktop loads the plugin from a **local folder** (`sdkjs-plugins/{GUID}/`). Updates replace that folder.

**Update path:**

1. Download new `.plugin` or zip / Mac `.dmg`.
2. Remove old plugin (Plugin Manager → Supprimer, or delete the GUID folder).
3. Install the new build → restart ONLYOFFICE Writer.

**Marketplace path:** listing on the official ONLYOFFICE Plugin Marketplace gives in-app install + versioned updates via Plugin Manager. That is a **separate** publication process (copy into `onlyoffice.github.io` + PR). Maintainer guide: [ONLYOFFICE_MARKETPLACE.md](ONLYOFFICE_MARKETPLACE.md).

### 2.4 marinaMoji IME

Not covered in this repo. Treat IME and office plugins as **independent release lines**. Mention both in release notes when a change affects typing vs formatting.

---

## Part 3 — Alerting users to updates

Today there is **no unified auto-update notifier** in the plugins. Use a **layered** approach:

### 3.1 GitHub Releases (canonical)

- Tag every public drop: `plugins-v0.4.0`.
- Write short **release notes** (what changed, which hosts affected).
- Users can **Watch → Custom → Releases** on `marinaMoji/plugin`.

`publish-github-release.sh` generates a starter `RELEASE_NOTES.md` table of assets.

### 3.2 Website banner

On `/install/` and per-host pages, show:

```text
Latest office plugins: v0.4.0 (June 2026) — [Download on GitHub]
```

Update manually when you tag, or generate from GitHub API in your site CMS (Grav) if you want automation later.

### 3.3 In-plugin “new version available”

**Word (shipped):** the task pane fetches `https://marinamoji.github.io/plugin/version.json` after Ready. If remote `word` or `word_manifest` is newer than the build-time constants, a dismissible banner appears with a link to `release_url`. **Word code updates still apply automatically** on reopen; the banner covers stale cache and required **manifest** reinstalls.

**LibreOffice (shipped feed):** Extension Manager uses `MarinaMojiKaeriten.update.xml` on GitHub Pages (see §2.2). No in-Writer dialog beyond LO’s own update UI.

**ONLYOFFICE:** still website + GitHub Watch only. Same `version.json` can power a future sidebar “Check for updates” — see [UPDATE_LEFTOVERS.md](UPDATE_LEFTOVERS.md).

### 3.4 Email / newsletter / Mastodon

For a small scholarly community, a short post when you tag a release is often enough. Link to GitHub Releases and the install page.

### 3.5 What not to rely on

| Approach | Why it fails for us today |
|----------|---------------------------|
| **Mac App Store / Sparkle** | We ship unsigned `.app` installers, not sandboxed Mac apps |
| **Microsoft AppSource** | Deferred; sideload + self-host instead |
| **Silent auto-install without user action** | LO/OO have no supported silent updater in our install model; Word updates JS but not manifest |
| **Only bumping git** | Users never see git; they see Releases or the website |

---

## Part 4 — Automating what you can

### 4.1 Already automated

| Step | How |
|------|-----|
| **Word hosted files** | Push to `main` → `.github/workflows/word-pages.yml` → GitHub Pages |
| **`version.json` + LO update XML** | Copied from `pages/` by the same Pages workflow |
| **Production Word manifest URL** | Workflow writes `marinamoji-kaeriten-word.xml` with correct base URL |
| **Checksums** | `build-release.sh` / `build-word-release.sh` write `SHA256SUMS.txt` |
| **GitHub Release (installers)** | Tag `plugins-v*` → `.github/workflows/release.yml` (macOS) → build + upload |
| **ONLYOFFICE marketplace export** | `onlyoffice/export-marketplace.sh` + [onlyoffice-marketplace.yml](../.github/workflows/onlyoffice-marketplace.yml) → zip artifact (no upstream PR) |

### 4.2 Semi-automated maintainer workflow (recommended)

```text
1. Bump host versions (description.xml, config.json, Word package.json + manifest Version, …)
2. Run tests / QA on each host you ship
3. Commit + push to main (Pages deploys Word)
4. git tag plugins-vX.Y.Z && git push origin plugins-vX.Y.Z
5. Confirm Actions → "Release plugins" green (syncs version.json + LO feed onto main, builds, publishes)
6. Announce release
```

Word-only JS/CSS fix without a new installer: **push to `main`** (Pages) and optionally announce — no new tag required.

### 4.3 Future automation (optional backlog)

| Idea | Effort | Benefit |
|------|--------|---------|
| **ONLYOFFICE sidebar “Check for updates”** | Low | Reuse `version.json` ([plugin#1](https://github.com/marinaMoji/plugin/issues/1)) |
| **Mac-safe LO online update** | Medium | Toolbar still works after Extension Manager update |
| **ONLYOFFICE Marketplace** | Medium (docs + validation ready; PR + screenshots remain) | In-app install + updates — [ONLYOFFICE_MARKETPLACE.md](ONLYOFFICE_MARKETPLACE.md) |
| **Apple notarization** | Medium ($99/yr) | Smoother Mac installs; still not auto-update |
| **M365 Centralized Deployment** | High (institutional) | IT pushes Word manifest to lab machines |

---

## Part 5 — User-facing update instructions (copy-paste for website)

### LibreOffice

> In Writer: **Tools → Extension Manager → Check for Updates** (after you have installed a build that includes the marinaMoji update feed). Or download the latest `.oxt` or Mac `.dmg` from [GitHub Releases](https://github.com/marinaMoji/plugin/releases). Quit Writer, install, restart. On Mac, if the toolbar stops working after an online update, run the Mac `.dmg` installer once.

### Word

> **Formatting code** updates automatically when you are online (we host the add-in on GitHub Pages). Quit and reopen Word if you do not see a fix. The Kaeriten pane may show a short notice when a newer build or manifest is available.  
> If we announce a **manifest update**, download the new Mac installer or `marinamoji-kaeriten-word.xml` and install again, then restart Word.

### ONLYOFFICE

> Download the latest `.plugin` or Mac installer from [GitHub Releases](https://github.com/marinaMoji/plugin/releases). Remove the old plugin in Plugin Manager, install the new one, restart ONLYOFFICE Writer.

---

## Part 6 — Troubleshooting update confusion

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Word: “network connectivity” error | Dev manifest (`127.0.0.1`) still installed | `./word/install-mac-production.sh` |
| Word: old UI after deploy | WebView cache | Cmd+Q Word; bump manifest `<Version>` if persistent |
| LO: toolbar dead after update | Macros not copied (Mac LO 26.x) | Use Mac `.dmg` installer, not raw `.oxt` alone |
| OO: plugin unchanged after install | Old GUID folder not replaced | Remove `{7A9E3B2C-…}` folder, reinstall |
| “I updated but nothing changed” | Updated wrong product (IME vs plugin) | Check release notes; IME is separate repo |

---

## Related documents

| Doc | Topic |
|-----|--------|
| [DISTRIBUTION.md](DISTRIBUTION.md) | Strategy, Gatekeeper, asset list |
| [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md) | First public release phases |
| [GITHUB_PAGES.md](GITHUB_PAGES.md) | Word hosting + production install |
| [INSTALL-MAC-GATEKEEPER.md](INSTALL-MAC-GATEKEEPER.md) | Unsigned Mac installers |
| [packaging/mac/README.md](../packaging/mac/README.md) | Build `.app` / `.dmg` |
| [STATUS.md](STATUS.md) | Current QA gates |
| [ONLYOFFICE_MARKETPLACE.md](ONLYOFFICE_MARKETPLACE.md) | Official Plugin Marketplace listing + updates |

---

## Summary

- **Build installers** by tagging `plugins-vX.Y.Z` (CI on macOS) or locally with `packaging/build-release.sh` + `publish-github-release.sh`. Bump per-host version fields **and** `pages/version.json` / LO update XML before you tag.
- **Word:** hosted code on **GitHub Pages** updates automatically; task pane can show a notice from `version.json`; reinstall the manifest when `word_manifest` advances.
- **LibreOffice:** Extension Manager feed on GitHub Pages; bootstrap install once; Mac `.dmg` still the safe path if the toolbar breaks after online update.
- **ONLYOFFICE:** still **manual reinstall** via Releases until listed; marketplace path in [ONLYOFFICE_MARKETPLACE.md](ONLYOFFICE_MARKETPLACE.md). Leftovers in [UPDATE_LEFTOVERS.md](UPDATE_LEFTOVERS.md).
- **Full silent auto-install** (no user click) remains out of scope.
