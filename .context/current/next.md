# Next actions

Updated: 2026-10-01 15:13 MSK

1. Preserve IOS-M2 as the active commitment from baseline `main@95caa93fc8fd0db827491e679628efa40612b55c`.
2. Add a bounded post-root boot-boundary probe to the existing Windows E2E integration harness while preserving the IOS-M1 proof.
3. Push that diagnostic mutation to `main`; the normal push path should trigger Windows E2E.
4. Capture exact-SHA evidence for mounts/volumes, system/preboot paths, device/disk exposure and launchd/service state.
5. Classify the first evidenced blocker before changing QEMU hardware, provisioning semantics or trust/security logic.
6. Implement the smallest bounded mutation against that blocker and repeat exact-SHA E2E.
7. If the live carrier reaches an external-evidence wait or continuity boundary, activate clean PP-RM package `IOS-M2-CONTINUOUS-009` using generation16–19 semantics.
8. Do not resume packages005,006,007 or008.
