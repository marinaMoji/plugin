# The Little Book of Japanese Typography

**Version:** LibreOffice extension **0.3.34** (toolbar `.v7`).

## Mechanism

The square marinaMoji logo (far left of the toolbar) opens **one** offline HTML
handbook in the system browser (`file://`):

- `help/about_en.html`
- `help/about_ja.html`
- `help/about_fr.html`

Eight pages in a single document (welcome → six features → Beyond Unicode), with
Previous/Next and arrow-key navigation (`help/book.js`).

Native UNO dialogs cannot host this editorial layout reliably; a bundled HTML
guide is the maintainable cross-platform choice. Opening it does **not** modify
the Writer document. See [INTEGRATION.md](INTEGRATION.md) for the browser vs
native/webview decision.

Page background is `#f7f5ef` to match specimen PNG fills. Page height follows
content (navigation is not pinned to the bottom of a tall viewport). Specimens
use per-feature CSS width caps so short PNGs are not oversized by `max-height`
alone.

## Page map

| # | Content | Specimen |
|---|---|---|
| 01 | Welcome | logo |
| 02 | Ruby | `ruby.png` |
| 03 | Warichū | `warichu.png` |
| 04 | Emphasis | `emphasis.png` |
| 05 | Tate-chū-yoko | `tate.png` |
| 06 | Jidori | `jidori.png` |
| 07 | Composition / kinsoku | `kinsoku.png` |
| 08 | Beyond Unicode + site link | `composer.png` |

## Screenshots

See [`screenshots/`](screenshots/).
