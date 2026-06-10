# Project status (June 2026)

Single source of truth for **where the three office plugins are** before self-hosted publishing.

**Next gate:** pre-publish QA on each host (see checklists below). **Not yet:** public GitHub/website release.

---

## Summary

| Host | Implementation | Default renderer | User export | Publish |
|------|----------------|------------------|-------------|---------|
| **LibreOffice** | ✅ feature-complete | SVG **inline image** (`libreoffice_primary: inline_image`) | **Copy plain** Unicode only | Blocked on QA |
| **Word** | ✅ feature-complete | **Inline picture** (`word_primary: inline_picture`) | **Copy plain** only | Blocked on QA (hosting live on GitHub Pages) |
| **ONLYOFFICE** | ✅ feature-complete | **Inline image** (`onlyoffice_primary: inline_image`) | **Copy plain** only | Blocked on QA |

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
| **Dev workflow** | `npm run serve` + `./install-mac.sh` (localhost) — developers only |
| **End users / testers** | GitHub Pages: `https://marinamoji.github.io/plugin/word/` — use `./install-mac-production.sh` |

**Pre-publish QA:** [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) section B, then [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md) Phase 3.

Word is **pre-release**: hosting is live on GitHub Pages; **QA** is the remaining gate before public GitHub/website release.

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
