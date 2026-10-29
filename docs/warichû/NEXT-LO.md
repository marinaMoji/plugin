# LibreOffice next steps (release + upstream prep)

## Waiting on you

1. **Manual test 0.3.16** — [`RELEASE-0.3.16-CHECKLIST.md`](RELEASE-0.3.16-CHECKLIST.md). Do not publish until signed off.
2. **Review U1 Bugzilla draft** — [`upstream/U1-BUGZILLA-REVIEW.md`](upstream/U1-BUGZILLA-REVIEW.md) + native ODT in `upstream/u1-reproducer/`. File only after approval.
3. **Approve Ubuntu VM** — [`upstream/lo-build-vm/`](upstream/lo-build-vm/) (150–200 GiB). No paid provision / full `make` until you say so.

## Deferred

| Item | Status |
|---|---|
| File U2 kinsoku | After independent re-verify of B11/B19/B20 (not filed) |
| Implement scholarly mode | After maintainer discussion; summary ready |
| U1 patch compile | After VM build exists; keep separate from U2 |

## Shipped locally

- Extension **0.3.16** with caret-aware remove (`warichu.py`).
- Build: `libreoffice/./build.sh` → `dist/MarinaMojiKaeriten.oxt`.
