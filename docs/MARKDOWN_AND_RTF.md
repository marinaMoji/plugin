# Markdown and Apple RTF / RTFD study

Planning notes (June 2026). This is an exploration of whether marinaMoji should support **Markdown**, **HTML/CSS**, **Apple RTF**, or **RTFD** as additional rendering/export paths for kanbun marks.

**Related:** [ARCHITECTURE.md](ARCHITECTURE.md), [CONVENTIONS.md](CONVENTIONS.md), [OTHER_HOSTS.md](OTHER_HOSTS.md), [RENDERING_IMPROVEMENTS.md](RENDERING_IMPROVEMENTS.md).

---

## Executive summary

| Target | Best role | Recommendation |
|--------|-----------|----------------|
| **Markdown (`.md`)** | Canonical source plus human-readable notes | Keep plain Unicode; optionally add a small preview/export tool |
| **Markdown → HTML/CSS** | Browser preview, teaching pages, HTML/PDF export | Promising; lowest-risk non-office rendering path |
| **RTF (`.rtf`)** | Styled text exchange | Weak for kaeriten images on Apple; not a primary target |
| **RTFD (`.rtfd`)** | Apple-local rich text with image attachments | Worth a prototype, but Mac-centric and poor for interchange |
| **Apple Pages** | Apple word processor | No plugin API comparable to Word; use import/export or AppleScript only if users ask |

The main conclusion is consistent with the plugin architecture:

> Keep **Unicode Kanbun** (`說㆒㆑者`) as the semantic source. Treat Markdown / HTML / RTFD as **views or exports**, not as the place where kaeriten meaning lives.

Markdown/HTML is the more promising path. Apple RTFD is technically interesting because it can store text plus image attachments, but it is Apple-specific and fragile as a collaboration format.

---

## Baseline architecture

marinaMoji already separates:

1. **Input / source:** visible Unicode (`說㆒㆑者`).
2. **Rendered view:** host-specific layout objects (LibreOffice SVG image, Word inline PNG, ONLYOFFICE inline PNG).
3. **Export:** copy plain Unicode; downstream projects transform to their own TEI / LaTeX / HTML conventions.

Markdown and RTF should not break that model. If they cannot preserve the source string clearly, they are not good archival formats.

---

## Markdown

### What Markdown can do well

Markdown is excellent for:

- notes, documentation, lesson pages, syllabi, and corpus comments;
- git-friendly editing and review;
- plain Unicode preservation;
- conversion to HTML / PDF through tools such as Pandoc, Markdown-it, or static-site generators.

For marinaMoji, the simplest Markdown source is just:

```md
說㆒㆑者
```

This is perfectly searchable and round-trips through most tools. It is not pretty, but it is semantically honest.

### What Markdown cannot do natively

CommonMark / GitHub Flavored Markdown has **no native ruby or kaeriten syntax**. It does allow raw HTML in many renderers, but this is renderer-dependent and often disabled or sanitized in hosted services.

For example, a renderer that allows raw HTML can carry ruby:

```md
<ruby>說<rt>一レ</rt></ruby>者
```

But this is no longer portable Markdown in the same way. Some Markdown processors escape raw HTML by default; GitHub-flavored pipelines may apply tag filters; static-site generators vary.

### Markdown plus custom syntax

We could define a small marinaMoji Markdown convention, for example:

```md
{說|㆒㆑}者
```

or:

```md
說{㆒㆑}者
```

A preprocessor could convert this to:

```html
<span class="mm-kanbun">
  <span class="mm-base">說</span>
  <span class="mm-kaeriten">一<br>レ</span>
</span>者
```

This would be easy to parse, but it creates **another source dialect**. Since marinaMoji already commits `說㆒㆑者`, the better first step is probably:

```text
Unicode source → Markdown preview/export
```

not:

```text
New Markdown syntax → canonical source
```

### Markdown recommendation

Do **not** create a separate Markdown source syntax yet. Instead:

- Support plain Unicode in Markdown.
- Consider a small converter: `說㆒㆑者` → HTML spans / ruby / inline SVG.
- Use it for documentation, teaching pages, static website examples, or PDF handouts.

---

## HTML / CSS from Markdown

HTML/CSS is the strongest “Markdown-adjacent” target because browsers have real layout tools:

- `<ruby>`, `<rt>`, `<rp>` for annotations;
- `writing-mode: vertical-rl` for vertical text;
- `ruby-position` for annotation side control;
- inline SVG or canvas-generated PNG for exact compound marks.

### Option A: HTML ruby

Simple output:

```html
<ruby>說<rt>一レ</rt></ruby>者
```

Pros:

- semantic-ish web markup;
- accessible fallback possible with `<rp>`;
- works for furigana-like annotations.

Cons:

- kaeriten are not ordinary ruby;
- compound stacks (`一` over `レ`) need careful CSS;
- side placement differs between horizontal and vertical writing;
- browser support for complex ruby is uneven compared with simple ruby.

### Option B: CSS inline boxes

Output:

```html
<span class="mm-cluster">
  <span class="mm-base">說</span>
  <span class="mm-marks">一<br>レ</span>
</span>者
```

CSS can then tune:

```css
.mm-cluster {
  display: inline-flex;
  align-items: flex-end;
}
.mm-marks {
  font-size: 0.42em;
  line-height: 0.7;
}
.vertical {
  writing-mode: vertical-rl;
}
```

Pros:

- closer to our Word / ONLYOFFICE image layout logic;
- easy to tune;
- can be generated from Unicode source.

Cons:

- less semantic than ruby;
- print/PDF output depends on browser engine;
- vertical kanbun layout still needs testing.

### Option C: inline SVG

Output:

```html
說<img class="mm-kaeriten" alt="㆒㆑" src="data:image/svg+xml,...">者
```

Pros:

- closest to the LibreOffice SVG renderer;
- exact compound stacking;
- stable print from browser/PDF if CSS is controlled.

Cons:

- images are views, not text;
- copy/paste loses marks unless `alt` / data attributes are used;
- accessibility needs care.

### HTML/CSS recommendation

Prototype a **static preview/export pipeline**:

```text
plain Unicode (`說㆒㆑者`)
  → parse clusters
  → HTML spans or inline SVG
  → browser preview / print to PDF
```

This would be useful for:

- website documentation;
- teaching handouts;
- web preview of Markdown notes;
- corpus browsing interfaces.

It should not replace the office plugins for serious word-processor editing.

---

## Apple RTF

### What RTF can do

RTF is a styled text exchange format. Apple’s `NSAttributedString` APIs can read and write RTF, and TextEdit can open it.

RTF can represent:

- font, size, color;
- superscript / subscript-like baseline changes;
- paragraph styles;
- basic document metadata.

### Why RTF is weak for kaeriten

Apple’s RTF implementation is not a good target for our current image-based renderer:

- standard RTF on macOS is poor for embedded image attachments;
- TextEdit tends to switch to **RTFD** when images are inserted;
- precise anchored inline images are not portable across RTF readers;
- vertical Japanese page layout is not a strength of TextEdit / RTF.

You could approximate simple marks with small baseline-shifted text:

```text
說 + small raised/subscript レ
```

But compound kaeriten and vertical placement would be fragile. That is exactly the class of problem we rejected for the office plugins.

### RTF recommendation

Do not target plain `.rtf` as a primary renderer. At most:

- export simple fallback rich text for TextEdit;
- use it for debugging `NSAttributedString`;
- keep canonical Unicode visible or recoverable.

---

## Apple RTFD

### What RTFD is

RTFD (“Rich Text Format Directory”) is Apple’s package format for rich text with attachments. It is a directory that appears as a file in Finder. It usually contains:

- `TXT.rtf` — the RTF text stream;
- image/PDF attachments stored as separate files;
- RTF references to those attachments.

TextEdit and some Apple frameworks support RTFD. Apple’s attributed-string APIs can write RTFD through file-wrapper APIs (`NSAttributedString` / `FileWrapper`) when text includes `NSTextAttachment` images.

### Why RTFD is interesting

RTFD could represent the same source/view split:

```text
說 [attached PNG/SVG for 一レ] 者
```

The attached image could be generated by the same canvas/SVG code used by the office plugins. In a native macOS tool, `NSTextAttachment` could hold the rendered mark image.

Potential workflow:

```text
Unicode source (`說㆒㆑者`)
  → parse clusters
  → NSAttributedString
  → replace marks with NSTextAttachment image
  → write `.rtfd`
```

### Why RTFD is risky

RTFD is not a general interchange format:

- it is mostly Apple / Cocoa / TextEdit / Pages territory;
- it is a package directory, awkward to send unless zipped;
- Microsoft Word and many non-Apple tools do not reliably support it;
- copy/paste may lose attachment metadata;
- image attachments are views, so the Unicode marks need to remain recoverable somehow.

### Possible metadata strategy

For RTFD, do not rely on image pixels. Possible strategies:

1. Keep a hidden or visible source layer nearby.
2. Put source marks in attachment filename, e.g. `mmk_3192_3191.png`.
3. Store a sidecar JSON inside the `.rtfd` package, e.g. `marinamoji.json`.
4. Prefer a visible source export alongside `.rtfd`, e.g. `document.txt`.

The cleanest approach may be:

```text
document.rtfd      # Apple-local preview/edit file
document.txt       # canonical Unicode source
```

But that is less convenient than our current “source inside the document” architecture.

### RTFD recommendation

RTFD is worth a **small prototype** if we want an Apple-native export:

- input: `.txt` / Markdown with Unicode source;
- output: `.rtfd` with `NSTextAttachment` images;
- no editing promises at first;
- source recovery through visible Unicode sidecar or embedded metadata.

It should be treated as **Apple-local preview/export**, not as a fourth office plugin.

---

## Apple Pages

Pages can open/import RTF/RTFD and has AppleScript / Shortcuts automation possibilities, but it does not offer a Word-style add-in API for in-document rendering commands.

Possible paths:

- Generate `.rtfd` and open in Pages.
- Generate `.docx` via the Word renderer path and open in Pages (layout uncertain).
- Use AppleScript to automate paste/import (fragile).

Recommendation: defer Pages unless a specific user group asks for it.

---

## Prototype proposals

### Prototype 1: Markdown/HTML preview

Build a small script:

```bash
python tools/kanbun_preview.py input.md > output.html
```

It should:

- preserve Markdown content;
- detect Unicode clusters like `說㆒㆑`;
- render clusters as HTML spans or inline SVG;
- include CSS for horizontal and vertical preview;
- leave the source Markdown untouched.

This is the best first prototype.

### Prototype 2: Static-site shortcode

For the marinaMoji website, add a Markdown/Grav shortcode:

```md
[kanbun]說㆒㆑者[/kanbun]
```

or automatically render code spans / spans marked with a class. This is useful for documentation but should not be generalized too early.

### Prototype 3: Apple RTFD exporter

Build a small macOS command-line tool or Swift script:

```bash
marinamoji-rtfd input.txt output.rtfd
```

It should:

- parse `說㆒㆑者`;
- create an `NSAttributedString`;
- replace mark runs with `NSTextAttachment` PNG/PDF images;
- write RTFD with `rtfdFileWrapper` / `fileWrapper`;
- include a source sidecar or source metadata.

This is more experimental and more platform-specific than Markdown/HTML.

---

## Recommended priority

| Priority | Work | Why |
|----------|------|-----|
| 1 | Markdown → HTML preview/export | Helps docs, teaching, web preview; low risk |
| 2 | HTML/CSS vertical layout experiments | Clarifies whether web/PDF can serve real kanbun pages |
| 3 | RTFD exporter spike | Useful Apple-native experiment, but narrow |
| 4 | Pages automation | Only if user demand appears |
| Defer | Plain RTF renderer | Too weak for compound image-based kaeriten |

---

## Open questions

1. Should Markdown rendering use **HTML ruby**, **CSS inline boxes**, or **inline SVG**?
2. Is the target **screen preview**, **browser print/PDF**, or **editable rich text**?
3. For RTFD, must the `.rtfd` be editable, or is it acceptable as a rendered preview?
4. How should source marks be recoverable from RTFD attachments?
5. Do we need a website shortcode before a general Markdown tool?

---

## Changelog

| Date | Note |
|------|------|
| 2026-06 | Initial Markdown / HTML / Apple RTF / RTFD study. |
