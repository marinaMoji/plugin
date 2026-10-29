# Scholarly use cases — classical Japanese, kanbun, diplomatic transcription

**Status:** planning notes for profiles (no UI in Stage E1).

## Classical Japanese

Modern kinsoku / full-width punctuation assumptions often **do not** fit:

- Unpunctuated or lightly punctuated sources.
- Editorial punctuation added by modern editors.
- Historical kana, iteration marks, variant characters.
- Mixed Sino-Japanese orthography.

**Inspector stance:** advisory only. Prefer messages like “differs from the selected modern composition convention,” never “incorrect punctuation.”

Rules that should **vary by profile:**

- Mixed half/full-width Japanese punctuation warnings.
- Strict small-kana / 々 / ー line-start warnings (JLREQ itself documents relaxation).
- Expectations for Western-style `,.` in Japanese prose.

## Kanbun and kundoku

marinaMoji already supports kaeriten. Ordinary Japanese kinsoku must **not** be applied blindly to:

- Classical Chinese base text.
- Reading marks / kaeriten / okurigana as if they were body punctuation.
- Vertically stacked annotation systems.

**Integration points (do not implement now):**

- Detect kaeriten spans via existing marinaMoji formatting markers before emitting `KINSOKU_*` findings.
- Profile `kanbun`: suppress body-punctuation consistency rules on mark characters; keep layout settings inspection.

**Do not modify** the kaeriten implementation during Stage E.

## Diplomatic transcription

Intentional unconventional spacing or punctuation is a feature, not a bug.

Preferred model:

> This punctuation arrangement differs from the selected composition convention.

Not:

> This punctuation is wrong.

Profile `diplomatic` should default most punctuation-consistency rules to **off** or informational-only.

## Profile sketch (future)

| Profile | Strict line-start small kana | Mixed-width punct | Explicit break before `。` | Warichū advisory |
|---|---|---|---|---|
| modern_ja | on (optional) | on | on | on |
| classical_ja | off | optional | optional | on |
| kanbun | off for marks | off for marks | optional | on |
| diplomatic | off | off | off | optional |

Universal (all profiles): read-only reporting of paragraph Asian settings; never auto-normalize Unicode.
