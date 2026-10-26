# Project status (June 2026)

Single source of truth for **where the three office plugins are** before self-hosted publishing.

**Next gate:** pre-publish QA on each host (see checklists below). **Not yet:** public GitHub/website release.

**Update channel (Oct 2026):** shared `version.json` + LibreOffice update feed on GitHub Pages; Word task-pane notice. Leftovers (ONLYOFFICE, Mac LO online-update verify, Windows Word QA): [UPDATE_LEFTOVERS.md](UPDATE_LEFTOVERS.md).

---

## Summary

| Host | Implementation | Default renderer | User export | Publish |
|------|----------------|------------------|-------------|---------|
| **LibreOffice** | ✅ feature-complete | SVG **inline image** (`libreoffice_primary: inline_image`) | **Copy plain** Unicode only | Package + update feed ready for `libreoffice-v0.3.10`; Extensions site listing optional later ([LIBREOFFICE_MARKETPLACE.md](LIBREOFFICE_MARKETPLACE.md)) |
| **Word** | ✅ feature-complete | **Inline picture** (`word_primary: inline_picture`) | **Copy plain** only | Mac QA passed (Apple Silicon 2026-08-26; Intel 2026-10-19). Windows / Word-on-the-web QA remain. Marketplace prep: [WORD_APPSOURCE.md](WORD_APPSOURCE.md) |
| **ONLYOFFICE** | ✅ feature-complete | **Inline image** (`onlyoffice_primary: inline_image`) | **Copy plain** only | Blocked on QA; marketplace prep started ([ONLYOFFICE_MARKETPLACE.md](ONLYOFFICE_MARKETPLACE.md)) |

All three support **Render** (formats new marks and smart-refreshes existing views), **Unrender**, and **Copy plain text** (canonical `說㆒㆑者`). Word and ONLYOFFICE expose a single **Render** button; LibreOffice menu **Refresh rendering** is an alias for **Format kaeriten**.

**Removed from v1:** **Copy TEI** and **Copy LaTeX**. There is no single agreed standard for encoding kanbun kaeriten in TEI XML or LaTeX across projects; shipping our own dialect would confuse more than help. **Canonical interchange = visible Unicode** (+ optional plain-text copy). See [ARCHITECTURE.md](ARCHITECTURE.md#export).

---

## LibreOffice

| | |
|---|---|
| **Vertical text** | Page-style toggle; kaeriten on left; compound image stacks |
| **Compound marks** | Painted SVG with `compound_touch` |
| **Daily use** | Recommended primary host after QA |

**Pre-publish QA:** [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md) Phase 1.

---

## Word

| | |
|---|---|
| **Mac renderer** | Inline PNG (canvas), not content controls / OOXML boxes |
| **Composed characters** | **Unreleased:** clipboard SVG from marinaMoji character composer → `XmlSvg` insert ([WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md); [word/CHANGELOG.md](../word/CHANGELOG.md)) |
| **Dev workflow** | `npm run serve` + `./install-mac.sh` (localhost) — developers only |
| **End users / testers** | GitHub Pages: `https://marinamoji.github.io/plugin/word/` — use `./install-mac-production.sh` |
| **Update notice** | Task pane fetches `https://marinamoji.github.io/plugin/version.json` after Ready |

**Pre-publish QA:** Mac passed on Apple Silicon (2026-08-26) and Intel (2026-10-19) — see [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) section B. Windows not yet run. Then [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md) Phase 3.

Word is **pre-release** for a broad public announce, but **Mac desktop is QA-green** (Intel + Apple Silicon): hosting is live on GitHub Pages; update notice shipped. Remaining gates before claiming Windows / web support: Windows QA and Word-on-the-web QA. Microsoft Marketplace (AppSource) prep is under [WORD_APPSOURCE.md](WORD_APPSOURCE.md) and `packaging/release/marketplace-word/` (deferred; not required for self-host Mac distribution). `MARINAMOJI_INCLUDE_WORD=1` is already the release default.

---

## ONLYOFFICE

| | |
|---|---|
| **Status** | Same command set as LO/Word; inline images with metadata; controls fallback |
| **Limitation** | Paste from LO does not keep frames — Unicode source only |

**Pre-publish QA:** [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md) Phase 2.

---

## Export policy (v1)

| Export | Ship? | Why |
|--------|-------|-----|
| **Copy plain text** | ✅ Yes | Canonical `說㆒㆑者`; works everywhere |
| **Copy TEI** | ❌ No | No one TEI encoding for kaeriten; project-specific XML misleads |
| **Copy LaTeX** | ❌ No | Many LaTeX packages (`kunten2e`, `sfkanbun`, …); no single target |

`export_core.py` / `exportCore.js` still contain TEI/LaTeX helpers for **developer experiments**; they are not exposed in toolbars or documented for end users.

---

## Publishing

When QA passes: [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md).

Rollout order: **LibreOffice** → **ONLYOFFICE** → **Word** (Word hosting is on GitHub Pages; enable in default release after QA).
