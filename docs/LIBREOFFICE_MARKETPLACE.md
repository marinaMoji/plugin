# LibreOffice Extensions website — maintainer guide

How to list **marinaMoji** on the official [LibreOffice Extensions](https://extensions.libreoffice.org/) site and keep Extension Manager updates working.

**Audience:** maintainers.  
**Extension code:** [libreoffice/](../libreoffice/)  
**GitHub Releases + self-hosted feed:** [INSTALLERS_AND_UPDATES.md](INSTALLERS_AND_UPDATES.md)

**Extensions website** listing can wait (screenshots optional). A **GitHub Release + update feed** does not require the store.

---

## Your checklist — first GitHub release (`0.3.10`)

Do this in the **plugin** repo when you are ready. No Extensions website step here.

1. **Review / commit** all local changes (including this doc). Note: `main` may already be a few commits ahead of `origin` with mixed ONLYOFFICE + LO prep — push only when that history looks right to you.
2. **Sanity check locally** (optional but quick):

   ```bash
   cd plugin/libreoffice
   ./build.sh && ./validate-extension.sh
   python3 tests/test_parser.py && python3 tests/test_export.py
   ```

3. **Push `main`** to `origin` when you are happy with the commits.
4. **Tag and push** (version must match `description.xml`):

   ```bash
   git tag libreoffice-v0.3.10
   git push origin libreoffice-v0.3.10
   ```

   Or: Actions → **Release LibreOffice extension** → run with tag `libreoffice-v0.3.10`.  
   On a **tag push**, CI publishes the GitHub Release **and** updates the live Pages feed.  
   On **manual dispatch**, leave `publish_update_feed` unchecked to upload the Release only and review the update XML artifact first.
5. **Confirm**:
   - Release asset: `https://github.com/marinaMoji/plugin/releases/tag/libreoffice-v0.3.10`
   - Feed (after Pages deploy): `https://marinamoji.github.io/plugin/MarinaMojiKaeriten.update.xml` shows `0.3.10` and a versioned (not `/latest/`) download URL
6. **Optional later:** Extensions website submission (below). Screenshots help there; they are not required for steps 1–5.

**Do not edit** `pages/MarinaMojiKaeriten.update.xml` by hand before the Release exists — CI writes the versioned URL after the `.oxt` is uploaded.

---

## Mental model (important)

Publication on **extensions.libreoffice.org** and **native Extension Manager updates** are separate systems.

```text
A. Marketplace listing (discovery / first install)
   You upload (or link) an .oxt on extensions.libreoffice.org
   → users find and install it from the website / Extension Manager browse UI

B. Native update discovery (this repo’s feed)
   description.xml → <update-information>
     → https://marinamoji.github.io/plugin/MarinaMojiKaeriten.update.xml
       → versioned GitHub Release asset MarinaMojiKaeriten.oxt

C. Download + install of that update
   LibreOffice fetches the feed, compares versions, downloads the .oxt URL,
   and asks the user to confirm (then usually restart Writer)
```

- Listing on the Extensions website **does not** automatically configure (A)→(B).
- Our `<update-information>` URL is what makes (B) work for any install that includes that hook (marketplace or sideload).
- Historical note: the Extensions website itself has **not** been a reliable update oracle; maintainers who want Check for Updates working host their own feed ([mailing-list confirmation](https://lists.freedesktop.org/archives/libreoffice/2014-December/065451.html)). Treat that as observed convention; re-verify if TDF documents a change.

Official starting points:

- [Using this site as an extension maintainer](https://extensions.libreoffice.org/en/home/using-this-site-as-an-extension-maintainer)
- [Extension development (TDF wiki)](https://wiki.documentfoundation.org/Development/Extension_Development)
- [DevGuide: Extensions](https://wiki.documentfoundation.org/Documentation/DevGuide/Extensions) (and the OpenOffice DevGuide pages for `description.xml` / update XML)

---

## Stable identifiers (do not change)

| Field | Value | Why |
|-------|--------|-----|
| **Extension identifier** | `org.marinaMoji.kaeriten` | LibreOffice treats a new id as a *different* extension |
| **Display name** | `marinaMoji Kaeriten` | Brand + feature |
| **Slogan** | Make room for character | Store / description copy |
| **Platform** | `all` | Pure Python/UNO — no native binaries |
| **Minimum LibreOffice** | `6.4` | Declared in `description.xml` and the update feed |
| **Update feed URL** | `https://marinamoji.github.io/plugin/MarinaMojiKaeriten.update.xml` | Stable; do not rotate casually |
| **License** | GPL-3.0-only | Bundled as `registration/license_en.txt` |

Host version (`description.xml` → `<version>`) is **independent** of the IME, ONLYOFFICE, Word, and the umbrella tag `plugins-v*`.

---

## What is already in good shape

- Pure Python + UNO (Windows / macOS / Linux same `.oxt`)
- ProtocolHandler toolbar in Writer
- Offline formatting (no runtime network / telemetry)
- `<update-information>` pointing at our GitHub Pages feed
- Build: `libreoffice/build.sh` → `dist/MarinaMojiKaeriten.oxt`
- Validation: `libreoffice/validate-extension.sh`
- LO-only CI: `.github/workflows/release-libreoffice.yml` (`libreoffice-v*` tags)
- Umbrella CI still ships the `.oxt` on `plugins-v*` tags

---

## Compliance checklist

### Documented / package requirements

| Requirement | Status |
|-------------|--------|
| `description.xml` + `META-INF/manifest.xml` | Required — present |
| Stable `identifier` | Required — `org.marinaMoji.kaeriten` |
| Semver-like `version` (`x.y.z`) | Required — authoritative in `description.xml` |
| `platform` / LO minimal version | Present (`all`, `6.4`) |
| License text via `registration/simple-license` | Present (GPL-3.0) |
| Extension Manager `icon` (≈42×42 PNG) | Present (`images/extension_icon.png`) |
| Localized short descriptions | EN / FR / JA in `description/` |
| `update-information` HTTPS URL | Present (GitHub Pages) |
| No platform-specific binaries | Yes |

### Still needs a human

| Item | Why |
|------|-----|
| **TDF SSO account** | Create at https://user.documentfoundation.org — you log in at https://extensions.libreoffice.org/admin |
| **Marketplace screenshots** | Optional but strongly recommended; capture Writer + marinaMoji toolbar + a rendered paragraph (EN, optionally FR/JA UI) |
| **Project logo upload** | Same square logo as Extension Manager icon is fine; approve which file |
| **Moderator review** | Initial listing waits for a moderator after you save a publishable entry (`.oxt` present). You may **not** get an email — check the admin UI |
| **Subsequent site releases** | Manual “Add Extension Release” in the admin UI (no supported public upload API for automation) |
| **Real LibreOffice QA** | Install / update / uninstall on Windows, macOS, Linux (see manual test plan below) |
| **Authorize Pages feed deploy** | Pushing `pages/MarinaMojiKaeriten.update.xml` to `main` goes live |

Validate anytime:

```bash
cd plugin/libreoffice
./build.sh
./validate-extension.sh
python3 tests/test_parser.py
python3 tests/test_export.py
```

---

## How the update feed works

1. Every built `.oxt` ships `description.xml` with:

   ```xml
   <update-information>
     <src xlink:href="https://marinamoji.github.io/plugin/MarinaMojiKaeriten.update.xml"/>
   </update-information>
   ```

2. That URL is a static file in [pages/MarinaMojiKaeriten.update.xml](../pages/MarinaMojiKaeriten.update.xml), deployed by the Word/Pages workflow when `pages/**` changes on `main`.

3. The feed advertises:
   - same `identifier`
   - newer `<version>`
   - HTTPS `update-download` pointing at a **versioned** GitHub Release asset  
     `…/releases/download/<tag>/MarinaMojiKaeriten.oxt`  
     (not `/latest/`, so the advertised file is reproducible)

4. User path: **Tools → Extension Manager → Check for Updates** (wording varies by language). LibreOffice prompts; a restart of Writer is typically required.

5. Marketplace-installed copies that include our `update-information` can use this feed. Do **not** assume the Extensions website rewrites or hosts an equivalent feed for us.

### Bootstrap caveat

Older installs **without** `update-information` cannot discover the feed until the user installs **once** from a package that includes it (then Check for Updates works).

### Mac caveat

Online update installs the `.oxt` only. On LibreOffice 26.x macOS, if the toolbar dies after an update, run the Mac `.dmg` installer (macro copy). See [UPDATE_LEFTOVERS.md](UPDATE_LEFTOVERS.md).

### Incorrect feed / rollback

1. Fix `pages/MarinaMojiKaeriten.update.xml` (version + download URL) on `main`, or re-run the LO release workflow with `publish_update_feed=true`.
2. Prefer pointing the feed at an older **existing** Release asset rather than deleting GitHub Release files.
3. Do not reuse the same `<version>` for different package bytes — bump `description.xml` and ship a new tag.

---

## Versioning and release lines

| Line | Tag / field | Builds |
|------|-------------|--------|
| LibreOffice only | `libreoffice-v0.3.10` (= `description.xml` version) | `.oxt` (+ Mac DMG on macOS runners) |
| All office plugins | `plugins-v0.0.3` | LO + ONLYOFFICE + Word (existing workflow) |
| IME | separate `marinaMoji/marinaMoji` releases | not this repo |

Authoritative LO version: **`libreoffice/marinamoji_kaeriten/description.xml`**.  
`packaging/sync-version-channel.sh` (umbrella release) and the LO-only workflow both derive the feed from that value.

---

## Automation vs manual

| Step | Automated? |
|------|------------|
| Build `.oxt`, validate ZIP/XML/id/version | Yes — `validate-extension.sh` + LO release workflow |
| Unit tests (parser/export) | Yes — in `build-libreoffice-release.sh` |
| Attach assets to GitHub Release | Yes — on `libreoffice-v*` / `plugins-v*` |
| Generate reviewable update XML | Yes — workflow artifact + Release asset |
| Deploy update XML to GitHub Pages | Yes **after** Release, when authorized (tag push for LO-only; umbrella release always syncs) |
| Upload new version to extensions.libreoffice.org | **No** — no supported public API; use the admin UI |
| Moderator approval | **Manual** (TDF) |
| Real Writer install / update clicks | **Manual** |

Do **not** automate the Extensions website via scraping or stored browser passwords.

---

## Initial marketplace submission

1. Finish compliance checklist; run `./validate-extension.sh` and ship a GitHub Release whose `.oxt` you are willing to list (e.g. `libreoffice-v0.3.10`).
2. Create a TDF SSO account → sign in at https://extensions.libreoffice.org/admin.
3. **Add Extension** in **English** first (fallback language).
4. Suggested metadata (edit freely before submit):

   | Field | Suggestion |
   |-------|------------|
   | Title | marinaMoji Kaeriten |
   | Summary | Format Unicode kaeriten (Kanbun marks) in Writer — Make room for character |
   | Description | Use `description/desc_en.txt` (expand with install notes if useful) |
   | Homepage | https://github.com/marinaMoji/plugin |
   | Source repository | https://github.com/marinaMoji/plugin |
   | Tags | Writer, CJK, Japanese, Chinese, education, typography (pick what the form allows) |
   | License | GPL-3.0 |

5. Save/create the entry, then **Add Extension Release** and upload `MarinaMojiKaeriten.oxt` (or link the GitHub Release asset if the form allows a download URL — prefer uploading the exact bytes you validated).
6. Add FR/JA translations of title/summary/description when ready (language dropdown in admin).
7. Optional: logo + screenshots.
8. Leave the entry in a publishable state (`.oxt` present). Wait for moderator publication; check the admin UI rather than email.
9. Confirm the listed package’s `description.xml` still contains our `update-information` URL (so Check for Updates keeps using our feed).

**Rejected / changes requested:** fix the package in this repo, bump version, release again, upload the new release on the site, reply in the Extensions community forum if needed: https://community.documentfoundation.org/c/extensions/36

---

## Extension-only release (example)

### Ship `0.2.0` (illustrative)

1. Set `<version value="0.2.0"/>` in `description.xml`.
2. Commit to `main` (does **not** by itself change the live update feed).
3. Tag and push: `git tag libreoffice-v0.2.0 && git push origin libreoffice-v0.2.0`  
   — or run **Release LibreOffice extension** with that tag.
4. CI builds/validates, creates GitHub Release `libreoffice-v0.2.0` with the `.oxt`, then (on tag push) commits the new feed to `main`.
5. Users with an older install that already has `update-information`: Check for Updates → offered `0.2.0` → download from the versioned Release URL → confirm → restart Writer.
6. **Manually** add release `0.2.0` on extensions.libreoffice.org if you want the marketplace page to show the new file (discovery), independent of (B)/(C).

### One month later: `0.2.1`

1. Bump to `0.2.1`, tag `libreoffice-v0.2.1`, same CI path.
2. Live feed now advertises `0.2.1` and `…/download/libreoffice-v0.2.1/MarinaMojiKaeriten.oxt`.
3. Historical `libreoffice-v0.2.0` assets remain on GitHub (do not overwrite).
4. Upload `0.2.1` on the Extensions website when you want the store page current.

---

## Manual test plan (when LibreOffice is available)

Distinguish:

| # | Behavior | How to verify |
|---|----------|----------------|
| A | New version visible on extensions.libreoffice.org | Open the public extension page after moderation |
| B | Native update detection | Install older `.oxt` with update-information → host a newer feed → Check for Updates shows the new version |
| C | Download + install from that URL | Accept the update; confirm Extension Manager shows the new version; toolbar still works |

Also test: fresh install, uninstall, reinstall, settings/documents preserved, feed URL unreachable (should fail gracefully / “no update”), install **without** marinaMoji IME (paste `說㆒㆑者`), Windows/macOS/Linux as available.

This maintainer environment may not have LibreOffice installed — treat Writer tests as **manual** until run on a real machine.

---

## Related documents

| Doc | Topic |
|-----|--------|
| [INSTALLERS_AND_UPDATES.md](INSTALLERS_AND_UPDATES.md) | Build/publish/update overview for all hosts |
| [UPDATE_LEFTOVERS.md](UPDATE_LEFTOVERS.md) | Bootstrap + Mac online-update caveats |
| [DISTRIBUTION.md](DISTRIBUTION.md) | GitHub Releases + website distribution |
| [libreoffice/README.md](../libreoffice/README.md) | Developer install / toolbar |
| [ONLYOFFICE_MARKETPLACE.md](ONLYOFFICE_MARKETPLACE.md) | Sibling marketplace guide (different process) |
