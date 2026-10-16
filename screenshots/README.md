# Marketplace / store screenshots

Canonical UI captures. Prefer replacing files **here**, then refreshing the host copies.

| File | Host | Also used as |
|------|------|----------------|
| `marinaMoji_libreoffice.png` | LibreOffice | `libreoffice/screenshots/writer.png` — upload to extensions.libreoffice.org |
| `marinaMoji_onlyoffice.png` | ONLYOFFICE | `onlyoffice/resources/store/screenshots/screen_1.png` (in `config.json`); plus `writer.png` and 1280×720 `install.png` / `uninstall.png` |

Refresh after editing:

```bash
cd plugin
cp screenshots/marinaMoji_libreoffice.png libreoffice/screenshots/writer.png
cp screenshots/marinaMoji_onlyoffice.png onlyoffice/resources/store/screenshots/writer.png
cp screenshots/marinaMoji_onlyoffice.png onlyoffice/resources/store/screenshots/screen_1.png
python3 - <<'PY'
from PIL import Image
src = Image.open("onlyoffice/resources/store/screenshots/writer.png").convert("RGBA")
tw, th = 1280, 720
sw, sh = src.size
scale = max(tw / sw, th / sh)
nw, nh = int(round(sw * scale)), int(round(sh * scale))
resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
left, top = (nw - tw) // 2, (nh - th) // 2
tile = resized.crop((left, top, left + tw, top + th))
tile.save("onlyoffice/resources/store/screenshots/install.png")
tile.save("onlyoffice/resources/store/screenshots/uninstall.png")
print("updated install.png / uninstall.png", tile.size)
PY
```

Docs: [LIBREOFFICE_MARKETPLACE.md](../docs/LIBREOFFICE_MARKETPLACE.md), [ONLYOFFICE_MARKETPLACE.md](../docs/ONLYOFFICE_MARKETPLACE.md).
