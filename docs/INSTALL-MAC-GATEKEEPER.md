# Installing marinaMoji on macOS (Gatekeeper)

marinaMoji tools are distributed from **GitHub** and our **website**, not from the Mac App Store. Apple may block the first launch of an unsigned installer. This is normal.

## Quick fix (recommended)

When you see that the app **cannot be opened** or is from an **unidentified developer**:

1. **Control-click** (right-click) the app or installer.
2. Choose **Open**.
3. Click **Open** again in the dialog.

French: **Clic droit → Ouvrir → Ouvrir**.

You only need to do this **once** per downloaded file.

## Alternative: System Settings

1. Try to open the app (it will be blocked).
2. Open **System Settings** → **Privacy & Security**.
3. Scroll down; click **Open Anyway** next to the marinaMoji message.
4. Confirm **Open**.

French: **Réglages Système → Confidentialité et sécurité → Ouvrir quand même**.

## What we do *not* recommend

- Disabling Gatekeeper globally (`spctl --master-disable`) — unnecessary and unsafe.
- Telling everyone to use Terminal unless support truly requires it.

## Downloads from the browser

Files from Chrome/Safari may have a **quarantine** flag. **Right-click → Open** clears the usual block. Advanced support only:

```bash
xattr -cr "/path/to/Install marinaMoji Kaeriten.app"
```

## Notarization (for maintainers)

**Apple notarization** needs a paid Apple Developer account. We currently ship **unsigned** installers and document **Right-click → Open**. Notarization can be added later if funding allows.

## Product-specific install pages

| Product | Install doc |
|---------|-------------|
| LibreOffice | Website → download `.oxt` → double-click |
| Word | Website → download `.dmg` → run installer app |
| ONLYOFFICE | Website → download zip or installer app |
| marinaMoji IME | [marinaMoji/marinaMoji](https://github.com/marinaMoji/marinaMoji) or website (separate installer) |

See [DISTRIBUTION.md](DISTRIBUTION.md).
