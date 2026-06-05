# marinaMoji Kaeriten — LibreOffice extension

Turns Unicode Kanbun source (`說㆒㆑者`) into small **anchored images** with painted kaeriten glyphs (一 / レ). Legacy borderless frames remain readable/unrenderable.

## Requirements

- LibreOffice **6.4+** Writer (tested on **26.x** macOS)
- marinaMoji (or any input) for `;1` `;r` → ㆒ ㆑ in the document

## Install

### macOS (recommended — no Terminal)

1. Download **`marinamoji-kaeriten-libreoffice-mac.dmg`** from [GitHub Releases](https://github.com/marinaMoji/marinaMoji/releases) (or your website).
2. **Right-click → Open** the installer if macOS warns.
3. **Quit Writer**, run **Install marinaMoji Kaeriten (LibreOffice)**.
4. Accept the extension → **restart Writer** → **View → Toolbars → marinaMoji**.

The installer copies Python macros (needed on LibreOffice **26.x**) and opens `MarinaMojiKaeriten.oxt`.

### All platforms (`.oxt` only)

```bash
cd libreoffice
chmod +x build.sh build-icons.sh
./build.sh
```

Toolbar icons come from `../icons/*.svg` (copied into the `.oxt`, plus 32×32 and 26×26 PNGs). LibreOffice’s **built-in** toolbar uses SVG; **extensions** still use `ImageSmallURL` / `ImageBigURL` bitmaps, which LO scales to the current toolbar size. Install **librsvg** (`brew install librsvg`) before building if PNGs are missing.

1. **Quit Writer** completely.
2. **Tools → Extension Manager** — **remove** any old **marinaMoji Kaeriten**, **restart Writer**, then **Add** → `dist/MarinaMojiKaeriten.oxt` (**0.3.9**). A plain “update” can leave old toolbar config (wrong name or missing icons).
3. **Restart Writer**.

On **macOS 26.x**, if toolbar buttons do nothing after step 3, use the Mac installer above (or `./install.sh` from Terminal).

All commands are on the **marinaMoji** toolbar: **View → Toolbars → marinaMoji**.

If the menu still shows **Add-On 2** (a name LibreOffice invented earlier), remove the extension, quit Writer, reinstall **0.3.9**, and enable the toolbar again. That clears the old cached label.

| Button | Clipboard contents |
|--------|-------------------|
| Copy plain text | Canonical Unicode `說㆒㆑者` |
| Copy TEI | TEI XML (snippet if selection; full document if none) |
| Copy LaTeX | LaTeX (snippet if selection; full `.tex` scaffold if none) |

Render / Unrender are unchanged (they edit the document, not the clipboard).
The **Toggle vertical page** button switches the current page style between horizontal left-to-right (`LR_TB`) and vertical right-to-left (`TB_RL`), then refreshes existing rendered kaeriten.

### How the bundle works

| Piece | Role |
|-------|------|
| `Scripts/python/marinamoji_kaeriten.py` | Render / unrender / copy |
| `Scripts/python/export_core.py` | TEI / LaTeX conversion (no LO dependency) |
| `marinamoji_kaeriten_dispatch.py` | ProtocolHandler for toolbar |

Optional **`./install.sh`** — copies macros for **Tools → Macros** / APSO only.

### If buttons are missing or do nothing

1. Extension Manager → **remove** → restart Writer → install **0.3.9** → restart Writer.
2. **View → Toolbars → marinaMoji**
3. **Tools → Customize → Toolbars → marinaMoji → Reset**

## Use

1. Type `說㆒㆑者` with marinaMoji
2. Toolbar **Render kaeriten**
3. Optional: **Toggle vertical page** to switch the current page style between 横書き and 縦書き
4. Edit source with **Unrender**; do not edit inside rendered images/frames
5. **Copy plain text** / **Copy TEI** / **Copy LaTeX** — paste elsewhere

Export reads **Unicode source** (including marks from rendered images/frames). See [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## Development

```bash
python3 libreoffice/tests/test_parser.py
python3 libreoffice/tests/test_export.py
./install.sh   # optional
```
