# Manager intentions and commitments

## Completed

### IOS-M1 — first Windows boot milestone
- status: COMPLETED
- objective: verified recovery `launchd` plus verified root shell on Windows
- authoritative product: `main@95caa93fc8fd0db827491e679628efa40612b55c`
- evidence: Windows End-to-End Boot run `36844422600`, job `110311023233`
- semantic result: SUCCESS
- workflow conclusion: FAILURE only because of post-proof QEMU/harness nontermination

### IOS-PP-RM-005 — generation19 persistent external-evidence wait
- status: IMPLEMENTED / VALIDATED IN PRODUCTION
- package008 completed successfully under generation19 semantics

## Active

### IOS-M2 — Full iOS Boot Boundary
- status: ACTIVE
- owner authorization: direct Owner directive on 2026-10-01 after roadmap review
- start baseline: `main@95caa93fc8fd0db827491e679628efa40612b55c`
- objective: determine the first verified technical boundary between the working recovery/root shell and full iOS system userland
- acceptance A: demonstrate progression into full system userland/system-launchd territory with exact runtime evidence; or
- acceptance B: identify the first concrete blocking dependency with reproducible evidence sufficient to define the next bounded engineering mutation
- first method: collect post-root evidence before speculative QEMU or firmware changes
- initial probe scope: mounts/volumes, system/preboot paths, disk/device exposure, launchd/service state
- reserved successor package: `IOS-M2-CONTINUOUS-009`

## Superseded runtime packages
Packages005,006,007 and completed package008 must not resume.

## OCB
Explicit safety/safety-check block only; max three exact-identical attempts; no automatic fourth; reconcile ambiguous mutable side effects before replay.
