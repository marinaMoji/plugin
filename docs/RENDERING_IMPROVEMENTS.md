# Rendering improvements — implementation notes

Cross-host rendering improvements (June 2026). All three items below are **implemented**.

**Related:** [ARCHITECTURE.md](ARCHITECTURE.md), [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md), [WORD_FINDINGS.md](WORD_FINDINGS.md), [ONLYOFFICE.md](ONLYOFFICE.md), [mapping.json](../mapping.json).

---

## Summary

| # | Goal | Host | Priority (suggested) |
|---|------|------|----------------------|
| 1 | **Inline image renderer** with tight compound stacking (like Word) | ONLYOFFICE | Done — June 2026 |
| 2 | **Render whole document** when nothing is selected (LO behaviour) | Word | Done — June 2026 |
| 3 | **Incremental smart Render** — new marks only; refresh when font/size/orientation changed; skip if already correct | LibreOffice / Word / OO | Done — June 2026 implementation pass |

---

## 1. ONLYOFFICE: inline images like Word

### Current state

- Renderer: **inline images** (`Api.CreateImage`) generated from sidebar canvas PNGs.
- Compound layout: painted glyphs in a canvas PNG, using `compound_touch` overlap from `mapping.json`.
- `mapping.json` → `onlyoffice_primary: "inline_image"`.

Inline content controls remain as a fallback/legacy path, but the primary renderer now matches Word’s canvas-drawn PNG model. This avoids fighting ONLYOFFICE run positioning for tight compound stacks.

### Implemented state

Match **Word’s inline-picture model** ([word/src/wordInlinePicture.js](../word/src/wordInlinePicture.js)):

- Draw compound kaeriten on an **off-screen canvas** in the plugin UI (sidebar has DOM + canvas).
- Export **PNG (base64)** per cluster with `compound_touch` overlap for tight vertical stacks.
- Insert with **`Api.CreateImage(base64, widthEmu, heightEmu)`** + **`SetWrappingStyle("inline")`** + **`paragraph.AddDrawing(image)`** (ONLYOFFICE Document Builder API).
- Store source marks and fingerprint in the drawing **name** (`MARINAMOJI:source=㆒㆑;fp=…`). ONLYOFFICE exposes `SetName` / `GetName` on drawings, not Word-style alternative text.

### Why this is feasible

ONLYOFFICE documents **`Api.CreateImage`** with URL or **Base64** and inline wrapping ([CreateImage](https://api.onlyoffice.com/docs/office-api/usage-api/document-api/Api/Methods/CreateImage/), [SetWrappingStyle](https://api.onlyoffice.com/docs/office-api/usage-api/document-api/ApiImage/Methods/SetWrappingStyle/)). The plugin already runs in a browser context where canvas is available (unlike `callCommand` sandbox — image generation stays in the sidebar, only base64 crosses the boundary).

### Implementation

1. **Canvas draw module** — duplicated minimally in `onlyoffice/scripts/kaeriten.js` with the same `onlyoffice_inline_image` mapping knobs.
2. **Render plan** — keep paragraph scan + segment split; replace `fillInlineSdtGlyphs` branch with “insert inline drawing per kaeriten segment”.
3. **Unrender / Refresh / Copy plain** — walk controls and drawings by metadata prefix; images use drawing names.
4. **mapping.json** — `onlyoffice_primary: "inline_image"` and `onlyoffice_inline_image` glyph ratios.

### Risks

- **Base64 size** in `callCommand` payloads for long documents (batch per paragraph).
- **API differences** between ONLYOFFICE Desktop vs Document Server versions (`AddDrawing` on paragraph vs run).
- **No 縦書き** in ONLYOFFICE — horizontal image placement only (same limitation as today).
- QA needed: inline image vertical alignment beside kanji vs Word/LO.

### Success criteria

- `說㆒㆑者` compound stack visually **touches** (一 over レ) comparable to Word inline picture and LO SVG.
- Unrender restores `㆒㆑` without glyph spill (current SDT unrender fix preserved).
- Copy plain still reads marks from image metadata.

---

## 2. Word: render all (selection optional)

### Current state

| Command | Scope in Word | Scope in LibreOffice |
|---------|---------------|----------------------|
| **Render** | Selection if it contains marks; empty selection scans **whole document** | Selection if non-empty, else **whole document** (`_work_range`) |
| **Copy plain** | Selection or body | Selection or document |
| **Unrender** | Selection required | Selection or document |

Earlier Word builds deliberately required a selection with kanbun marks to avoid silent full-document scans and accidental mass formatting. This has now been relaxed for **Render** only: a non-empty selection still scopes the command, but an empty selection uses the document body, matching LibreOffice.

LibreOffice’s **Render** and legacy **Refresh** alias all call `render_kaeriten` → `_work_range(doc)` → format + refresh in scope.

### Implemented first step

**Parity with LibreOffice for Render:**

- Caret only / empty selection → **scan `document.body`** for kaeriten clusters and render all unrendered marks in range.
- Non-empty selection with marks → selection only.
- Non-empty selection without marks → warning: clear the selection to render the whole document.
- Optional later: confirmation dialog before whole-document render on very large files.

### Implementation sketch

1. Change `getWorkRangeForRender` to mirror `getWorkRange`:
   - If selection empty or whitespace-only → `context.document.body.getRange()`.
   - If selection has text but **no** marks → prompt user (stricter).
2. Keep orphan-view and cluster search scoped to `workRange` (already in `renderClustersInRange`).
3. Update task pane strings and [CONVENTIONS.md](CONVENTIONS.md) — “select text, or click Render with caret anywhere to format the document”.
4. **Unrender:** consider optional whole-document unrender when selection empty (LO already allows this via `_work_range`).

### Risks

- Performance on long theses (batch `Word.run` already used; may need progress UI).
- Selection that includes **both** rendered pictures and raw marks — must not double-render (see §3 fingerprint logic; Word already has orphan-view recovery).

### Success criteria

- User types marks throughout chapter, places caret, clicks **Render** once → all clusters formatted (same as LO).
- Refresh on already-current inline pictures is a no-op; changing font size/orientation makes the fingerprint differ and redraws.

---

## 3. LibreOffice: incremental smart Render

### Problem (user report)

After some kaeriten in a passage are already rendered, **Render** on a selection that mixes views + fresh Unicode marks can miss new marks or behave inconsistently. Users want one button that:

1. Renders **all unrendered** kaeriten in scope.
2. **Re-renders** existing views when **font**, **font size**, or **page/paragraph orientation** (横↔縦) changed.
3. **Skips** views that are already correct (no flicker, faster).

### Current state (code)

`render_kaeriten` → `_render_in_scope`:

```text
n_new     = _format_clusters(...)      # Unicode mark runs → new views
n_updated = _refresh_frames_in_place(...)
          + _refresh_graphics_in_place(...)   # stale existing views only
```

- **`_collect_mark_runs`** (2026 fix): walks **text portions** instead of string offsets, because as-character frames desync `getString()` length from cursor positions. This addressed “later marks skipped after first render” in many cases.
- **`_refresh_*_in_place`**: computes a render fingerprint and skips views whose stored fingerprint still matches.
- **`toggle_page_writing_mode`**: calls `_refresh_rendered_views` only (no new marks).
- Legacy menu name **Refresh rendering** is an **alias for Render** (same function), not refresh-only.

So today: Render = “new + refresh stale existing views in scope.”

### Implemented first pass

Single **Render** command on Word and ONLYOFFICE; LibreOffice **Format kaeriten** / **Refresh rendering** (same function):

| Cluster state | Action |
|---------------|--------|
| Unicode marks in source, no view | **Insert** new view |
| View exists, fingerprint **matches** host | **Skip** |
| View exists, fingerprint **differs** (size, font, vertical, mapping version) | **Replace** view in place (or delete + insert) |
| View exists, source marks **changed** (user edited after Unrender) | **Render** the edited Unicode source |
| Orphan view (no matching source) | Leave for manual Unrender or optional cleanup |

### Fingerprint

Encoded in frame/graphic `Description`, appended to the existing `MARINAMOJI:…` payload:

```text
MARINAMOJI:source=㆒㆑;fp=v1|renderer=image|pt=12.0|vert=0|font=…|rh=<mapping rendering hash>
```

| Field | Source |
|-------|--------|
| `pt` | `_host_char_height` at anchor (rounded 0.1 pt) |
| `vert` | `_is_vertical_writing` at anchor |
| `font` | first resolved font name at anchor |
| `renderer` | image vs legacy frame |
| `rh` | hash of relevant `mapping.json` rendering keys |

On Render:

1. Format any **source clusters** (Unicode mark runs) still visible in `work_range`.
2. Refresh existing image/frame views only when their fingerprint differs.
3. Legacy views without a fingerprint are refreshed once and upgraded.

### Implementation (LibreOffice)

1. **`_render_fingerprint(doc, text, anchor, marks, mapper)`** — compute current fp string.
2. **`_decode_desc`** — parse `source` + `fp` from Description.
3. **`_format_clusters`** — insert views with fingerprint metadata.
4. **`_refresh_graphics_in_place` / `_refresh_frames_in_place`** — skip when fp matches; else redraw (current path).
5. **Tests** in [libreoffice/tests/](../libreoffice/tests/): mixed rendered/unrendered paragraph; font size change; toggle vertical page style.
6. Port same fingerprint idea to **Word** alt text and **ONLYOFFICE** tags after LO proves the model. **Done for inline-picture / inline-image paths.**

### Edge cases

- **Partial selection** spanning half a compound cluster — scope rules unchanged (`_range_contains`).
- **Multiple marks same base** — anchor granularity must be per cluster, not per character only.
- **Image vs frame legacy** — `use_image_renderer` may convert frame → graphic on refresh; fingerprint should survive conversion.

### Success criteria

- Paragraph `說㆒㆑者` rendered; user adds `学㆑` on same line; Render selection → only `学` cluster gets new view; `說` view unchanged if fp matches.
- User bumps paragraph font 12→14 pt; Render → all views in scope rescale; second Render immediately after → **no-op** (0 updated).
- Toggle 縦書き; Render → views reposition; stable after second Render.

---

## Cross-host parity matrix (target)

| Behaviour | LibreOffice | Word | ONLYOFFICE |
|-----------|-------------|------|------------|
| Empty selection → whole document Render | ✅ | ✅ | ✅ paragraph scan |
| Inline image / SVG compound stack | ✅ SVG | ✅ PNG | ✅ PNG |
| Incremental Render + skip if clean | ✅ | ✅ inline pictures | ✅ image/control metadata |
| Fingerprint in view metadata | ✅ Description | ✅ alt text | ✅ drawing name / SDT tag |

---

## Suggested order of work

1. **Word §2** — implemented.
2. **LibreOffice §3** — implemented.
3. **ONLYOFFICE §1** — implemented.

---

## Open questions

1. ~~Should **Refresh** remain a separate command?~~ **Resolved:** Word and ONLYOFFICE use a single **Render** button (render + smart refresh). LibreOffice **Refresh rendering** menu item remains an alias for **Format kaeriten**.
2. Whole-document Word Render: silent or confirmation dialog? (Currently silent, like LibreOffice.)
3. ONLYOFFICE image path: keep content-control fallback in `mapping.json` for older builds?
4. Store fingerprint in user-visible Description vs hidden property only?

---

## Changelog

| Date | Note |
|------|------|
| 2026-06 | Initial exploration from project discussion (OO images, Word scope, LO incremental render). |
| 2026-06 | Implemented Word whole-document Render, LO fingerprints, Word inline-picture fingerprints, and ONLYOFFICE inline-image renderer. |
