# marinaMoji Kaeriten — ONLYOFFICE plugin

JavaScript plugin for **ONLYOFFICE Document Editor** (Writer). Same model as the LibreOffice and Word tools:

- **Source:** visible Unicode from marinaMoji (`說㆒㆑者`)
- **View:** inline PNG images with stacked display glyphs (一 / レ); inline content controls remain as a fallback
- **Commands:** Render, Unrender, Refresh, Copy plain text

**Status (June 2026):** Implementation complete for v1. **Pre-publish QA** on ONLYOFFICE Desktop before release. LibreOffice remains the recommended daily driver after QA.

See [../docs/WORD_FINDINGS.md](../docs/WORD_FINDINGS.md) (interoperability) and [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## Requirements

- ONLYOFFICE Document Server or Desktop **7.0+** with **plugin support**
- marinaMoji (or any input) for Kanbun marks in the document

Paste from LibreOffice **does not** bring LO frames into ONLYOFFICE — format from **Unicode source** in each app.

## Install

### Desktop Editors (macOS) — recommended (no Terminal)

Download **`marinamoji-kaeriten-onlyoffice-mac.dmg`** from GitHub Releases, then:

1. **Right-click → Open** the installer if macOS warns.
2. **Quit ONLYOFFICE (Cmd+Q)**, run **Install marinaMoji Kaeriten (ONLYOFFICE)**.
3. Reopen Writer → **Plugins → marinaMoji**.

### Desktop Editors (macOS) — Terminal (developers)

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

**Find the plugin:** **Plugins** tab → **Plugin Manager** → **My plugins**, or the **Plugins** list → **marinaMoji**.

### Manual install (macOS / Windows / Linux)

1. Run `./build.sh` — produces `dist/marinamoji-kaeriten.plugin` for Plugin Manager (7.4+).
2. Copy all plugin files into the editor’s `sdkjs-plugins` directory inside a folder named `{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}`:

   | Platform | `sdkjs-plugins` path |
   |----------|-------------------|
   | **macOS** | `~/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/sdkjs-plugins/` |
   | **Windows** | `%ProgramFiles%\ONLYOFFICE\DesktopEditors\editors\sdkjs-plugins\` |
   | **Linux** | `/opt/onlyoffice/desktopeditors/editors/sdkjs-plugins/` or `~/.local/share/onlyoffice/desktopeditors/sdkjs-plugins/` |

3. Restart ONLYOFFICE Writer.

### Plugin Manager (offline, 7.4+)

1. Run `./build.sh` (or download `marinamoji-kaeriten.plugin` from GitHub Releases).
2. In Writer: **Plugins** → **Plugin Manager** → **My plugins** → **Install plugin manually** → select `dist/marinamoji-kaeriten.plugin`.

### Document Server (Docker / self-hosted)

Mount the plugin into the server’s `sdkjs-plugins` directory using the GUID folder name `{7A9E3B2C-4D5F-6E8A-1B0C-9D3E5F7A2B1C}`.

Then enable plugins in editor config (`plugins: true`).

## Use

1. Type `說㆒㆑者` with marinaMoji.
2. Open the **marinaMoji** sidebar.
3. Click **Render** — paragraphs with mark clusters get inline views, and existing views are rebuilt from their Unicode source.
4. Edit source with **Unrender**; do not edit inside the rendered images/controls.
5. Click **Render** again after font changes; it rebuilds existing views too.
6. **Copy plain** for canonical Unicode elsewhere.

**Note:** v0.1 **Render** walks **all paragraphs** in the document that contain marks or rendered views (not only the current selection). Export uses selection when present, otherwise the full document.

## Project layout

| Path | Role |
|------|------|
| `config.json` | Plugin registration |
| `index.html` | Sidebar UI |
| `scripts/exportCore.js` | Parser + plain export |
| `scripts/kaeriten.js` | `callCommand` render / unrender |
| `mapping.json` | Shared mark definitions (from `../mapping.json`) |

## Development

- Official plugin API: [ONLYOFFICE Plugins](https://api.onlyoffice.com/docs/plugin-and-macros/get-started/overview/)
- Inline images: `Api.CreateImage()` + `SetWrappingStyle("inline")`; source metadata lives in drawing names (`MARINAMOJI:source=…`)
- Image size is computed from the paragraph/run font size; the PNG can include a small transparent top pad to tune alignment because ONLYOFFICE inline drawings cannot be raised/lowered like text runs.
- Inline controls: `Api.CreateInlineLvlSdt()` remain as the fallback renderer
- Reuses export logic from `word/src/exportCore.js` / LO `export_core.py`

## Limitations (v0.1)

- No import of LibreOffice frames or Word content controls from other apps
- Render applies per **paragraph** (document-wide scan)
- Copy plain reads canonical text from image/control metadata while views are shown
- API names (`GetParentParagraph`, `RemoveElement`, …) may differ slightly across ONLYOFFICE versions — report issues if a command fails
