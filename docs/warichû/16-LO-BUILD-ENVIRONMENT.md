# LibreOffice development environment (Stage C)

**Date:** 2026-10-29  
**Machine:** macOS, ~51 GiB free on Data volume (disk ~95% full).  
**Installed binary:** LibreOffice **26.8.0.3** (`bce0998afefdbc…`) — **do not modify**.  
**Source tree on disk:** **None** (`~/lo`, `~/libreoffice`, `~/Code/libreoffice*` absent).

## Verdict

A suitable LibreOffice **source build environment does not exist** on this machine yet.  
Stage C **cannot** compile or run a patched `soffice` here without a dedicated setup and substantial disk/time.

## Least expensive reproducible setup (proposed)

| Option | What | Approx. cost | Notes |
|---|---|---|---|
| **A. Cloud/VM with large disk** (recommended first) | Ubuntu 22.04+ VM, 100 GB+, 8+ cores, clone `core`, `autogen` + `make` | Disk **40–80 GB**; first build **2–8 h** depending on cores/ccache | Keeps Mac disk free; matches TDF wiki |
| **B. Local macOS build** | Xcode CLT, brew deps, clone core | Disk **50 GB+** free required; first build **several hours** | This Mac currently has **insufficient free space** for a comfortable build |
| **C. Gerrit draft only** | Analyze + write patch; ask LO developer to try | Hours of analysis, zero local compile | Acceptable interim; cannot claim “patch works” |

**Do not start a multi-hour local compile on this Mac until ≥80 GB free (or external volume) is available.**

Official guide: https://wiki.documentfoundation.org/Development/BuildingOnMac  
Linux: https://wiki.documentfoundation.org/Development/GenericBuildingGuide

## Tools already present

- `git`, `ninja`, `autoconf` (Homebrew)  
- No LO `core` checkout, no evidence of prior `instdir` / ccache LO objects

## Stage C policy

- Experimental patches live under `docs/warichû/upstream/` as **text patches + notes**, not applied to `/Applications/LibreOffice.app`.  
- “Delimiter patch works?” → **Not verified** until a build env exists.  
- Root-cause hypothesis and minimal patch sketch are in `17-DELIMITER-PATCH-NOTES.md`.
