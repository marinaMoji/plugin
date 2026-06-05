# Project status (June 2026)

Single source of truth for **where the three office plugins are** before self-hosted publishing.

**Next gate:** pre-publish QA on each host (see checklists below). **Not yet:** public GitHub/website release.

---

## Summary

| Host | Implementation | Default renderer | User export | Publish |
|------|----------------|------------------|-------------|---------|
| **LibreOffice** | ✅ feature-complete | SVG **inline image** (`libreoffice_primary: inline_image`) | **Copy plain** Unicode only | Blocked on QA |
| **Word** | ✅ feature-complete | **Inline picture** (`word_primary: inline_picture`) | **Copy plain** only | Blocked on QA + hosting |
| **ONLYOFFICE** | ✅ feature-complete | Inline content controls | **Copy plain** only | Blocked on QA |

All three support **Render**, **Unrender**, **Refresh**, and **Copy plain text** (canonical `說㆒㆑者`).

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
| **Dev workflow** | `npm run serve` + sideload for developers only |
| **End users** | Hosted `dist/` on HTTPS — no local server |

**Pre-publish QA:** [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) section B, then [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md) Phase 3.

Word is **no longer parked** in the repo; it is **pre-release** pending QA and website hosting.

---

## ONLYOFFICE

| | |
|---|---|
| **Status** | Same command set as LO/Word; inline controls |
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

Rollout order: **LibreOffice** → **ONLYOFFICE** → **Word** (Word needs HTTPS hosting).
