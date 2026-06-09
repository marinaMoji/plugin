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
| **LibreOffice** | `.oxt` or Mac `.dmg` | Nothing | Re-install `.oxt` / run Mac installer again |
| **Word** | Mac `.dmg` or Windows manifest `.xml` | **GitHub Pages** (`/word/`) | **Mostly automatic** — Word reloads JS from the web |
| **ONLYOFFICE** | `.plugin` / zip or Mac `.dmg` | Nothing (Desktop) | Re-install plugin folder |

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
| **Word npm package** | `word/package.json` | `"version"` (informational) |
| **Release label** | `MARINAMOJI_RELEASE_VERSION` env var | e.g. `0.4.0` → `plugins-v0.4.0` tag |

Word **add-in JavaScript** does not carry a separate store version once hosted: users load whatever is on GitHub Pages. The manifest `<Version>` mainly helps Word **drop cached add-in metadata** when you change ribbon or manifest URLs.

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

```bash
cd plugin/packaging
./publish-github-release.sh
```

Requires `gh auth login`. Creates or updates a release and uploads all files from `packaging/release/`.

Mirror download links on your **website** (`/install/libreoffice/`, etc.) pointing at the latest GitHub Release assets or at “latest” redirect URLs.

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

### 2.2 LibreOffice — **manual** reinstall

The extension lives **inside** the user profile after install. There is no phone-home updater in v1.

**Update path for users:**

1. Download new `.oxt` or Mac `.dmg` from GitHub Releases / website.
2. Extension Manager → **remove** old marinaMoji Kaeriten (optional but avoids version confusion).
3. Quit Writer → install new `.oxt` or run Mac installer → restart Writer.

**Future option (not implemented):** LibreOffice supports an **`updateURL`** in `description.xml` pointing at an extension update feed (XML). You could host a small update descriptor on your website or GitHub Pages that lists the latest `.oxt` URL and version. Extension Manager would then show “update available” like other LO extensions. This requires setting up that feed and testing on your target LO version.

### 2.3 ONLYOFFICE — **manual** reinstall

Desktop loads the plugin from a **local folder** (`sdkjs-plugins/{GUID}/`). Updates replace that folder.

**Update path:**

1. Download new `.plugin` or zip / Mac `.dmg`.
2. Remove old plugin (Plugin Manager → Supprimer, or delete the GUID folder).
3. Install the new build → restart ONLYOFFICE Writer.

**Future option:** ONLYOFFICE Plugin Marketplace supports versioning and in-app updates for listed plugins. That is a separate publication process (like Microsoft AppSource for Word).

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

### 3.3 In-plugin “new version available” (recommended next step)

**Word (easy):** the task pane already loads from the network. On open, fetch a small JSON file from GitHub Pages, e.g.:

```text
https://marinamoji.github.io/plugin/version.json
```

Example content:

```json
{
  "plugins": "0.4.0",
  "word": "0.1.3",
  "libreoffice": "0.3.9",
  "onlyoffice": "0.1.11",
  "release_url": "https://github.com/marinaMoji/plugin/releases/latest"
}
```

Compare to constants baked into the task pane at build time (or read current from `mapping.json`). If remote is newer, show a non-blocking banner: “Plugin v0.4.0 available — [Release notes]”. **Word code updates still apply automatically**; the banner mainly matters for LO/OO users who also use Word, or when a **manifest** bump is required.

**LibreOffice / ONLYOFFICE:** same `version.json` could be checked from a startup dialog or a “About / Check for updates” menu item if you add one later. Until then, LO/OO users rely on website + GitHub Watch.

**Implementation status:** not in v1 code yet — this section describes the intended pattern.

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
| **Production Word manifest URL** | Workflow writes `marinamoji-kaeriten-word.xml` with correct base URL |
| **Checksums** | `build-release.sh` / `build-word-release.sh` write `SHA256SUMS.txt` |
| **GitHub Release upload** | `./publish-github-release.sh` (one command after build) |

### 4.2 Semi-automated maintainer workflow (recommended)

```text
1. Bump versions (description.xml, config.json, manifest Version, …)
2. Run tests / QA on each host you ship
3. cd plugin/packaging && ./build-release.sh
4. git tag plugins-vX.Y.Z && git push origin plugins-vX.Y.Z
5. ./publish-github-release.sh
6. Confirm GitHub Pages workflow green (Word)
7. Update website install pages + version.json (when added)
8. Announce release
```

Word-only JS/CSS fix without manifest changes: steps 4–6 collapse to **push to `main`** and optionally announce.

### 4.3 Future automation (optional backlog)

| Idea | Effort | Benefit |
|------|--------|---------|
| **`version.json` on Pages** | Low | One URL for all hosts to check |
| **Task pane update banner** | Low | Word users see “new release” when manifest reinstall needed |
| **LO `updateURL` feed** | Medium | Native “update extension” in Extension Manager |
| **GitHub Action: release on tag** | Medium | Tag push builds + publishes without local Mac (DMG still needs macOS runner) |
| **ONLYOFFICE Marketplace** | High | In-app install + updates for OO users |
| **Apple notarization** | Medium ($99/yr) | Smoother Mac installs; still not auto-update |
| **M365 Centralized Deployment** | High (institutional) | IT pushes Word manifest to lab machines |

---

## Part 5 — User-facing update instructions (copy-paste for website)

### LibreOffice

> A new version is available on [GitHub Releases](https://github.com/marinaMoji/plugin/releases). Download the latest `.oxt` or Mac `.dmg`. Quit Writer, install, restart. You may remove the old extension first in Extension Manager.

### Word

> **Formatting code** updates automatically when you are online (we host the add-in on GitHub Pages). Quit and reopen Word if you do not see a fix.  
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

---

## Summary

- **Build installers** with `packaging/build-release.sh` (and `build-word-release.sh` for Word-only), bump per-host version fields, publish via `publish-github-release.sh`.
- **Word** is special: host code on **GitHub Pages** updates automatically; users reinstall the manifest only when you change registration URLs or `<Version>`.
- **LibreOffice and ONLYOFFICE** need **manual reinstall** for v1; tell users via **GitHub Releases**, your **website**, and (recommended next) a small **`version.json`** plus an in-pane notice.
- **Full auto-update** like an app store is out of scope until you adopt LO update feeds, ONLYOFFICE Marketplace, or Microsoft centralized deployment.
