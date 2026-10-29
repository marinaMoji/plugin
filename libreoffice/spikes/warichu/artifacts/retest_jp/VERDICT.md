# JP retest verdict (updated 2026-10-29)

**Host:** LibreOffice Writer 26.8.0.3 · macOS · Hiragino Mincho ProN · Japanese

## Automated sections A/B/C
| Block | Result |
|---|---|
| **A** plain | Pass |
| **B/C** combine on whole paragraph | **Fail** — illegible overlap |

Cause (ODF): our spike set `style:text-combine="lines"` on **paragraph** automatic styles (`style:family="paragraph"`), with the whole run as the paragraph contents and no `text:span`.

## Manual UI test (user)
Pattern in saved ODT:

```xml
<text:p text:style-name="P10">割り注
  <text:span text:style-name="T1">割り注は、良いです。</text:span>
</text:p>
```

- `P10`: paragraph, `text-combine="none"`
- `T1`: **character** style (`style:family="text"`), only `style:text-combine="lines"`

**Result:** structurally correct warichū (two mini-rows after body text). Internal row spacing still a bit tight/overlap-y, but usable as a starting point. Screenshot: `screenshots/manual_UI_structurally_ok.png`.

## Conclusion
Native Writer warichū **is viable**. The plugin must apply combine as a **character-range / text span**, not as a paragraph property. Gate 1 LO reopened for a span-based apply/remove MVP; fine alignment control still host-limited.
