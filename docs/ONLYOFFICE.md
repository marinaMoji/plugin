# ONLYOFFICE and marinaMoji Kaeriten

A practical guide to **ONLYOFFICE** in the marinaMoji stack: how it fits the architecture, what works today, limits, and how it compares to LibreOffice and Word.

**Plugin code:** [onlyoffice/](../onlyoffice/)  
**Research / Word planning:** [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md)

---

## What is ONLYOFFICE?

**ONLYOFFICE** is an office suite (word processor, spreadsheet, presentation) that can run as:

| Form | Typical user |
|------|----------------|
| **Desktop Editors** | Free download for Mac / Windows / Linux |
| **Document Server** | Self-hosted (often **Docker**) for browser editing |
| **Cloud** | onlyoffice.com hosted workspaces |

For marinaMoji, the relevant piece is **ONLYOFFICE Document Editor** (Writer) and its **plugin** system — small HTML/JavaScript extensions similar in spirit to Office add-ins, but loaded from the editor’s **plugin folder** (no separate HTTPS dev server required for basic use).

Official docs: [Plugin and macros overview](https://api.onlyoffice.com/docs/plugin-and-macros/get-started/overview/).

---

## Where ONLYOFFICE fits in marinaMoji

### Shared architecture (all hosts)

```text
marinaMoji IME  →  說㆒㆑者     (canonical Unicode in the document)
Plugin          →  small stacked views (host-specific)
```

- **Meaning** lives in visible Unicode — not in hidden cross-app metadata.
- **Views** are disposable: Unrender → edit marks → Render again.
- **[mapping.json](../mapping.json)** defines display glyphs and stack order.

See [ARCHITECTURE.md](ARCHITECTURE.md).

### What ONLYOFFICE is *not* in v1

| Expectation | Reality |
|-------------|---------|
| Open LibreOffice `.odt` and keep frames | **No** — LO frames are lost on paste |
| Same boxes as Word textboxes | **No** — separate renderer |
| One plugin install for all colleagues without IT | Depends on Desktop vs Server deployment |

From interoperability tests in [WORD_FINDINGS.md](WORD_FINDINGS.md):

- Copy **LibreOffice → ONLYOFFICE**: frame objects **do not** survive.
- Copy **plain Unicode** (`說㆒㆑者`): **yes** — that is the portable format.

---

## marinaMoji Kaeriten plugin (v0.1)

### What we built

| Piece | Description |
|-------|-------------|
| **Sidebar UI** | Render, Unrender, Refresh, Copy plain / TEI / LaTeX |
| **Renderer** | Inline content controls (`Api.CreateInlineLvlSdt`) with tag `MARINAMOJI:source=…` |
| **Export** | Same logic as Word / LO (`exportCore.js` port) |

Install and daily use: **[onlyoffice/README.md](../onlyoffice/README.md)**.

### Status

| | |
|---|---|
| **Code** | Scaffold complete (May 2026) |
| **QA on real ONLYOFFICE** | **Not done yet** on your machine |
| **Recommended for daily work** | **LibreOffice** until QA passes |

---

## Install overview

### Desktop (simplest for one user)

```bash
cd plugin/onlyoffice
./install-mac.sh
```

Copy the plugin into **`data/sdkjs-plugins/{GUID}/`** — not `plugins/marinamoji-kaeriten/`. See [onlyoffice/README.md](../onlyoffice/README.md).

Restart ONLYOFFICE Writer → **Plugins** → **marinaMoji Kaeriten**.

### Document Server (team / browser)

1. Mount or copy the plugin into the image’s `sdkjs-plugins/` path.
2. Enable plugins in editor configuration.
3. Users see the same sidebar inside the browser editor.

Paths vary by Docker image — see ONLYOFFICE deployment docs for your image version.

---

## How the plugin works (technical)

### Plugin model vs Word add-in

| | Word add-in | ONLYOFFICE plugin |
|---|-------------|-------------------|
| **Registration** | `manifest.xml` + sideload `wef` | `config.json` in plugin folder |
| **UI** | Task pane URL (HTTPS server) | `index.html` loaded locally |
| **Document API** | `Word.run` / Office.js | `Asc.plugin.callCommand` + Document Builder `Api.*` |
| **Dev server** | **Required** (`npm run serve`) | **Not required** for normal use |
| **Trust / certs** | Major pain on Mac Word | Usually none for local plugins |

### Render pipeline (simplified)

1. **Scan** document paragraphs for Kanbun mark clusters (`說` + `㆒㆑`).
2. **Rebuild** each affected paragraph: plain runs + inline controls with stacked glyphs.
3. **Unrender** finds controls by tag prefix `MARINAMOJI:source=` and restores Unicode marks.
4. **Refresh** updates glyph text inside controls from `mapping.json`.

### v0.1 limitations (honest list)

- **Compound stacks:** default `"stack"` uses `SetPosition` + tight spacing inside the inline control (no `AddLineBreak` — that escapes and breaks the line before the block). Tune with `"stack_step_hps"` (half-points; `0` = auto). Fallbacks: `"soft_break"` or `"horizontal"`.
- **Unrender:** replaces the control in place (no `Delete()`) so display glyphs are not spilled to line start.
- **Export (TEI/LaTeX):** reads canonical Unicode from control tags while views are shown (no Unrender required).
- **API names** may differ slightly between ONLYOFFICE versions (`GetParentParagraph`, etc.).
- **No import** of Word content controls or LO frames from other apps.

---

## Comparison: LibreOffice vs Word vs ONLYOFFICE

| | LibreOffice | Word add-in | ONLYOFFICE plugin |
|---|-------------|-------------|-------------------|
| **Render primitive** | Anchored **frame** | **Content control** (v0.1) | Inline **content control** |
| **Visual match to print** | Best in your tests | Good | TBD (QA) |
| **Install difficulty** | Extension Manager `.oxt` | High (HTTPS + serve) | Medium (copy folder) |
| **Mac daily use** | ✅ Working | 🔧 In progress | ⏳ Not QA’d |
| **Paste from LO** | — | Views lost | Views lost |
| **Canonical Unicode** | ✅ | ✅ | ✅ |
| **TEI / LaTeX export** | ✅ | ✅ (code) | ✅ (code) |

---

## When to choose ONLYOFFICE

**Good fit if you:**

- Already use **ONLYOFFICE Desktop** or **Document Server** for collaboration.
- Want a **sidebar** tool without running `npm run serve` like Word.
- Accept **re-rendering from source** when moving documents between LO and ONLYOFFICE.

**Poor fit if you:**

- Need **perfect visual parity** with LibreOffice frames in the same file without re-running Render.
- Rely on **Word-only** features (native `.docx` track changes workflow with Word Mac add-in).
- Need **selection-only** render in v0.1 (not implemented yet in ONLYOFFICE plugin).

---

## Workflow recommendations

### Solo scholar (your situation)

1. **Author in LibreOffice** with marinaMoji + Kaeriten extension.
2. **Archive / git** plain Unicode or `.odt` with source marks visible.
3. **Optional:** open copy in ONLYOFFICE or Word → **Render** there for a specific deliverable (PDF, collaborator).
4. **Export TEI/LaTeX** from whichever host has the tools working that day (LO is safest today).

### Document with collaborators

| Collaborator uses | You send |
|-------------------|----------|
| LibreOffice | `.odt` with Unicode source (or rendered, knowing views are LO-specific) |
| Word | `.docx` with Unicode source; they Render in Word if they install add-in |
| ONLYOFFICE | Same — Unicode source; they use plugin |

**Copy as plain text** (from any host) is the safest handoff.

---

## Relationship to Word plugin work

ONLYOFFICE and Word share:

- `mapping.json`
- Export rules (TEI, LaTeX)
- Tag convention `MARINAMOJI:source=…`
- “Edit source, not the view” UX

They differ in **deployment**:

- Word = ongoing **HTTPS + Office.js** investment on Mac.
- ONLYOFFICE = **copy plugin once**, fewer moving parts.

If Word Mac remains painful, ONLYOFFICE may be a **lower-friction** second target for browser/self-hosted workflows — but it does **not** remove the need for LO as the reference renderer.

---

## Roadmap hooks

From [ROADMAP.md](ROADMAP.md):

- [x] Plugin skeleton
- [ ] Install + QA (simple mark, compound, font refresh)
- [ ] Selection-scoped render (parity with LO/Word)
- [ ] Smarter export (read marks from control tags without manual Unrender)

---

## References

- [ONLYOFFICE plugin getting started](https://api.onlyoffice.com/docs/plugin-and-macros/get-started/overview/)
- [CreateInlineLvlSdt](https://api.onlyoffice.com/docs/office-api/usage-api/text-document-api/Api/Methods/CreateInlineLvlSdt/)
- [ARCHITECTURE.md](ARCHITECTURE.md) — source vs view
- [WORD_FINDINGS.md](WORD_FINDINGS.md) — paste / interoperability
- [onlyoffice/README.md](../onlyoffice/README.md) — install commands
