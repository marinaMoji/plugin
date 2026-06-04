# Word plugin — research memo (May 2026)

Planning notes for **marinaMoji Kaeriten** on **Microsoft Word (Mac, French UI)**. Covers research briefs **#1, #2, #4, #6, #7**, plus **certification** and **macros vs Office.js**.

**Related:** [WORD_FINDINGS.md](WORD_FINDINGS.md) (conclusions), [WORD_ADDIN_ATTEMPTS.md](WORD_ADDIN_ATTEMPTS.md) (add-in chronicle), [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) (dev checklist), [ONLYOFFICE.md](ONLYOFFICE.md).

---

## Executive summary

| Question | Short answer |
|----------|----------------|
| **Do we need “certification” to develop?** | **No.** Self-signed HTTPS (mkcert or `office-addin-dev-certs`) is enough for sideloading on your Mac. |
| **Do we need certification to publish?** | **Only if** you list the add-in on **Microsoft Marketplace** (AppSource). That is a **Partner Center review**, not an Apple Developer certificate. |
| **Can simple Word macros do everything?** | **Not reliably on Mac.** VBA is limited, sandboxed, and a poor match for cross-platform marinaMoji. Macros might help a **Windows-only** fallback, not replace the add-in. |
| **Best render API for Mac v0.1?** | **Content controls** (current code) — supported, taggable, lockable. **Textboxes** match [WORD_FINDINGS.md](WORD_FINDINGS.md) visually but need `WordApiDesktop` + more layout work. |
| **Practical workflow today** | **LibreOffice** for editing; **Word add-in** when dev HTTPS + Office.js connect; treat Word as **optional** until QA passes. |

---

## 1. Word for Mac add-in — reality check

### What an Office add-in actually is

- A **web app** (HTML + JavaScript) loaded in a **sandboxed webview** inside Word.
- Your **manifest.xml** tells Word where to load the UI (`https://127.0.0.1:3000/...`).
- **Office.js** bridges the web page and the document (`Word.run`, `Office.onReady`).

Official overview: [Office Add-ins platform](https://learn.microsoft.com/en-us/office/dev/add-ins/overview/office-add-ins).

### Mac sideloading (what you are doing)

Microsoft’s documented flow:

1. Copy `manifest.xml` to  
   `~/Library/Containers/com.microsoft.Word/Data/Documents/wef/`
2. Restart Word, open a **document**.
3. Use **Home → Add-ins** (French: **Accueil → Compléments** / add-in picker).

Source: [Sideload Office Add-ins on Mac](https://learn.microsoft.com/en-us/office/dev/add-ins/testing/sideload-an-office-add-in-on-mac).

**There is no “Extension Manager”** on Mac Word like LibreOffice. **“Upload my add-in”** exists mainly on **Word on the web** and **Windows**, not the Mac desktop flow you have.

### HTTPS and certificates (development)

| Topic | Fact |
|-------|------|
| **HTTPS required?** | Strongly recommended; effectively required for web + Marketplace. |
| **Self-signed OK for dev?** | **Yes**, if the CA is **trusted on your Mac** (login keychain). |
| **Tools** | `office-addin-dev-certs`, or **mkcert** (what we use in `plugin/word/`). |
| **Apple Developer ID?** | **Not** for local sideloading. Used for Mac **apps**, not Office add-in dev servers. |

Source: [Requirements for running Office Add-ins](https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/requirements-for-running-office-add-ins).

### Mac-specific friction (what you hit)

| Issue | Cause | Mitigation |
|-------|--------|------------|
| **Blank task pane** | Word does not trust dev HTTPS | `mkcert -install`, `npm run serve`, Safari check `https://127.0.0.1:3000/taskpane.html` |
| **“Word did not connect”** | **Compléments** preview is not a full host; or server down | Open pane from **Accueil → Kaeriten → Kaeriten pane** with document open |
| **`Office.onReady` slow** | CDN blocked, cert errors, wrong context | Bundled `office.js`, hosted fallback, fix trust first |
| **Dev server must run** | Add-in is not bundled inside Word | Keep `npm run serve` open |
| **127.0.0.1 vs localhost** | Word/WebView treat them differently | Manifest uses **127.0.0.1** |

### Word Mac vs Windows (add-ins)

| | Mac | Windows |
|---|-----|---------|
| Sideload | `wef` folder | `wef` + often “Upload” / shared catalog |
| Debugging | Safari Web Inspector (if enabled) | Edge DevTools |
| Custom ribbon tab | Often **hidden** — use **Home** tab group | More predictable |
| Minimum Word | 15.18+ (very old baseline); use current M365 | Same API broadly |

### Minimum recommendation for your project

1. Treat **“doctor + serve + Accueil pane → Ready”** as the gate before any renderer work.
2. Do **not** judge the add-in from the **Compléments catalog preview** alone.
3. Prefer **Word from office.com** over Mac App Store if you need **Web Inspector** (`OfficeWebAddinDeveloperExtras`).

---

## 2. Content controls vs textboxes (renderer choice)

### What your experiments already concluded

[WORD_FINDINGS.md](WORD_FINDINGS.md): **anchored textboxes** are the best **visual** match for LibreOffice frames, but users must edit **source Unicode**, not the box.

The **current add-in** uses **content controls** because they are easier to tag (`MARINAMOJI:source=㆒㆑`), lock, and refresh via Office.js.

### API availability (Word Mac desktop)

| Approach | Office.js API | Mac Word | Fits kaeriten? |
|----------|---------------|----------|----------------|
| **Content controls** | `range.insertContentControl()`, `cc.tag`, `cc.cannotEdit` | **Yes** (Word API 1.1+) | **Good v0.1** — stacked lines inside CC |
| **Floating textboxes** | `paragraph.insertTextBox()` (documented as **floating**) | **Yes** — **`WordApiDesktop` 1.2+** | Implemented as optional Renderer B; **Mac QA poor** |
| **Inline text box** | `insertTextBox` + `shape.textWrap.type = inline` | **Yes** (same requirement set) | **Best next spike** — in-line with text; no `left`/`top` |
| **Inline picture** | `insertInlinePictureFromBase64` | Yes | **Wrong primitive** — images only, not stacked text |
| **Raw OOXML** | `paragraph.insertOoxml()` | Yes | **Fallback** if inline wrap fails; fragile |
| **Ruby / phonetic guide** | — | Yes but wrong typography | **Reject** |
| **Subscript only** | `font.subscript` | Yes | **Fallback** for simple レ |

Sources:

- [Word.ContentControl](https://learn.microsoft.com/en-us/javascript/api/word/word.contentcontrol)
- [WordApiDesktop 1.2](https://learn.microsoft.com/en-us/javascript/api/requirement-sets/word/word-api-desktop-1-2-requirement-set) (`insertTextBox`, shape wrap)
- [Word.ShapeTextWrapType](https://learn.microsoft.com/en-us/javascript/api/word/word.shapetextwraptype?view=word-js-preview) (`inline`)
- [Word.Paragraph.insertTextBox](https://learn.microsoft.com/en-us/javascript/api/word/word.paragraph?view=word-js-preview#word-word-paragraph-inserttextbox-method)

Always check support:

```javascript
Office.context.requirements.isSetSupported("WordApiDesktop", "1.2")
```

### Comparison for marinaMoji

| Criterion | Content controls | Floating text box (Renderer B) | Inline text box (Renderer C, planned) |
|-----------|------------------|--------------------------------|--------------------------------------|
| Match LO “as character” | Approximate (in-flow text) | **Poor** on Mac (float + nudges) | **Promising** per MS `textWrap.inline` |
| Tag / store source marks | **Easy** (`tag`) | `altTextDescription` | Same as B |
| Lock from editing | **Built-in** | Manual | Manual |
| Font size refresh | Rescale inner text | **Refresh** command | Same |
| Search `說` + `者` across mark | **Fails** when object between chars | Same (expected) | Same (expected) |
| Implementation cost | **Done** | Done but off by default | Small delta on `wordTextBox.js` |
| Word on the web | Supported | Desktop-oriented | Desktop-oriented |

### Recommendation

| Phase | Choice |
|-------|--------|
| **v0.1 (now)** | **Keep content controls** until Mac connection QA passes |
| **v0.2 (if Word matters)** | Spike **Renderer C:** `insertTextBox` + `textWrap.type = inline` on one cluster (`說㆒㆑`); compare to LO screenshot on Mac and Windows |
| **Do not** | Block v0.1 on textboxes; **do not** invest more in float + `Character` + `left`/`top` tuning without trying `inline` first |
| **Later** | `insertOoxml` (`wp:inline`) only if Renderer C fails |

---

## 4. Feature parity matrix

Legend: ✅ done / reliable · 🟡 partial · ❌ no · 🔧 dev only · ⏳ not QA’d

| Feature | LibreOffice extension | Word add-in v0.1.2 | ONLYOFFICE plugin v0.1 |
|---------|----------------------|--------------------|-------------------------|
| **Canonical source `說㆒㆑者`** | ✅ | ✅ (design) | ✅ (design) |
| **Render** | ✅ frames | 🔧 content controls | ⏳ inline CC |
| **Unrender** | ✅ | 🔧 | ⏳ |
| **Refresh** | ✅ | 🔧 | ⏳ |
| **Copy plain / TEI / LaTeX** | ✅ | 🔧 (export logic tested) | ⏳ |
| **Scope: selection** | ✅ | ✅ | ❌ (OO: whole doc scan) |
| **Scope: whole document** | ✅ | ✅ | ✅ |
| **Silent UI (no dialogs)** | ✅ | ✅ | ✅ |
| **Toolbar / ribbon** | ✅ marinaMoji bar | 🟡 Accueil → Kaeriten | ⏳ Plugins sidebar |
| **Install friction** | Extension Manager | High (HTTPS + serve) | Medium (copy plugin folder) |
| **Paste LO → host visuals** | — | ❌ | ❌ |
| **縦書き** | 🟡 manual QA pending | ⏳ | ⏳ |
| **Compound ㆒㆑** | ✅ | 🔧 (logic shared) | ⏳ |
| **Daily use ready** | **Yes** | **Not yet** | **Not yet** |

**Word MVP (definition of “done”):**

1. Accueil pane → **Ready**
2. Render / Unrender / Refresh on `說㆒㆑者`
3. Copy plain at minimum; TEI/LaTeX if export path stable

---

## 6. Alternatives — macros, VBA, and “do we need the add-in?”

### Can “simple macros” do everything?

**On your Mac, not as a full replacement.**

| Approach | What it is | Mac Word | Kaeriten fit |
|----------|------------|----------|--------------|
| **Office.js add-in** (current) | JS + HTTPS + manifest | ✅ supported | **Best cross-platform path** |
| **VBA macros** | `.docm` embedded code | 🟡 **limited** | Possible on Windows; fragile on Mac |
| **AppleScript** | macOS automation | 🟡 external | Awkward for in-document layout |
| **Word-Documents only** | Edit in LO, save `.docx` | ✅ | **Unicode source** travels; **views do not** |
| **Pandoc / external script** | Export pipeline | ✅ | Good for TEI/LaTeX; not WYSIWYG render |

### VBA on Mac — important limits

- Word for Mac runs VBA in a **sandbox** since Office 2016 — file access and cross-process behavior are restricted.
- **No macro recorder** on Mac.
- VBA dialect differs from Windows (VB5 vs VB6 gaps) — macros shared with Windows colleagues **break easily**.
- Your manual tests already used **shapes/textboxes**; VBA could create `Shapes.AddTextbox` with an **Anchor** range — but maintaining that macro set is **separate code** from LO Python and Word JS (triple maintenance).

Sources: [Office Add-ins overview (vs VBA)](https://learn.microsoft.com/en-us/office/dev/add-ins/overview/office-add-ins); general Mac Word VBA limitations are widely documented by Microsoft partners.

### What macros *could* still be useful for

| Use case | Verdict |
|----------|---------|
| **Personal Windows machine**, no Node, no HTTPS | Small VBA “format selection” macro **possible** |
| **Classroom / collaborators on Mac** | **Poor** — use LO or Word add-in |
| **TEI/LaTeX export only** | Python/`export_core.py` or LO buttons — **no Word needed** |
| **Subscript fallback** (レ only) | Simple VBA or character style — **not** compound stacks |

### Strategic options (ranked for a solo DH scholar)

1. **Primary: LibreOffice** — already works; same `mapping.json`.
2. **Continue Word add-in** only if Accueil pane connects reliably (environment, not architecture).
3. **Try ONLYOFFICE plugin** if you already run Document Server / Desktop — see [ONLYOFFICE.md](ONLYOFFICE.md).
4. **Defer VBA** unless you commit to **Windows-only** distribution as `.dotm`.
5. **Do not** pursue Microsoft Marketplace unless you want public distribution (see below).

---

## 7. Compléments / ribbon UX (French Word on Mac)

### Official vs French UI

| English (Microsoft docs) | French (your UI) |
|--------------------------|------------------|
| Home | **Accueil** |
| Add-ins | **Compléments** |
| Home → Add-ins → your add-in | **Accueil → Compléments** → marinaMoji Kaeriten |
| Custom ribbon group | **Accueil → Kaeriten** (our manifest uses `TabHome`) |

Microsoft’s Mac sideload doc says: **Home → Add-ins** → select add-in. That matches opening the add-in list; it does **not** guarantee a working **task pane** until the add-in is run **inside a document**.

### Three different UI surfaces

```text
┌─────────────────────────────────────────────────────────┐
│  A. Compléments list / “navigateur”                     │
│     Registers add-in; may show HTML preview             │
│     Office.js often NEVER connects → timeout message    │
├─────────────────────────────────────────────────────────┤
│  B. Accueil → Kaeriten → Kaeriten pane                  │
│     Real task pane — USE THIS for development           │
├─────────────────────────────────────────────────────────┤
│  C. Accueil → Kaeriten → Render / Unrender / …          │
│     Ribbon buttons (ExecuteFunction) — no pane needed   │
└─────────────────────────────────────────────────────────┘
```

### Custom tab vs Home group

Many Mac Word builds **hide custom top-level tabs**. Our manifest puts commands on **Accueil** (`OfficeTab idMso="TabHome"`) for that reason.

### Checklist for French UI testing

- [ ] Document open (not only add-in gallery)
- [ ] `npm run serve` running
- [ ] **Accueil → Kaeriten → Kaeriten pane** → “Ready”
- [ ] If ribbon missing: `./install-mac.sh`, Cmd+Q Word, reopen
- [ ] Optional: ribbon **Render** without opening pane

---

## Certification — what it is and what you need

### Development (you, now)

| Item | Required? |
|------|-----------|
| Microsoft Partner Center account | **No** |
| Commercial SSL certificate | **No** (mkcert / dev certs OK) |
| Apple Developer Program | **No** |
| Code signing the add-in bundle | **No** (there is no bundle — it’s a URL) |
| `office-addin-manifest validate` | **Helpful**, not mandatory |

### Publishing to Microsoft Marketplace (later, optional)

| Item | Required? |
|------|-----------|
| Partner Center **company** account | **Yes** |
| Hosted add-in on **public HTTPS** | **Yes** |
| Manifest validation + policy compliance | **Yes** |
| Microsoft **review** (≈ 3–5 business days) | **Yes** |
| Microsoft 365 **App Certification** program | **Optional** (trust badge for enterprises) |

Sources:

- [Publish Office Add-ins to Marketplace](https://learn.microsoft.com/en-us/office/dev/add-ins/publish/publish-office-add-ins-to-appsource)
- [Marketplace certification process](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/submit-to-appsource-via-partner-center)

**For marinaMoji as a research tool:** sideload + git distribution of `manifest.xml` is enough. Marketplace is only relevant if you want strangers to install from **Insert → Get Add-ins**.

### Distribution without Marketplace

We ship via **GitHub Releases** and our **website**, not AppSource. End users get **double-click installers**; add-in files are hosted on our domain with normal HTTPS (no mkcert). See **[DISTRIBUTION.md](DISTRIBUTION.md)** and **[INSTALL-MAC-GATEKEEPER.md](INSTALL-MAC-GATEKEEPER.md)**.

| Audience | Approach |
|----------|----------|
| **Yourself (dev)** | Sideload + `npm run serve` + mkcert |
| **New users** | Download `.oxt` / `.dmg` / zip; Right-click → Open if Gatekeeper warns |
| **Word users** | Production manifest → `https://your-site/word/` (no local server) |
| **University IT** | Optional: Centralized Deployment (M365 admin) |
| **Public store** | Deferred (Partner Center) |

---

## Suggested decision tree (next planning session)

```text
Can you get "Ready" in Accueil → Kaeriten pane?
├─ NO  → Fix HTTPS / serve / Word restart (WORD_ADDIN_DEV.md)
│        Consider pausing Word; use LO + optional ONLYOFFICE
└─ YES → Render 說㆒㆑者 works?
         ├─ NO  → Debug Word.run / content control code
         └─ YES → QA 縦書き + compound + export
                  └─ Layout good enough?
                     ├─ YES → Ship v0.1 Word; document workflow
                     └─ NO  → Try insertTextBox prototype (v0.2)
```

---

## References

- [Sideload on Mac](https://learn.microsoft.com/en-us/office/dev/add-ins/testing/sideload-an-office-add-in-on-mac)
- [Debug Office Add-ins on a Mac](https://learn.microsoft.com/en-us/office/dev/add-ins/testing/debug-office-add-ins-on-ipad-and-mac)
- [office-addin-dev-certs](https://www.npmjs.com/package/office-addin-dev-certs)
- [Word JavaScript API overview](https://learn.microsoft.com/en-us/office/dev/add-ins/reference/overview/word-add-ins-overview)
- [ONLYOFFICE plugin doc](ONLYOFFICE.md)
