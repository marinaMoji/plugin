# GitHub Pages — Word add-in hosting

Host the Word add-in static files on **GitHub Pages** so end users load the task pane over HTTPS without a local dev server.

**Live base URL (this repo):**

```text
https://marinamoji.github.io/plugin/word
```

Word loads `taskpane.html`, `commands.html`, and bundled JS from that path every session.

---

## One-time GitHub setup

**Required.** Without this step the deploy job fails with `404 Not Found`.

1. Open **github.com/marinaMoji/plugin** → **Settings** → **Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions** (not “Deploy from a branch”).
3. Merge or push the workflow file `.github/workflows/word-pages.yml` to `main`.

Or from a machine with `gh` CLI access to the repo:

```bash
gh api -X POST repos/marinaMoji/plugin/pages -f build_type=workflow
```

4. **Actions** → **Word add-in — GitHub Pages** → **Run workflow** (or push to `main`).
5. Pages should show: `https://marinamoji.github.io/plugin/`

Verify in a browser:

- `https://marinamoji.github.io/plugin/word/taskpane.html`
- `https://marinamoji.github.io/plugin/marinamoji-kaeriten-word.xml`

---

## What the workflow does

On push to `main` (when `word/`, `mapping.json`, or `pages/` change) or on manual **Run workflow**:

1. `npm ci && npm run build && npm test` in `word/`
2. Copies `word/dist/` → site `word/`
3. Copies `pages/index.html` → site root
4. Writes production `marinamoji-kaeriten-word.xml` with URLs pointing at GitHub Pages
5. Deploys via **GitHub Pages** (official `deploy-pages` action)

Download the manifest from the latest workflow run (**Artifacts** → `marinamoji-kaeriten-word-manifest`) or from the live URL above.

---

## Local release build (same URL)

```bash
cp packaging/word-release.env.example packaging/word-release.env
# Set:
# MARINAMOJI_PLUGIN_BASE=https://marinamoji.github.io/plugin/word
./packaging/build-word-release.sh
```

Produces `packaging/release/word-dist.zip`, `marinamoji-kaeriten-word.xml`, and Mac `.dmg` (on macOS).

---

## Sideload for testing (production URL)

**Mac:** install the production manifest (not `./install-mac.sh`, which is dev-only localhost):

```bash
cd plugin/word
./install-mac-production.sh
```

Or download and copy manually:

```bash
curl -fsSL -o ~/Library/Containers/com.microsoft.Word/Data/Documents/wef/marinamoji-kaeriten.xml \
  https://marinamoji.github.io/plugin/marinamoji-kaeriten-word.xml
```

Then **Cmd+Q Word**, reopen with a document, **Accueil → Kaeriten pane**. No `npm run serve`.

**Windows:** **Insertion** → **Compléments** → **Téléverser mon complément** →  
`https://marinaMoji.github.io/plugin/marinamoji-kaeriten-word.xml`  
(or download that file and upload it).

**Important:** quit Word (Cmd+Q), reopen with a document, then **Accueil → Kaeriten → Kaeriten pane**. No `npm run serve` required.

---

## Custom domain (optional)

If you later use `plugins.marinaMoji.org`, change `MARINAMOJI_PLUGIN_BASE` in:

- `.github/workflows/word-pages.yml` (`env.MARINAMOJI_PLUGIN_BASE`)
- `packaging/word-release.env`

Rebuild the manifest and redeploy. Users must reinstall or refresh the sideloaded manifest when the base URL changes.

---

## Related

- [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md) Phase 3
- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) — localhost dev (not for end users)
- [DISTRIBUTION.md](DISTRIBUTION.md)
