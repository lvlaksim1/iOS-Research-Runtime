# Current state

Updated: 2026-10-01 15:12 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 20
- product authority: `main`
- product baseline at IOS-M2 start: `95caa93fc8fd0db827491e679628efa40612b55c`
- PP-RM architecture: generation19 persistent external-evidence wait + generation18 result-first evidence + generation17 recurring Watchdog + generation16 native two-phase mutation
- execution status: ACTIVE / IOS-M2
- active milestone: `IOS-M2 — Full iOS Boot Boundary`
- reserved successor package: `IOS-M2-CONTINUOUS-009`
- current carrier: direct Owner-facing live runtime

## Completed foundation
IOS-M1 remains COMPLETE on `main@95caa93fc8fd0db827491e679628efa40612b55c`.
Exact-SHA E2E run `36844422600`, job `110311023233`, proved recovery Darwin, launchd, interactive root shell, Darwin uname, `whoami=root`, root filesystem listing and `__IOS_RESEARCH_PROOF_END__`.

## Active IOS-M2
Owner approved the roadmap and authorized execution on 2026-10-01.

Objective: establish the first verified boundary after the recovery root shell on the path toward full iOS system userland.

Immediate action:
- extend the E2E integration harness with a bounded post-root diagnostic probe;
- collect mounts/volumes, system/preboot paths, disk/device exposure and launchd/service state;
- trigger exact-SHA Windows E2E through the normal `main` push path;
- classify the first concrete blocker before changing QEMU or firmware semantics.

## Known residual issues
- QEMU/integration harness may not terminate cleanly after semantic proof.
- repeated `AppleSEPManager` endpoint timeouts occur.
These remain observations until IOS-M2 evidence establishes whether either is the first blocking dependency.

## Superseded PP-RM state
Package008 is terminal `FINAL_COMPLETED`.
Packages005,006,007 are terminal/superseded and must not resume.
