# Manager intentions and commitments

## Completed

### IOS-M1 — first Windows boot milestone
- status: COMPLETED
- objective: verified recovery `launchd` plus verified root shell on Windows
- authoritative product: `main@95caa93fc8fd0db827491e679628efa40612b55c`
- evidence: Windows End-to-End Boot run `36844422600`, job `110311023233`
- semantic result: SUCCESS
- verified: launchd, spawned bash, interactive root shell, Darwin uname, `whoami=root`, root filesystem listing, proof-end marker
- workflow conclusion: FAILURE only because of post-proof QEMU/harness nontermination
- completion accepted by PP-RM generation8 `FINAL_COMPLETED`

### IOS-PP-RM-005 — generation19 persistent external-evidence wait
- status: IMPLEMENTED / VALIDATED IN PRODUCTION
- package008 completed successfully under generation19 semantics
- generation16 two-phase mutation, generation17 recurring Watchdog, generation18 result-first evidence and generation19 WAIT_EXTERNAL_EVIDENCE remain available for future packages

## Active
No active product implementation commitment.

## Pending Owner/Manager decision
Select the next product milestone. Do not infer or auto-select whether it should be harness stabilization, AppleSEPManager, additional services, SpringBoard/GUI, packaging, or another direction.

## Superseded runtime packages
Packages005,006,007 and completed package008 must not resume.

## OCB
Explicit OSB only; max three exact-identical attempts; no automatic fourth; reconcile ambiguous mutable side effects before replay.
