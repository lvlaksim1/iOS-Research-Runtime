# Current state

Updated: 2026-10-01 17:13 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 23
- product authority: `main@951575209542d70d9f370049b3d17cde83ee64cf`
- execution status: ACTIVE / IOS-M3 / WAIT_EXTERNAL_EVIDENCE
- active package: `IOS-M3-CONTINUOUS-010`

## Completed foundation
IOS-M1 complete.
IOS-M2 complete: exact-SHA E2E `36870111560` / `110395408194` SUCCESS isolated the missing full-system storage boundary.

## IOS-M3 product progress
Commit `951575209542d70d9f370049b3d17cde83ee64cf` is published to main.
It adds no new download and no QEMU/storage mutation.
It emits BootKC storage capability evidence from the existing kext listing.

## Current wait
Expected workflow: `.github/workflows/windows-e2e.yml`.
Expected exact head: `951575209542d70d9f370049b3d17cde83ee64cf`.
Required output: `[storage-capability]` lines identifying ANS/NVMe/VirtIO/embedded-storage/APFS candidates.

## Constraints
Do not download SystemOS in normal E2E until transport is proven.
Do not infer AppleSEPManager as causal blocker without evidence.
Packages005–009 must not resume.
