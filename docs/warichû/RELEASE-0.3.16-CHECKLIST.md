# marinaMoji LibreOffice **0.3.16** — release validation (manual)

**Status:** Ready for your testing. **Do not publish** until you confirm this checklist.  
**Package:** `plugin/libreoffice/dist/MarinaMojiKaeriten.oxt` (built locally; `dist/` is gitignored — rebuild with `./build.sh` if missing).  
**Host tested in development:** LibreOffice Writer **26.8.0.3** (macOS).

---

## Install (macOS)

1. **Quit LibreOffice** completely (all Writer windows; check Dock).
2. Rebuild if needed:
   ```bash
   cd /Users/daniel/Code/marinaMoji/plugin/libreoffice
   ./build.sh
   ./validate-extension.sh
   ```
3. **Tools → Extension Manager** → select any older **marinaMoji Kaeriten** → **Remove** → close Manager → **quit Writer** → reopen Writer.
4. Extension Manager → **Add** → choose  
   `plugin/libreoffice/dist/MarinaMojiKaeriten.oxt`  
   → accept GPL → **restart Writer**.
5. Confirm version **0.3.16** in Extension Manager.
6. **View → Toolbars → marinaMoji**.
7. On LO **26.x**, if toolbar buttons do nothing, also run:
   ```bash
   cd /Users/daniel/Code/marinaMoji/plugin/libreoffice
   ./install.sh
   ```
   then quit and restart Writer again.

---

## Manual checklist — warichū

Use a new Writer document, Japanese language, Asian font (e.g. Hiragino Mincho ProN), 14 pt.

### A. Insert

| # | Step | Pass? |
|---|---|---|
| A1 | Type `本文割り注は、良いです。` | ☐ |
| A2 | Select **only** `割り注は、良いです。` (leave `本文` outside) | ☐ |
| A3 | Click **Apply warichū** | ☐ |
| A4 | Note paints as **two readable mini-lines** next to `本文` | ☐ |
| A5 | Selecting the **whole paragraph** then Apply → **refused** with a warning | ☐ |

### B. Remove with selection

| # | Step | Pass? |
|---|---|---|
| B1 | Select the entire warichū note | ☐ |
| B2 | **Remove warichū** | ☐ |
| B3 | Text returns to a **single line**; characters still `割り注は、良いです。` | ☐ |

### C. Remove with caret (0.3.16)

| # | Step | Pass? |
|---|---|---|
| C1 | Apply warichū again on the same note | ☐ |
| C2 | Click **inside** the annotation (collapsed caret; no selection) | ☐ |
| C3 | **Remove warichū** | ☐ |
| C4 | Whole annotation clears to one line (not just one character) | ☐ |

### D. Text preservation

| # | Step | Pass? |
|---|---|---|
| D1 | After apply/remove cycles, string is still exactly `割り注は、良いです。` | ☐ |
| D2 | Undo (⌘Z) restores prior state sensibly | ☐ |
| D3 | Ordinary typing / kaeriten toolbar still works in the same document | ☐ |

### E. Save / reopen ODT

| # | Step | Pass? |
|---|---|---|
| E1 | Apply warichū; **File → Save As** `.odt`; close | ☐ |
| E2 | Reopen; annotation still two lines | ☐ |
| E3 | Caret inside note → Remove still works | ☐ |
| E4 | Optional: unzip ODT and confirm `style:text-combine="lines"` on a **text** style (not paragraph) | ☐ |

---

## Out of scope for this release

- UNO / Asian Layout **brackets** around warichū (known Writer paint bug — see U1 draft).
- Manual division, alignment modes, annotation size UI.
- Publishing to GitHub Releases / update feed (wait for your OK).

## Sign-off

| Item | You |
|---|---|
| Manual tests passed | ☐ |
| Approve publish 0.3.16 | ☐ |
| Approve file Bugzilla U1 | ☐ (separate) |
