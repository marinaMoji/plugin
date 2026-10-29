# LibreOffice Writer build — isolated Ubuntu VM (plan)

**Goal:** Reproduce and fix **U1** (delimiter paint) without compiling on the marinaMoji Mac.  
**Do not** provision paid cloud or start a full build until you approve sizes/cost.

## Recommended VM shape

| Resource | Target |
|---|---|
| OS | Ubuntu **22.04 LTS** or **24.04 LTS** (x86_64) |
| Disk | **150–200 GiB** (source + `instdir` + ccache) |
| RAM | **16–32 GiB** |
| CPU | **8 cores** (more helps) |
| Network | Needed for `git clone` and dependency packages |

Local Mac currently has ~50 GiB free — **unsuitable** for a full `core` build.

## Scripts in this folder

| Script | Purpose |
|---|---|
| `01-install-deps.sh` | Apt build dependencies (TDF wiki set) |
| `02-clone-core.sh` | Clone LibreOffice `core`; optional checkout of a tag near 26.8 |
| `03-autogen-make.sh` | `autogen` + parallel `make` (long) |
| `04-run-tests.sh` | Placeholder for Writer/layout tests once U1 has a Cppunit/UITest |
| `05-run-instdir.sh` | Launch experimental `soffice` with **isolated** user profile |

All scripts are **idempotent where practical** and refuse to run if disk looks too small.

## Suggested source revision

For matching the bug host: start from a **26.8** branch/tag close to  
`bce0998afefdbc355585ca324285661a2170ba77` if published as a tag; otherwise `libreoffice-26-8` branch tip and note the exact `git rev-parse HEAD` in the bug.

```bash
# after clone
git fetch --tags
git checkout libreoffice-26-8   # or a specific tag once confirmed
git rev-parse HEAD
```

## Build cost (order of magnitude)

| Phase | Wall time (8 cores, rough) |
|---|---|
| Deps + clone | 15–60 min |
| First full build | **2–8 h** |
| Incremental rebuild after small `pormulti.cxx` edit | minutes–tens of minutes |

## Workflow once approved

1. Create VM (your hypervisor/cloud of choice).  
2. Copy this folder to the VM.  
3. Run `01` → `02` → `03` (after explicit go-ahead for the long `make`).  
4. Open `u1_text_combine_brackets_collapse.odt` in `instdir` build.  
5. Patch U1 only; keep U2 separate.  
6. Run `05-run-instdir.sh` for before/after screenshots.

## References

- https://wiki.documentfoundation.org/Development/GenericBuildingGuide  
- https://wiki.documentfoundation.org/Development/Linux  
- https://wiki.documentfoundation.org/Development/How_to_debug  
