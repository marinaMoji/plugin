# Other hosts: reflections on expanding beyond LO / Word / OnlyOffice

Planning notes (June 2026). Not a commitment to build anything listed here.

**Context:** marinaMoji already has kaeriten renderers for **LibreOffice**, **Microsoft Word**, and **ONLYOFFICE**. Colleagues sometimes ask whether we should add **Google Docs**, **Pages**, or other word processors. This document records how we think about that question.

**Related:** [ARCHITECTURE.md](ARCHITECTURE.md) (source vs view), [BACKGROUND.md](BACKGROUND.md) (prior art), [ONLYOFFICE.md](ONLYOFFICE.md) (third host today), [ROADMAP.md](ROADMAP.md) (what we are building now).

---

## What our plugins actually do

The stack splits two jobs:

1. **marinaMoji IME** — commits canonical Unicode (`說㆒㆑者`).
2. **Office plugins** — turn that string into **print-oriented inline views** (compound stacks, placement beside kanji, vertical tuning on LibreOffice).

Collaborators **without** the plugin can still use the **Unicode string**; the plugin is for **page-setting and PDFs**, not for preserving meaning. See [CONVENTIONS.md](CONVENTIONS.md#collaboration).

So the question is usually not “which word processors exist?” but **“where do users need rendering, not just typing?”**

| Need | Tool |
|------|------|
| Fast keyboard input of marks | marinaMoji IME |
| Interchange, git, XML/LaTeX prep | Plain Unicode in any editor |
| Print-quality layout in a word processor | LO / Word / OnlyOffice plugin |

---

## What the current three hosts cover

| Host | Role in v1 | Distinctive strength |
|------|------------|----------------------|
| **LibreOffice** | Recommended daily driver after QA | Real **縦書き**; inline SVG renderer; open extension model |
| **Microsoft Word** | Desktop + (eventually) web | Familiar in universities; inline-picture renderer; Office.js add-in |
| **ONLYOFFICE** | Experimental parity | Word-like UI; sidebar plugin; **no** LO frame paste fidelity |

Rollout order and QA gates: [STATUS.md](STATUS.md), [SELF_HOSTED_PUBLISHING_PLAN.md](SELF_HOSTED_PUBLISHING_PLAN.md).

Until those three pass pre-publish QA, **new hosts are a distraction** unless a concrete user cohort blocks on one environment.

---

## Google Docs

### Short answer

**Not a near-term priority** for a kaeriten renderer, given our architecture and audience.

### Why

**1. Vertical text (縦書き).** Kanbun page layout often assumes vertical writing. LibreOffice is the only plugin host where we invest in 縦書き (including page-orientation toggles). ONLYOFFICE already lacks vertical mode. **Google Docs has no real vertical-text page mode.** A Docs add-on could render horizontal kaeriten, but on the weakest host for classical Japanese typography.

**2. API limits.** The Word add-in inserts **inline pictures** with careful positioning after months of experimentation ([WORD_FINDINGS.md](WORD_FINDINGS.md)). Google Docs add-ons (Apps Script / Workspace Add-ons) are more constrained: images and text runs, but not LibreOffice-style “frame anchored as character” or the layout control we fought for in Word. We would likely land near **ONLYOFFICE content controls** — fine for drafts, weak for serious print layout.

**3. Unicode-only workflow already works.** In Google Docs, a marinaMoji user can:

- Type `說㆒㆑者` with the IME (marks visible in the document),
- Collaborate on the **semantic layer** in the browser,
- Copy or export plain Unicode for downstream XML/LaTeX.

That matches [ARCHITECTURE.md](ARCHITECTURE.md). A Docs plugin would mainly add **pretty rendering inside the browser** — useful UX, but heavy engineering on a host that cannot do vertical layout well.

### When Google Docs *would* make sense

- Users routinely collaborate in the browser on **horizontal** drafts and complain that raw Unicode marks look wrong on screen (even though the data is correct).
- We explicitly scope a **“display only”** renderer, not print parity.
- Vertical layout is out of scope for that persona.

Treat as **Phase 5+** or “someday,” not a gap in the core story while LO/Word/OnlyOffice QA is open.

---

## Other word processors and editors

Grouped by how much they matter for marinaMoji’s audience (humanities scholars, thesis work, print-oriented kanbun).

### Tier A — extensions of what we already have

| Host | Assessment |
|------|------------|
| **Word on the web (Word Online)** | Same Office.js add-in family as desktop Word, with limitations. **Extending QA and hosting** to Word Online may reach cloud collaborators **without** a new platform. Likely higher ROI than a Google Docs renderer. |
| **Apache OpenOffice** | Already noted on [ROADMAP.md](ROADMAP.md) as “OpenOffice QA.” The LibreOffice `.oxt` may work with little extra work — smoke test, not a new codebase. |
| **Collabora Online / Nextcloud Office** | LibreOffice in the browser, but **extensions usually do not run** in the online build. Users get Unicode source only; same story as Docs for rendering. |

### Tier B — real products, niche or costly

| Host | Assessment |
|------|------------|
| **Apple Pages** | No add-in API comparable to Word. Scripting/automation only; small share for Japanese kanbun in DH workflows. |
| **WPS Office** | Large in some markets; has an extension model, but another full renderer to maintain. |
| **Zoho Writer** | Cloud-first; layout APIs similar to Google Docs. |
| **Hancom Office (한글)** | Korea-focused; unlikely priority for kanbun. |

### Tier C — covered by a different strategy (not “another word processor plugin”)

| Tool | Strategy |
|------|----------|
| **LaTeX / Overleaf** | Publication path from Unicode source ([BACKGROUND.md](BACKGROUND.md)); not duplicated inside WYSIWYG. A **converter** (Unicode → `kunten2e` / project markup) may beat another in-editor renderer. |
| **TEI/XML editors (oXygen, etc.)** | Unicode source + regex; no inline-image layout needed. |
| **Markdown / HTML / RTFD** | Preview and export path, not a host plugin. Markdown → HTML/CSS is promising; Apple RTFD is Mac-local and experimental. See [MARKDOWN_AND_RTF.md](MARKDOWN_AND_RTF.md). |
| **Plain text / VS Code / Obsidian** | IME output is already correct; rendering optional. |
| **一太郎 (Ichitaro)** | JustSystems’ **文字パレット「漢文」** — integrated kanbun palette in a proprietary word processor ([SOURCES.md](SOURCES.md)). Partnership or export/import territory, not “clone our LO extension.” |
| **漢文エディタ** | Own tag syntax (`[レ]` etc.) and Excel-centric workflow — different ecosystem; optional **import** is on the roadmap, not a host plugin. |

---

## Decision matrix (persona × host)

Use this when prioritising after v1 ships.

| Persona | Primary host | Needs rendered kaeriten? | Needs 縦書き? | Suggested path |
|---------|--------------|--------------------------|---------------|----------------|
| Thesis student (print PDF) | LibreOffice | Yes | Often | LO plugin + marinaMoji |
| Committee / co-author (track changes) | Word desktop | Yes | Sometimes | Word add-in |
| Lab on Word-compatible stack | ONLYOFFICE | Maybe | Rare | Unicode + optional plugin |
| Remote collaborators (browser) | Google Docs / Zoho | Rarely | No | **Unicode in Docs**; PDF export from LO for “pretty” |
| Remote collaborators (Microsoft shop) | Word Online | Maybe | Sometimes | **Word add-in QA on web** |
| Publication / book | LaTeX | N/A (TeX layout) | Yes | Unicode source → downstream converter |
| Corpus / encoding | oXygen, gedit | No | N/A | IME only |

---

## Practical recommendations

### Now (through beta / v1 release)

1. **Finish and ship LO → OnlyOffice → Word** ([STATUS.md](STATUS.md)).
2. Do **not** start a Google Docs renderer in parallel.
3. Document for users: **Unicode is the interchange format**; plugins are optional layout.

### Next (after v1 QA)

| Priority | Item | Rationale |
|----------|------|-----------|
| High | **Word Online** support / QA | Reuse existing add-in; cloud drafts |
| Medium | **OpenOffice** smoke test | Reuse `.oxt` |
| Medium | **LaTeX / export tooling** from Unicode | Publication path; not a new WYSIWYG host |
| Low | **漢文エディタ** `[レ]` import | Roadmap item; different markup |
| Low | Google Docs “display” add-on | Only if user interviews show browser pretty-print pain |
| Defer | Pages, WPS, Zoho, Hancom | Cost vs audience |

### Optional collaboration pattern (no new host)

- Author edits **Unicode source** (any editor + marinaMoji).
- **Render in LibreOffice** for PDF handout or print.
- Collaborators comment on PDF or on Unicode in Google Docs — without a Docs plugin.

---

## Questions to ask before any new host

1. Do users need **browser collaboration with rendered kaeriten**, or is **Unicode in the cloud** enough?
2. Do they need **縦書き** in that environment? (If yes, Google Docs and most web editors are the wrong host.)
3. Would **Word Online** + the existing add-in solve “shared draft in the cloud” more cheaply than a new platform?
4. Is the ask really **input** (IME / kanbun mode) rather than **layout** (plugin)?

---

## Changelog

| Date | Note |
|------|------|
| 2026-06 | Initial write-up from architecture review and host survey (LO / Word / OnlyOffice / Google Docs / others). |
