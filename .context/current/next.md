# Next actions

Updated: 2026-10-01 15:18 MSK

1. Preserve active product `main@24730a74051378d228efd370f3baee5a4f46bdfa`; do not duplicate the post-root probe.
2. Await/locate Windows End-to-End Boot evidence on that exact SHA through package009 `WAIT_EXTERNAL_EVIDENCE`.
3. When terminal evidence exists, resume Worker A through PP-RM Watchdog.
4. Consume the probe markers for mounts, system volumes, preboot, disk/device exposure and launchd/service state.
5. Classify the first evidenced boot boundary before changing QEMU hardware, provisioning semantics or trust/security logic.
6. Implement only the smallest bounded mutation against that blocker and repeat exact-SHA E2E.
7. Complete IOS-M2 when full-system progression is demonstrated or the first concrete blocker is reproducibly isolated for the next milestone.
8. Do not resume packages005,006,007 or008.
