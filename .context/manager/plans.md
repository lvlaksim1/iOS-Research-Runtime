# Manager plans

## Current planning state

Manager generation: 20.
Product baseline: `main@95caa93fc8fd0db827491e679628efa40612b55c`.
IOS-M1 status: COMPLETED.
IOS-M2 status: ACTIVE.
Execution carrier: current direct Owner-facing runtime for the first IOS-M2 probe.
Reserved successor package: `IOS-M2-CONTINUOUS-009`.

## IOS-M2 strategy — Full iOS Boot Boundary

### Phase 1 — instrument the proven root shell
Extend the Windows E2E integration harness so the already verified shell emits bounded evidence for:
- current mounts and filesystem topology;
- `/System/Volumes`, `/private/preboot` and related system paths when present;
- visible disk/device nodes;
- current launchd/service inventory.

Preserve the existing IOS-M1 proof. Do not require speculative QEMU hardware changes.

### Phase 2 — exact-SHA E2E
Push the probe to `main` and consume the normal Windows E2E result for that exact SHA.
Runtime logs remain evidence even if the workflow later fails from the known post-proof termination defect.

### Phase 3 — classify the boundary
Classify the first evidenced boundary as provisioning/material, storage exposure/mounting, launchd/bootstrap, trust/security/SEP, QEMU hardware behavior, or another directly evidenced class.
Do not select a fix before classification.

### Phase 4 — bounded mutation
Implement the smallest change that addresses the evidenced first blocker and verify it with a fresh exact-SHA Windows E2E run.

### Phase 5 — milestone decision
IOS-M2 completes when either full system-userland progression is demonstrated or the first concrete blocker is reproducibly isolated well enough to define the next bounded milestone.

## Later roadmap
After IOS-M2: full system/root filesystem → core services → graphics/input → SpringBoard → interactive iOS → Apple-service feasibility → Windows productization → reliability/release. These later stages are not yet active commitments.

## PP-RM
If the current live runtime reaches an external-evidence wait or continuity boundary, activate clean package009 using generation16–19 semantics. Never resume package008 or earlier packages.

## OCB
Explicit safety/safety-check block only; up to three exact-identical attempts total; no fourth automatic request; reconcile mutable side effects before replay.
