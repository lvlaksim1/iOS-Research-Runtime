# PP-RM Launch Package — generation 19

Status: PREPARED / LIVE-FIRST
Manager generation: 20
Package: `IOS-M2-CONTINUOUS-009`
Product baseline: `main@95caa93fc8fd0db827491e679628efa40612b55c`
Previous package: `IOS-M1-CONTINUOUS-008` — FINAL_COMPLETED / MUST NOT RESUME

## Mission
IOS-M2 — Full iOS Boot Boundary.

Determine the first verified technical boundary between the working recovery/root-shell environment and full iOS system userland.

## Acceptance
Complete IOS-M2 when exact runtime evidence establishes either:
- progression into full system userland/system-launchd territory; or
- the first concrete blocking dependency with enough reproducible evidence to define the next bounded mutation without speculation.

## First bounded step
Preserve the proven IOS-M1 root-shell path and add a post-root diagnostic probe for mounts/filesystem topology, system/preboot paths, visible disk/device nodes and launchd/service state.

Push the smallest diagnostic change to `main`, consume exact-SHA Windows E2E evidence, then classify the boundary before changing QEMU, provisioning or security semantics.

## Execution ownership
The direct Owner-facing live runtime owns the first bounded step.
Workers A/B and Watchdog remain unarmed while this live carrier performs the same work.
If execution reaches an external-evidence wait or continuity boundary, the Manager may activate this clean package using the retained generation16–19 protocol and a fresh activation tuple.

## Runtime architecture retained
- generation16 native two-phase mutation;
- generation17 recurring-backstop Watchdog;
- generation18 result-first workflow evidence;
- generation19 WAIT_EXTERNAL_EVIDENCE;
- OCB3.

## Supersession
Packages005,006,007 and completed package008 MUST NOT resume.
