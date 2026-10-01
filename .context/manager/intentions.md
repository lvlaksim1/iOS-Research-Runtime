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
- status: ACTIVE / WAIT_EXTERNAL_EVIDENCE
- owner authorization: direct Owner directive on 2026-10-01 after roadmap review
- start baseline: `main@95caa93fc8fd0db827491e679628efa40612b55c`
- current product: `main@24730a74051378d228efd370f3baee5a4f46bdfa`
- objective: determine the first verified technical boundary between the working recovery/root shell and full iOS system userland
- acceptance A: demonstrate progression into full system userland/system-launchd territory with exact runtime evidence; or
- acceptance B: identify the first concrete blocking dependency with reproducible evidence sufficient to define the next bounded engineering mutation
- first diagnostic mutation: published; post-root probe added without changing QEMU/firmware semantics
- expected evidence: Windows End-to-End Boot on exact head `24730a74051378d228efd370f3baee5a4f46bdfa`
- active runtime package: `IOS-M2-CONTINUOUS-009`

## Superseded runtime packages
Packages005,006,007 and completed package008 must not resume.

## OCB
Explicit safety/safety-check block only; max three exact-identical attempts; no automatic fourth; reconcile ambiguous mutable side effects before replay.
