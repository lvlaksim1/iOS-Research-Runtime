# 2026-10-15 — PP-RM PMGR staging attempt and bounded OCB recovery

Project: `lvlaksim1/iOS-Research-Runtime`
Package: `IOS-M3-CONTINUOUS-010`
Scope: generations 649–651
Status at observation: `OCB_BACKOFF`
Source: PP-RM Scheduled Tasks Mailbox / Trace, plus independent read-only GitHub ref checks.

## Authoritative evidence

- Base product `main`: `89cf1e04571545010c2433f24264bae25f5c5f2d`.
- Owner-authorized staging ref: `pp-rm/g649-pmgr-two-file-staging`, created and read back at the same exact baseline SHA.
- Generation 649, Worker B: the source `src/IOSResearchRuntime/Services/AppleDeviceTreePatcher.cs` was examined; `DeleteUnsupportedCompatible` removes compatibility properties except for the supported whitelist. Native `pmgr1,t8140` is not whitelisted in the observed source blob `eb3d6168e370ba91c609fc25c2709e3ba0dc2676`. Three identical attempts to update this host source on staging received explicit tool-safety blocks. The ref remained unchanged.
- Generation 650, Worker A: independently reconciled the same baseline and source blob. Three further identical attempts to update the host source received explicit tool-safety blocks. Ref readback confirmed no change.
- Generation 651, Worker B: a bounded read-only search of existing branches, commits and pull requests did not identify a complete, verified, exact-SHA *paired* host-ADT/QEMU-PMGR target. That search cannot prove nonexistence of every unreferenced Git object.
- Watchdog's subsequent independent compare still found `main` and the staging branch at the same SHA, with no changed files. It retained `OCB_BACKOFF` rather than issuing another blocked write.

## Engineering direction, not a completed implementation

The next candidate is an evidence-driven, coupled change to:
1. preserve verified native PMGR DeviceTree compatibility and original property values in host ADT processing, and
2. implement a bounded, evidence-based PMGR MMIO device in the pinned QEMU/Darwin runtime.

The purpose is to investigate the PCIe/IOKit provider-binding → NVMe → guest block-device path. Merely exposing a compatible string or installing an MMIO stub does **not** prove functional PMGR emulation, storage visibility, APFS/SystemOS mounting, or Large Stage 1 acceptance.

## Recovery and publication constraints

- The Owner separately approved justified temporary GitHub service branches on 2026-10-15 (DEC-0021).
- Do not repeat the blocked `UPDATE_HOST_ADT_PATCHER_ON_OWNER_AUTHORIZED_STAGING_BRANCH` operation through a relabelled alternate channel or assume a tool-safety block succeeded.
- There was **no prepared complete two-file commit** to publish when generations 649–651 ended. No frozen target SHA, commit, CI or end-to-end evidence exists for the proposed paired change.
- Do not move `main` based on this record. A future implementation needs a genuinely compliant construction method, a frozen direct-child target, required ordered exact-SHA evidence, and non-force publication according to PP-RM v19 / DEC-0020.

This is an episodic checkpoint, not a product modification or a test result.
