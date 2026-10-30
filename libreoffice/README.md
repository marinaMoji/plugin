# marinaMoji Kaeriten — LibreOffice extension

Turns Unicode Kanbun source (`說㆒㆑者`) into small **anchored images** with painted kaeriten glyphs (一 / レ). Legacy borderless frames remain readable/unrenderable.

## Composer drawings (no button)

When the marinaMoji character composer builds a structure with no Unicode character, **Insert** writes `character_composer_result.svg` to the marinaMoji profile folder (`~/Library/Application Support/marinaMoji/` on macOS, `~/.config/marinamoji/` on Linux, `%USERPROFILE%\AppData\LocalLow\marinaMoji\` on Windows — note **LocalLow**, not `%LOCALAPPDATA%`). The extension starts a small watcher (`Jobs.xcu` + background thread) and also inserts on Writer **OnFocus**: a result newer than the last one inserted, and under two minutes old, is inserted at the cursor as an as-character SVG image sized to the surrounding text. A failed attempt is retried (the result is only marked seen after a successful insert). There is no toolbar button. Needs extension **0.3.12+** (0.3.10 and earlier lack `composer_handoff.py` / `Jobs.xcu`). **0.3.14** looks in LocalLow first (0.3.13 looked only under `%LOCALAPPDATA%` and missed the IME file on Windows). On Windows the IME must also be **0.0.18-rc14+** so Insert writes the profile SVG (older builds only wrote a TEMP sibling the extension never reads). Reinstall the extension (remove the old one first) so the event job registers. On Linux, a marinaMoji build that restores the previous window after Insert avoids having to click back into Writer.

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

Toolbar icons come from `../icons/*.svg` (copied into the `.oxt`). `Addons.xcu` points `ImageSmallURL` / `ImageBigURL` at those SVGs so LibreOffice can render them at the current toolbar size (sharp on HiDPI, like Colibre). The Extension Manager still uses a 42×42 PNG — install **librsvg** (`brew install librsvg`) before building if that icon is missing.

1. **Quit Writer** completely.
2. **Tools → Extension Manager** — **remove** any old **marinaMoji Kaeriten**, **restart Writer**, then **Add** → `dist/MarinaMojiKaeriten.oxt` (**0.3.36**). A plain “update” can leave old toolbar config (wrong name or missing icons).
3. Accept the **GPL-3.0** license dialog → **Restart Writer**.

On **macOS 26.x**, if toolbar buttons do nothing after step 3, use the Mac installer above (or `./install.sh` from Terminal).

All commands are on the **marinaMoji** toolbar: **View → Toolbars → marinaMoji**.

If the menu still shows **Add-On 2** (a name LibreOffice invented earlier), remove the extension, quit Writer, reinstall **0.3.36**, and enable the toolbar again. That clears the old cached label.

**Version note:** GitHub’s `libreoffice-v0.3.10` tag was cut on 2026-10-16, *before* bottom-line / left-margin alignment landed. That release and a local Mac rebuild can both report “0.3.10” while shipping different Python. Use **0.3.11+** for the alignment work; **0.3.15+** for warichū.

| Button | Clipboard contents |
|--------|-------------------|
| Copy plain text | Canonical Unicode `說㆒㆑者` |

Render / Unrender are unchanged (they edit the document, not the clipboard).
The **Toggle vertical page** button switches the current page style between horizontal left-to-right (`LR_TB`) and vertical right-to-left (`TB_RL`), then refreshes existing rendered kaeriten.

**Apply warichū / Remove warichū** use Writer’s native character-span combine (`CharCombineIsOn` only — no UNO bracket props). Select the *note* text inside a paragraph (leave some body text outside the selection), then Apply. Selecting the whole paragraph is refused (that paints badly in Writer).

**Apply ruby / Remove ruby** (0.3.21+) use Writer’s native `RubyText` with `RubyAdjust` **LEFT** (Writer’s own default — stable beside vertical warichū; stretch modes can glitch adjacent combine). Nesting ruby and warichū on the same span is refused. Warichū apply is bare `CharCombineIsOn` only (do not clear `RubyText` on combine).

### How the bundle works

| Piece | Role |
|-------|------|
| `Scripts/python/marinamoji_kaeriten.py` | Render / unrender / copy / warichū entry points |
| `Scripts/python/warichu.py` | Native warichū apply / remove |
| `Scripts/python/export_core.py` | Plain-text export helpers (TEI/LaTeX kept for dev only) |
| `marinamoji_kaeriten_dispatch.py` | ProtocolHandler for toolbar |

Optional **`./install.sh`** — copies macros for **Tools → Macros** / APSO only.

### If buttons are missing or do nothing

1. Extension Manager → **remove** → restart Writer → install **0.3.15** → restart Writer.
2. **View → Toolbars → marinaMoji**
3. **Tools → Customize → Toolbars → marinaMoji → Reset**

## Validate / release

```bash
./build.sh
./validate-extension.sh
python3 tests/test_parser.py
python3 tests/test_export.py
python3 tests/test_warichu.py
```

- **LibreOffice-only GitHub release:** tag `libreoffice-v0.3.15` (must match `description.xml`) or run **Release LibreOffice extension** in Actions.
- **Official Extensions website + update feed:** [docs/LIBREOFFICE_MARKETPLACE.md](../docs/LIBREOFFICE_MARKETPLACE.md).

## Use

1. Type `說㆒㆑者` with marinaMoji
2. Toolbar **Render kaeriten**
3. Optional: **Toggle vertical page** to switch the current page style between 横書き and 縦書き
4. Edit source with **Unrender**; do not edit inside rendered images/frames
5. **Copy plain text** — paste elsewhere (canonical Unicode)
6. Warichū: type e.g. `本文割り注は、良いです。`, select only `割り注は、良いです。`, **Apply warichū**

Render is incremental: it formats new Unicode marks, refreshes rendered views when font / size / orientation changes, and skips views that are already current.

Export reads **Unicode source** (including marks from rendered images/frames). See [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

**Publishing:** GitHub Releases → [docs/INSTALLERS_AND_UPDATES.md](../docs/INSTALLERS_AND_UPDATES.md); Extensions website → [docs/LIBREOFFICE_MARKETPLACE.md](../docs/LIBREOFFICE_MARKETPLACE.md).

## Development

```bash
python3 tests/test_parser.py
python3 tests/test_export.py
./install.sh   # optional
```
