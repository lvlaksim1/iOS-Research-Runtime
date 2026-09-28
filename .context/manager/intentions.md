# Manager intentions and commitments

## Completed
- `MIG-IOS-001` — completed.
- IOSPM-001 protected-state adoption — completed and independently closed.

## Active

### IOS-M1
- status: accepted/active
- responsibility: `ios-research-runtime-project-manager`
- goal: verified recovery `launchd` plus verified root shell on Windows.
- current baseline: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`.
- historical restoration evidence: `d743b2e...` plus `b3befaeb...`.

### IOS-PP-RM-001
- status: accepted/active
- responsibility: `ios-research-runtime-project-manager`
- current stage: PREPARED / NOT ARMED.
- admission gate: run `IOS-PP-RM-PILOT-001`, verify PP-RM invariants, analyze Scheduler <-> GitHub passability and OCB evidence, then decide whether to refine OCB handling and admit `IOS-M1-R1`.
- OCB objective: reduce practical OSB/OCB impact on successful Scheduler <-> GitHub requests without sacrificing correctness.
- production package `IOS-M1-R1`: QUEUED / NOT ARMED until Manager admission.

## Superseded
The retired `ai-agent-lab` rotating shift-worker/OTK factory remains superseded and must not be re-enabled.
