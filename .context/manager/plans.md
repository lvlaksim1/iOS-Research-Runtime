# Manager plans

## Current planning state

Manager generation: 21.
IOS-M1 status: COMPLETED.
IOS-M2 status: ACTIVE / WAIT_EXTERNAL_EVIDENCE.
Product authority: `main@24730a74051378d228efd370f3baee5a4f46bdfa`.
PP-RM package: `IOS-M2-CONTINUOUS-009`.

## IOS-M2 strategy — Full iOS Boot Boundary

### Phase 1 — post-root probe
COMPLETED as product mutation. Commit `24730a74051378d228efd370f3baee5a4f46bdfa` preserves the IOS-M1 root proof and adds bounded markers/commands for:
- current mounts/filesystem topology;
- `/System/Volumes`;
- `/private/preboot`;
- visible `/dev/disk*` nodes;
- `launchctl list`.

No QEMU hardware, firmware provisioning or security semantics were changed.

### Phase 2 — exact-SHA E2E
ACTIVE. Await Windows End-to-End Boot evidence whose exact head is `24730a74051378d228efd370f3baee5a4f46bdfa`.
PP-RM package009 is initialized in `WAIT_EXTERNAL_EVIDENCE`; Watchdog owns evidence waiting and resumes Worker A only when terminal exact-SHA evidence exists.

### Phase 3 — classify the boundary
From the exact runtime output classify the first evidenced boundary as provisioning/material, storage exposure/mounting, launchd/bootstrap, trust/security/SEP, QEMU hardware behavior, or another directly evidenced class.
Do not select a fix before classification.

### Phase 4 — bounded mutation
Implement the smallest change against the evidenced first blocker, using PP-RM two-phase mutation semantics, and verify with a fresh exact-SHA Windows E2E run.

### Phase 5 — milestone decision
IOS-M2 completes when either full system-userland progression is demonstrated or the first concrete blocker is reproducibly isolated well enough to define the next bounded milestone.

## Later roadmap
After IOS-M2: full system/root filesystem → core services → graphics/input → SpringBoard → interactive iOS → Apple-service feasibility → Windows productization → reliability/release. Later stages are not active commitments.

## OCB
Explicit safety/safety-check block only; up to three exact-identical attempts total; no fourth automatic request; reconcile mutable side effects before replay.
