# Microsoft Marketplace (AppSource) — Word add-in maintainer guide

How to list **marinaMoji Kaeriten** in the **Microsoft 365 and Copilot** marketplace (formerly AppSource) via Partner Center.

**Audience:** maintainers.  
**Add-in code:** [word/](../word/)  
**Submission package:** [packaging/release/marketplace-word/](../packaging/release/marketplace-word/)  
**Do not** create Partner Center offers, deploy Pages, or submit for certification without explicit authorization.

---

## Mental model

```text
A. Hosted web app (GitHub Pages)
   JS / HTML / CSS / icons / mapping.json
   → users get updates automatically when Pages updates
   → no Partner Center resubmission for code-only fixes

B. Manifest (XML add-in only)
   Id, Version, URLs, ribbon, permissions, requirement sets
   → any change requires a new Marketplace submission + new Version
   → never change <Id> after first publish

C. Marketplace listing metadata
   screenshots, descriptions, store logo, privacy/support links
   → changing these also requires resubmission (with bumped manifest Version)
```

Official starting points:

- [Publish your Office Add-in to Microsoft Marketplace](https://learn.microsoft.com/en-us/office/dev/add-ins/publish/publish-office-add-ins-to-appsource)
- [Microsoft 365 app publishing checklist](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/checklist)
- [Step-by-step submission guide](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/add-in-submission-guide)
- [Submission FAQ](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/appsource-submission-faq)
- [Certification policies §1120 Office Add-ins](https://learn.microsoft.com/en-us/legal/marketplace/certification-policies)
- [Open an Office account in Partner Center](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/open-a-developer-account)

---

## Stable identifiers (do not change after first Marketplace publish)

| Field | Value | Why |
|-------|--------|-----|
| **Add-in Id** | `7f3c8b2a-9d4e-4f1a-b6c2-8e5a1d3f9b7c` | Changing Id creates a *different* add-in |
| **DisplayName** | `marinaMoji Kaeriten` | Must match Partner Center offer name closely |
| **ProviderName** | `marinaMoji` | Must match Partner Center publisher name |
| **Slogan** | Make room for character | Listing copy |
| **Hosted base URL** | `https://marinamoji.github.io/plugin/word` | Production `SourceLocation` |
| **SupportUrl** | `https://marinamoji.crcao.fr/en/support` | Must **not** be a GitHub repo URL |
| **Manifest format** | Add-in only **XML** (schema 1.1) | Unified JSON is optional; not required for a Word-only add-in |

**Marketplace Version** (manifest `<Version>`) must be `a.b.c.d` with **a ≥ 1**. First Marketplace candidate: **`1.0.0.0`**. Internal npm/`version.json` may still say `0.1.3` until you align them deliberately.

---

## Distribution mechanism (confirmed against current docs)

| Question | Answer |
|----------|--------|
| Where to publish? | Partner Center → **Microsoft 365 and Copilot** program → Office Add-in offer |
| Unified manifest required? | **No** for a standalone Word add-in. XML add-in-only remains valid for production Word |
| GitHub Pages OK? | **Yes**, if HTTPS and publicly reachable (already used) |
| Microsoft Entra app registration? | **Not required** for this add-in (no SSO / Graph) |
| Same account as Windows IME Store listing? | Often the **same Partner Center tenant** can enroll in multiple programs; you must still enroll in **Microsoft 365 and Copilot**. Confirm in Account settings → Programs |
| Publisher verification (Entra blue badge)? | Optional / recommended when using Entra apps; not a substitute for Partner Center enrollment |
| Fees for free listing? | Microsoft states **no cost to publish**; store fee applies to **paid/transact** offers (this add-in is free) |
| Special OSS rules? | No fee waiver special-case found; still need privacy, support, EULA/Standard Contract, working add-in |

---

## What was fixed for validation (local)

Microsoft’s `office-addin-manifest validate` now reports **The manifest is valid** for `word/marinamoji-kaeriten-word.xml` after:

1. Removing invalid **`WordApiDesktop`** activation requirement (XML cannot declare platform-specific sets; runtime checks remain in code).  
2. Setting **`WordApi` MinVersion `1.2`** (inline picture API).  
3. Placing **`<Requirements>`** before **`<DefaultSettings>`** / **`<Permissions>`**.  
4. Using **`VersionOverridesV1_0`** with Resources order **Images → Urls → ShortStrings → LongStrings**.  
5. Using **`<OfficeTab id="TabHome">`** (schema accepted form).  
6. Setting **`<Version>1.0.0.0</Version>`** (Marketplace rejects `0.x`).  
7. Replacing GitHub **SupportUrl** with the project support page.  
8. Replacing solid-colour placeholder icons with the marinaMoji mark.  
9. Loading **Office.js from Microsoft CDN only** (Marketplace FAQ).

---

## Submission package layout

```text
plugin/packaging/release/marketplace-word/
  marinamoji-kaeriten-word.xml   # production manifest to upload
  icons/                         # store + ribbon sizes
  screenshots/                   # place screen_1_1366x768.png here
  listing/                       # EN / FR / JA copy
  docs/
    PARTNER_CENTER_WALKTHROUGH.md
    CERTIFICATION_CHECKLIST.md
    RELEASE_AND_UPDATES.md
    MANUAL_QA.md
    PRIVACY_AND_SECURITY.md
    ISSUES_PLAN.md
```

---

## Blockers before submit

1. **Deploy site** so `https://marinamoji.crcao.fr/en/support` and `…/en/privacy` return 200 (pages drafted under `site/user/pages/`).  
2. **Deploy GitHub Pages** so production icons and CDN-only HTML match this branch.  
3. **Capture** one genuine Word screenshot at **1366×768**.  
4. **Manual QA** on Word Windows and Word on the web (Mac QA previously passed; iPad may be tested by Microsoft because the manifest activates there).  
5. **Partner Center** enrollment in Microsoft 365 and Copilot (manual).  
6. Confirm **ProviderName** `marinaMoji` matches the publisher display name you register.

---

## Related docs

- [WORD_ADDIN_DEV.md](WORD_ADDIN_DEV.md) — sideload / Mac QA  
- [GITHUB_PAGES.md](GITHUB_PAGES.md) — hosting  
- [STATUS.md](STATUS.md) — host readiness  
- [WORD_PLUGIN_RESEARCH.md](WORD_PLUGIN_RESEARCH.md) — earlier AppSource notes (superseded here where they conflict with 2025–2026 Learn docs)
