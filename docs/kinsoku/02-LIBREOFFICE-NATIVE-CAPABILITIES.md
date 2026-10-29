# LibreOffice Writer — native Japanese composition capabilities

**Environment:** LibreOffice **26.8.0.3** (`bce0998afefdbc355585ca324285661a2170ba77`), macOS.  
**Prerequisite:** Asian language support enabled  
(`LibreOffice → Preferences → Languages and Locales → General → Asian`).

Confidence: **Confirmed** (IDL / ODF / Help / source on `core` master, inspected 2026-10-29) · **Observed** (Help wording) · **Pending experiment** (corpus render).

Source revision note: Writer/i18npool cites are from LibreOffice `core` **master** raw files (same paths as 26.8 tree). Behaviour should be verified on 26.8.0.3 with the Stage E1 corpus; do not assume bit-identical layout across every release.

---

## UI locations (LO 26.8 Help, local `en-US`)

| Topic | UI path |
|---|---|
| Enable Asian support | Preferences → Languages and Locales → **General** → Asian |
| Global forbidden lists + compression defaults | Preferences → Languages and Locales → **Asian Layout** |
| Per-paragraph toggles | **Format → Paragraph → Asian Typography** (also paragraph style → Asian Typography) |

### Asian Layout (application defaults)

From [Asian Layout help](https://help.libreoffice.org/latest/en-US/text/shared/optionen/01150100.html) and local `01150100.html`:

- **Not at start of line** / **Not at end of line** character lists (per language; “Default” fills locale defaults).
- **Character spacing / compression:** No compression | Compress only punctuation | Compress punctuation and Japanese Kana.
- Kerning: Western only | Western + Asian punctuation.

**Scope:** application-level defaults.  
**marinaMoji rule:** never silently rewrite these global Options.

### Asian Typography (paragraph / style)

From local Help `05020700.html` (LO 26.8):

- Apply list of forbidden characters to beginning and end of line.
- Allow hanging punctuation (Help: “Prevent commas and periods from breaking the line… added to the end of the line, even in the page margin”).
- Apply spacing between Asian and non-Asian text.

Ignored in HTML documents (Help).

---

## UNO — paragraph Asian properties

Service: [`com.sun.star.style.ParagraphPropertiesAsian`](https://api.libreoffice.org/docs/idl/ref/servicecom_1_1sun_1_1star_1_1style_1_1ParagraphPropertiesAsian.html)  
(**Confirmed** IDL)

| Property | Type | Meaning |
|---|---|---|
| `ParaIsForbiddenRules` | `boolean` | Apply forbidden start/end characters when breaking lines |
| `ParaIsHangingPunctuation` | `boolean` | Allow hanging punctuation |
| `ParaIsCharacterDistance` | `boolean` | Distance between Asian and Western/complex text |

**Scope:** paragraph direct formatting and paragraph styles.  
**Read-only inspection:** ordinary `XPropertySet` getters — **Confirmed** API shape. Effective-vs-style merge: treat cursor property values as the **effective** formatting Writer applies (**Pending** Prototype A confirmation on style inheritance edge cases).

---

## UNO — document settings (compression, kerning, forbidden lists)

Service: [`com.sun.star.document.Settings`](https://api.libreoffice.org/docs/idl/ref/servicecom_1_1sun_1_1star_1_1document_1_1Settings.html) (**Confirmed**)

| Property | Type | Meaning |
|---|---|---|
| `ForbiddenCharacters` | `i18n::XForbiddenCharacters` | Per-locale begin/end lists for this document |
| `CharacterCompressionType` | `short` | See constants below |
| `IsKernAsianPunctuation` | `boolean` | Kern Asian punctuation when kerning is on |

Constants [`text::CharacterCompressionType`](https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1text_1_1CharacterCompressionType.html):

| Value | Name | Meaning |
|---|---|---|
| 0 | `NONE` | No compression |
| 1 | `PUNCTUATION_ONLY` | Compress punctuation |
| 2 | `PUNCTUATION_AND_KANA` | Compress punctuation and Japanese kana |

**Scope:** **document** settings (not the three paragraph booleans). UI “Asian Layout” compression seeds defaults; documents can carry `CharacterCompressionType` via settings export (**Confirmed** IDL; round-trip **Pending** corpus).

`XForbiddenCharacters` methods: `getForbiddenCharacters(Locale)`, `hasForbiddenCharacters`, `setForbiddenCharacters`, `removeForbiddenCharacters` — **Confirmed**. Stage E1 prototypes must **read only**.

---

## Locale default lists (`ja_JP`)

From LibreOffice `i18npool/source/localedata/data/ja_JP.xml` (**Confirmed**, `core` master = same content as `libreoffice-26-8` branch fetch):

**ForbiddenLineBeginCharacters** (excerpt of Japanese-relevant subset):  
`、。々〉》」』】〕ぁぃぅぇぉっゃゅょゎ…ァィゥェォッャュョヮヵヶ・ーヽヾ` plus ASCII/fullwidth punct and halfwidth kana smalls.

**ForbiddenLineEndCharacters:**  
`$([¥{£¥‘“〈《「『【〔＄（［｛｢£￥`

**LineBreakHangingCharacters:** `、。，．`

`LocaleDataImpl::getForbiddenCharacters` returns begin/end; `getHangingCharacters` returns the third string ([`localedata.cxx`](https://docs.libreoffice.org/i18npool/html/localedata_8cxx_source.html)).

Writer’s CJK break iterator loads hanging chars for `ja_JP` in `BreakIterator_CJK` constructor ([`breakiterator_cjk.cxx`](https://raw.githubusercontent.com/LibreOffice/core/master/i18npool/source/breakiterator/breakiterator_cjk.cxx)).

---

## ODF 1.2 paragraph attributes

From [ODF 1.2 Part 1](https://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html) and LO `xmloff/.../txtprmap.cxx` (**Confirmed** mapping):

| UNO | ODF attribute | Values |
|---|---|---|
| `ParaIsForbiddenRules` | `style:line-break` (§20.307) | `normal` \| `strict` |
| `ParaIsHangingPunctuation` | `style:punctuation-wrap` (§20.327) | `simple` \| `hanging` |
| `ParaIsCharacterDistance` | `style:text-autospace` (§20.355) | `none` \| `ideograph-alpha` |

Document `ForbiddenCharacters` / `CharacterCompressionType` export via settings helper (`SettingsExportHelper::exportForbiddenCharacters`) — **Confirmed** code path; exact ODF element names in settings.xml **Pending** sample dump.

Also related: `style:layout-grid-*` page attributes; `style:snap-to-layout-grid`.

---

## Implementation path (Writer layout)

### Body line break — **Confirmed**

1. `SwTextGuess` (`sw/source/core/text/guess.cxx`) loads document forbidden characters for the language, builds `LineBreakUserOptions` with:
   - `beginLine` / `endLine` from `ForbiddenCharacters`
   - `HasForbiddenChars()` ← paragraph `ParaIsForbiddenRules`
   - hanging allowed only if `IsHanging() && !IsMulti() && !IsInTab() && !InFieldGrp()`
2. Calls `XBreakIterator::getLineBreak` → CJK implementation in `i18npool/.../breakiterator_cjk.cxx`:
   - Optionally allows hanging punctuation (`allowPunctuationOutsideMargin` + hanging set).
   - If `applyForbiddenRules`, walks back while break would leave a forbidden begin or end character.
   - Falls back to ICU Unicode break iterator.
3. If break index advances past cut for hanging, Writer creates `SwHangingPortion`.

### Multiportion (warichū / ruby / rotate) — **Confirmed** limitation

`bAllowHanging = … && ! rInf.IsMulti()` — **hanging punctuation is disabled inside multiportions**.

Warichū **reuses** `BuildPortions` → `SwTextGuess::Guess` → `getLineBreak` (same forbidden lists when rules are on), but `BuildMultiPortion` has **no** warichū-specific post-filter for not-start at the head of inner line 2; width search + `IsFirstMulti` can still yield B11/B19/B20. Treat as **shared engine, different flags / no post-pass** — not “kinsoku fully absent in warichū.”

### Application Options (`AsianLayout`)

Registry under `org.openoffice.Office.Common/AsianLayout` (local `main.xcd`): `CompressCharacterDistance`, `IsKerningWesternTextOnly`, per-locale `StartCharacters` / `EndCharacters`. New documents seed document settings from these ([capability draft](36f96299-1481-4f0a-8295-66ffdb4a955b)). **Never rewrite from marinaMoji.**

### Punctuation compression — **Confirmed** API, behaviour Pending

- Document `CharacterCompressionType` + Options Asian Layout.
- `guess.cxx` references “maximum compression (for kanas)” when measuring fit — algorithm detail needs corpus observation, not screenshot inference alone.

---

## Vertical writing

- Same paragraph Asian properties; Help does not provide separate H/V toggles.
- Glyph orientation is largely font/writing-mode; hanging/forbidden logic is writing-mode agnostic in the break iterator (operates on string indices).
- Behavioural H vs V differences (hanging ink, grids): **Pending** corpus K09.

---

## DOCX

- Expect imperfect round-trip of Asian paragraph toggles and document forbidden lists.
- Do not rely on DOCX for Stage E1 evidence; prefer ODT.

---

## Capability matrix

| Feature | Writer native | UNO access | ODF | Vertical | Inspector (settings) | Inspector (layout) |
|---|---|---|---|---|---|---|
| Line-start/end prohibitions | **Yes** (locale lists + `ParaIsForbiddenRules`) | Paragraph bool + doc `ForbiddenCharacters` | `style:line-break` | Same API; render Pending | **Feasible** | Needs reliable line geometry |
| Hanging punctuation | **Yes** (body); **off** in multiportion | `ParaIsHangingPunctuation` | `style:punctuation-wrap` | Pending | **Feasible** | Needs geometry |
| Asian–Western spacing | **Yes** | `ParaIsCharacterDistance` | `style:text-autospace` | Pending | **Feasible** | Heuristic |
| Punctuation compression | **Yes** (doc/Options) | `CharacterCompressionType` | settings export | Pending | **Feasible** (read doc setting) | Hard |
| Line adjustment | Built-in (justify + CJK break) | Indirect | Indirect | Pending | N/A | Hard |
| Rendered line boundaries | Internal only | **Weak / unreliable for production** | N/A | See `08` | — | See `08` |
| Warichū internal breaks | Separate path; kinsoku-unsafe cases known | No break index | Combine attrs only | Stage B observed | Textual / advisory | Soft only |

---

## Architectural caution for marinaMoji

1. Prefer **reading** paragraph properties and document ForbiddenCharacters / compression over writing Options.  
2. Changing global Asian Layout alters the user’s whole LO profile — out of scope.  
3. “Forbidden rules off” is a **configuration finding**, not a layout defect.  
4. Never treat multiportion-internal breaks as proof that body kinsoku is broken.  
5. Do not silently treat a missing property as “disabled.”
