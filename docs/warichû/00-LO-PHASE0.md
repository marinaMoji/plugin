# Phase 0 — LibreOffice plugin reconnaissance

**Status:** Confirmed against repo sources and local LO install (2026-10-29).  
**Host under test:** LibreOffice Writer **26.8.0.3** (macOS), path `/Applications/LibreOffice.app`.  
**Extension:** `org.marinaMoji.kaeriten` **0.3.14** (`libreoffice/marinamoji_kaeriten/`).

Labels below: **confirmed** (read from repo/install), **inferred**, **unverified**.

## What exists today (confirmed)

| Piece | Location | Role |
|---|---|---|
| Macro module | `Scripts/python/marinamoji_kaeriten.py` (built into `.oxt`) | Render / unrender kaeriten, copy plain text, toggle page writing mode, composer insert |
| Export helpers | `export_core.py` | Plain-text / TEI / LaTeX helpers (dev; not toolbar) |
| Composer watcher | `composer_handoff.py` + `Jobs.xcu` | Insert SVG from marinaMoji profile on Writer focus |
| Toolbar | `Addons.xcu` + `marinamoji_kaeriten_dispatch.py` | Protocol `org.marinaMoji.kaeriten:` → four commands |
| Mapping | root `mapping.json` → `marinamoji_mapping.json` in bundle | Kaeriten glyph / layout metadata |
| Build | `libreoffice/build.sh` | Stages `dist/build/`, zips `MarinaMojiKaeriten.oxt` |
| Macros install | `libreoffice/install.sh` | Copies `.py` into LO user `Scripts/python/` (needed on LO 26.x macOS) |
| Tests | `libreoffice/tests/` | Pure Python (parser, export, composer handoff); **no live UNO tests** |
| Min LO | `description.xml` | LibreOffice **6.4+** |

### UI commands (confirmed)

- `render_kaeriten` / `unrender_kaeriten` / `copy_plain_text` / `toggle_page_writing_mode`
- Toolbar title: **marinaMoji**; Writer-only context
- Vertical toggle flips page style `WritingMode` between `LR_TB` (0) and `TB_RL` (2), then refreshes rendered kaeriten

### Design principle already in docs (confirmed)

From `docs/ARCHITECTURE.md`: **IME for input; extension for layout; Unicode source for meaning.** Kaeriten uses anchored images/frames as a *view*, with Unicode as source of truth.

**Implication for warichū:** planning docs require **native editable combine**, not image/table workarounds. That is a *different* strategy from kaeriten rendering — intentional, because warichū must remain searchable editable text. Do not reuse the image-frame pipeline as the primary warichū solution.

## Languages and runtime (confirmed)

- Extension logic: **Python 3** via LibreOffice’s bundled interpreter (`Contents/Resources/python`).
- System `python3` on this machine **does not** import `uno` — spikes must use LO’s Python or run inside Writer macros.
- UNO selection helpers already exist: `_get_document()`, `_get_selection_range()`, writing-mode detection (`_is_vertical_writing`).

## Warichū entry points (API-level confirmed; behaviour unverified until spike)

UNO `CharacterProperties` (optional):

- `CharCombineIsOn` — format text in two lines
- `CharCombinePrefix` / `CharCombineSuffix` — usually brackets around the combined span

ODF candidate (to verify on save): `style:text-combine="lines"` (distinct from `"letters"`).

**No** marinaMoji code currently sets these properties (repo grep: only planning docs mention them).

## Integration points for a future product feature (inferred)

1. Add spike/product helpers next to existing selection utilities in `marinamoji_kaeriten.py`, **or** a sibling module imported like `export_core` — prefer sibling until Gate 1 passes.
2. Register a toolbar command only after Gate 1 (Phase 2); keep throwaway code under `libreoffice/spikes/warichu/`.
3. Reuse `toggle_page_writing_mode` / `_is_vertical_writing` for T07 vertical fixtures.
4. Feature-gate anything beyond combine on/off + brackets until alignment experiments land.

## Risks (mixed)

| Risk | Status |
|---|---|
| Combine exists in IDL but alignment is host-owned | **confirmed** API surface; **unverified** renderer behaviour |
| No UNO integration tests in CI | **confirmed** |
| Kaeriten images adjacent to warichū may collide visually | **unverified** (fixture T06/T08 area) |
| DOCX export may lose combine details | **unverified** (T09) |
| Manual line break / per-glyph alignment unsupported in UNO | **hypothesis** (H1/H2 in investigation doc) |

## Smallest executable LO prototype

Headless (or GUI) script under `libreoffice/spikes/warichu/run_spike.py`:

1. Create Writer doc with fixture strings.
2. Apply `CharCombineIsOn` (+ optional prefix/suffix).
3. Read properties back; save `.odt`; reopen; re-read.
4. Dump ODF XML snippets mentioning `text-combine`.
5. Optionally export `.docx` and record fidelity.
6. Fill `capability_matrix.md`.

Screenshots for unequal-line alignment (T04) still need a GUI session — note as follow-up.

## Decision for next step

Proceed with **Phase 1 LO-only spike** first; Word spike deferred. Do **not** add toolbar warichū UI until Gate 1 evidence exists.

## Phase 1 automated results (confirmed, 2026-10-29)

Ran `libreoffice/spikes/warichu/warichu_spike_macro.py` inside Writer 26.8.0.3.

| Experiment | Result |
|---|---|
| T01 Insert `CharCombineIsOn` | **Verified** — property set succeeds; text stays editable Unicode |
| T02 Inspect | **Verified** — Prefix/Suffix round-trip on the range |
| T08 Save/reopen ODT | **Verified** — combine flag and brackets survive reopen |
| ODF persistence | **Verified** — `style:text-combine="lines"` with `text-combine-start-char` / `end-char` |
| T09 DOCX write | **Verified** that Writer can export; Word rendering **unverified** |
| T04 / T07 visual layout | **Failed** — first spike overlap (Songti / zh-CN). See `artifacts/screenshots/` |
| JP retest A/B/C | **A pass; B/C fail** when combine is on the **paragraph** style |
| Manual UI warichū | **Structurally pass** — combine on a **character span** (`text:span` + `style:family="text"`). See `artifacts/retest_jp/VERDICT.md` |
| T05 Manual break | Still unknown / limited |
| T10 | Unicode preserved; span-based combine editable |

**Platform caveat (confirmed):** launching `LibreOfficePython` as a Cursor or Terminal child fails with macOS `SIGKILL` / codesign launch constraint. Prefer in-process macros (`./run.sh`).

**Product implication (Gate 1 LO):** Native warichū **works** when applied like the UI: character range → `CharCombineIsOn` as a text span, not paragraph-wide. marinaMoji MVP should select annotation text (or body+note pattern), apply span combine + optional brackets. Do not set combine on the paragraph style. Fine row-gap/alignment still host-owned.

**Span spike v4 (2026-10-29):** `artifacts/span_spike/VERDICT.md` — **A pass** (bare `CharCombineIsOn` on note span); **B fail** (UNO `CharCombinePrefix`/`Suffix` collapses paint). Sticky cursor combine must be cleared on body runs. LO MVP: span combine without UNO bracket props.
