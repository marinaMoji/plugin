# marinaMoji Kaeriten — ONLYOFFICE plugin

JavaScript plugin for **ONLYOFFICE Document Editor** (Writer). Same model as the LibreOffice and Word tools:

- **Source:** visible Unicode from marinaMoji (`說㆒㆑者`)
- **View:** inline content controls with stacked display glyphs (一 / レ)
- **Commands:** Render, Unrender, Refresh, Copy plain / TEI / LaTeX

**Status (May 2026):** v0.1 scaffold — not yet QA’d on a live ONLYOFFICE install. LibreOffice remains the recommended editor for daily work.

See [../docs/WORD_FINDINGS.md](../docs/WORD_FINDINGS.md) (interoperability) and [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## Requirements

- ONLYOFFICE Document Server or Desktop **7.0+** with **plugin support**
- marinaMoji (or any input) for Kanbun marks in the document

Paste from LibreOffice **does not** bring LO frames into ONLYOFFICE — format from **Unicode source** in each app.

## Install

### Desktop Editors (macOS) — recommended

```bash
cd plugin/onlyoffice
chmod +x install-mac.sh build.sh
./install-mac.sh
```

Then **quit ONLYOFFICE (Cmd+Q)** and reopen Writer.

**Where it goes (macOS):**

```text
~/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/sdkjs-plugins/{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}/
```

ONLYOFFICE requires the folder name to be the plugin **GUID** from `config.json` (the part in `{…}` braces), **not** `marinamoji-kaeriten`. Putting files under `…/plugins/` does **not** work.

**Find the plugin:** **Plugins** tab → **Plugin Manager** → **My plugins**, or the **Plugins** list → **marinaMoji** → **marinaMoji Kaeriten**.

### Manual install (macOS / Windows / Linux)

1. Run `./build.sh`
2. Copy all plugin files into the editor’s `sdkjs-plugins` directory inside a folder named `{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}`:

   | Platform | `sdkjs-plugins` path |
   |----------|-------------------|
   | **macOS** | `~/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/sdkjs-plugins/` |
   | **Windows** | `%ProgramFiles%\ONLYOFFICE\DesktopEditors\editors\sdkjs-plugins\` |
   | **Linux** | `/opt/onlyoffice/desktopeditors/editors/sdkjs-plugins/` or `~/.local/share/onlyoffice/desktopeditors/sdkjs-plugins/` |

3. Restart ONLYOFFICE Writer.

### Plugin Manager (offline, 7.4+)

1. Zip the contents of `onlyoffice/` (files at archive root, not the folder wrapper).
2. Rename the zip to `.plugin`.
3. In Writer: **Plugins** → **Plugin Manager** → **My plugins** → **Install plugin manually**.

### Document Server (Docker / self-hosted)

Mount the plugin into the server’s `sdkjs-plugins` directory using the GUID folder name `{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}`.

Then enable plugins in editor config (`plugins: true`).

## Use

1. Type `說㆒㆑者` with marinaMoji.
2. Open the **marinaMoji Kaeriten** sidebar.
3. Click **Render** — paragraphs with mark clusters get inline views.
4. Edit source with **Unrender**; do not edit inside the controls.
5. **Refresh** after font changes.
6. **Copy plain** / **TEI** / **LaTeX** for export elsewhere.

**Note:** v0.1 **Render** walks **all paragraphs** in the document that contain marks (not only the current selection). Export uses selection when present, otherwise the full document.

## Project layout

| Path | Role |
|------|------|
| `config.json` | Plugin registration |
| `index.html` | Sidebar UI |
| `scripts/exportCore.js` | Parser + TEI/LaTeX |
| `scripts/kaeriten.js` | `callCommand` render / unrender |
| `mapping.json` | Shared mark definitions (from `../mapping.json`) |

## Development

- Official plugin API: [ONLYOFFICE Plugins](https://api.onlyoffice.com/docs/plugin-and-macros/get-started/overview/)
- Inline controls: `Api.CreateInlineLvlSdt()` with tag `MARINAMOJI:source=…` (same idea as Word content controls)
- Reuses export logic from `word/src/exportCore.js` / LO `export_core.py`

## Limitations (v0.1)

- No import of LibreOffice frames or Word content controls from other apps
- Render applies per **paragraph** (document-wide scan)
- TEI/LaTeX export briefly unrenders the document to read canonical text, then re-renders
- API names (`GetParentParagraph`, `RemoveElement`, …) may differ slightly across ONLYOFFICE versions — report issues if a command fails
