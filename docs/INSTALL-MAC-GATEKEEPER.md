# Installing marinaMoji on macOS (Gatekeeper)

marinaMoji tools are distributed from **GitHub** and our **website**, not from the Mac App Store. Apple may block the first launch of an unsigned installer. This is normal.

## Releases are signed and notarized

Installers published from `plugins-v*` tags are signed with a Developer ID and notarized by Apple, so they open with a double-click. Only older, unsigned downloads show the warning.

## If you still see the warning

1. Try to open the app (it will be blocked; close the dialog).
2. Open **System Settings** → **Privacy & Security**.
3. Scroll down; click **Open Anyway** next to the marinaMoji message.
4. Confirm **Open** (password required).

French: **Réglages Système → Confidentialité et sécurité → Ouvrir quand même**.

**Right-click → Open** no longer bypasses Gatekeeper on macOS 15 (Sequoia) and later.

## What we do *not* recommend

- Disabling Gatekeeper globally (`spctl --master-disable`) — unnecessary and unsafe.
- Telling everyone to use Terminal unless support truly requires it.

## Downloads from the browser

Files from Chrome/Safari may have a **quarantine** flag. If the warning persists, advanced support only:

```bash
xattr -cr "/path/to/Install marinaMoji Kaeriten.app"
```

## Notarization (for maintainers)

CI signs and notarizes the `.dmg` installers (`packaging/mac/sign-and-notarize.sh`) when the Apple secrets are set on the repo. Without them the build falls back to ad-hoc signing and the warning above appears.

## Product-specific install pages

| Product | Install doc |
|---------|-------------|
| LibreOffice | Website → download `.oxt` → double-click |
| Word | Website → download `.dmg` → run installer app |
| ONLYOFFICE | Website → download zip or installer app |
| marinaMoji IME | [marinaMoji/marinaMoji](https://github.com/marinaMoji/marinaMoji) or website (separate installer) |

See [DISTRIBUTION.md](DISTRIBUTION.md).
