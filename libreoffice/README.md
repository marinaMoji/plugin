# marinaMoji Kaeriten — LibreOffice extension

Turns Unicode Kanbun source (`說㆒㆑者`) into borderless **anchored frames** with stacked glyphs (一 / レ).

## Requirements

- LibreOffice **6.4+** Writer (tested on **26.x** macOS)
- marinaMoji (or any input) for `;1` `;r` → ㆒ ㆑ in the document

## Install (one step)

```bash
cd libreoffice
chmod +x build.sh
./build.sh
```

1. **Quit Writer** completely.
2. **Tools → Extension Manager** — remove any old **marinaMoji Kaeriten**, then **Add** → `dist/MarinaMojiKaeriten.oxt` (**0.3.0**).
3. **Restart Writer**.

You should see a **marinaMoji** toolbar (Writer) and menu **marinaMoji** with **Render** / **Unrender**.

If the toolbar is hidden: **View → Toolbars → marinaMoji**.

### How the bundle works

Everything lives in the `.oxt`:

| Piece | Role |
|-------|------|
| `Scripts/python/marinamoji_kaeriten.py` | Render / unrender logic |
| `marinamoji_kaeriten_dispatch.py` | **ProtocolHandler** — receives toolbar clicks |
| `ProtocolHandler.xcu` + `MarinaMojiKaeriten.components` | Register the handler with LibreOffice |

Toolbar URLs are `org.marinaMoji.kaeriten:render_kaeriten` (not `vnd.sun.star.script:…`). That is the usual pattern for extension buttons: a small dispatch module at the **root** of the `.oxt` calls into `Scripts/python/`.

Optional **`./install.sh`** copies the same macros into your user profile for **Tools → Macros** or APSO debugging — not required for the toolbar.

### If buttons still do nothing

- **Tools → Customize → Toolbars → marinaMoji → Reset** (stale URLs from older versions).
- Quit LO, delete `~/Library/Application Support/LibreOffice/4/user/uno_packages/cache/`, reinstall the `.oxt`.

## Use

1. Type `說㆒㆑者` with marinaMoji
2. **marinaMoji → Render kaeriten** — selection if highlighted, else the whole document
3. Edit **source marks** in the text (**Unrender kaeriten**); do not edit inside frames
4. Run **Render kaeriten** again after mark or font-size changes (updates existing frames)

## Development

```bash
python3 libreoffice/tests/test_parser.py
./install.sh   # optional: user-profile copy for Macro dialog / APSO
```

Macro source: `marinamoji_kaeriten/marinamoji_kaeriten.py`
