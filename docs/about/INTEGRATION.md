# Handbook launch — LibreOffice integration feasibility

**Status:** retain external browser (`file://`).  
**Date:** 2026-10-29 · extension **0.3.35**

## Current mechanism

The far-left toolbar control (`about_marinamoji`) calls `about.show_about_marinamoji()`.

That helper:

1. Resolves the Writer UI locale to `en` / `ja` / `fr`.
2. Locates the bundled file `help/about_<lang>.html` inside the installed `.oxt`.
3. Opens it with `com.sun.star.system.SystemShellExecute` (`URIS_ONLY`) as a
   `file://` URL, with OS fallbacks (`open` / `startfile` / `xdg-open`).

There is **no** local HTTP server in the shipped extension. A short-lived
`python -m http.server` is used only during development previews.

Assets (HTML, CSS, JS, logos, specimen PNGs) are packaged under `help/` and work
offline. The only expected network destination is the site link
`https://marinamoji.crcao.fr`.

## Option A — External browser (current)

| | |
|---|---|
| Pros | Full CSS; reliable images; same design on macOS / Windows / Linux; trivial packaging; offline |
| Cons | Leaves Writer; browser chrome; repeated clicks may open extra tabs |

**Recommendation:** keep this for production.

## Option B — Native LibreOffice dialog

UNO dialogs (`UnoControlDialog`, fixed text, buttons, image controls) can show
static labels and a few bitmaps. They do **not** provide a general HTML/CSS
engine. Recreating the eight-page handbook as native controls would abandon the
editorial layout and become a maintenance dead end.

**Not feasible** for preserving the current design.

## Option C — Embedded webview

LibreOffice does not expose a supported, cross-platform extension API for an
embedded Chromium/WebKit surface that extensions may ship. Platform-private
browser helpers (if any) are not a stable contract for Marketplace packaging,
would add security and accessibility surface, and would likely require different
code paths per OS.

**Not recommended** without an official LO API commitment.

## Decision

Prefer reliability, offline operation, and the existing HTML design over a
closer coupling to the Writer frame. The branded square logo remains the entry
point; the handbook remains a small book opened beside Writer.

Possible later polish (not required now): remember the last `file://` path and
document that re-clicking may add a browser tab — browsers control that, not the
extension.
