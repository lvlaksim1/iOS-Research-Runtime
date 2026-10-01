# Manager plans

## Current planning state
Manager generation: 24.
Macro stage: LARGE STAGE 1 — Full iOS System Boot.
Execution: ACTIVE / WAIT_EXTERNAL_EVIDENCE.
Product authority: `main@32dd17014113543862e756c7daa52822e2eec073`.
PP-RM package: `IOS-M3-CONTINUOUS-010`.
PP-RM runtime schema: 10.

## Current bounded experiment
Prior exact-SHA E2E `36908440572` proved:
- recovery XNU/launchd/root shell remain reproducible;
- IONVMeFamily and APFS support are present;
- `/dev/disk*` remains absent with the PCIe discovery node at DeviceTree root.

Current commit `32dd17014113543862e756c7daa52822e2eec073` moves that discovery node under `arm-io` while preserving bounded ECAM/MMIO ranges.

Await exact-SHA Windows E2E run `36915159246`.

## After evidence
1. If a guest disk appears, add explicit disk-node proof and proceed to SystemOS/APFS staging outside Git.
2. If no disk appears, use serial/DeviceTree/driver-binding evidence to isolate the next smallest PCIe/NVMe dependency (properties, hierarchy, interrupts or device model behavior).
3. Keep all IOS-M* subdivisions internal; continue until Large Stage 1 acceptance or a genuine strategic boundary.

## PP-RM continuity
DEC-0018 is authoritative.
Transient OCB must not terminalize the package.
Use fresh-runtime failover first, equivalent compliant operation next, then Watchdog-owned OCB_BACKOFF/replan if repeated.
A substantive no-compliant-path safety restriction remains a valid terminal governance boundary.
