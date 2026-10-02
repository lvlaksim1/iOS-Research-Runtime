# Current state

Updated: 2026-10-03 00:42 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 25
- macro stage: LARGE STAGE 1 — Full iOS System Boot
- product authority: `main@a8c960bc7d26011c7e87e0791cb2e7621f0cd61e`
- execution status: ACTIVE / WAIT_EXTERNAL_EVIDENCE
- active package: `IOS-M3-CONTINUOUS-010`
- PP-RM runtime schema: 10

## Product progress
Recovery/root-shell foundation remains reproducible.
BootKC/capability evidence contains IONVMeFamily, APFS, AppleEmbeddedPCIE and AppleT8140PCIe.
Source DeviceTree evidence contains native `apcie` hierarchy, DART/IOMMU relationships and PCIe ranges.

Exact-SHA E2E `37063868899` on `a79bd0f87fafcecb76a9cc751e4fa9cfaa47b199` completed SUCCESS with `BOOT_PROOF_OK` and `IOS_M2_BOUNDARY_PROBE_OK`.
`/dev/disk*` remained absent.
The filtered runtime IORegistry probe emitted no matching PCIe/NVMe provider lines, so the immediate boundary is now runtime IOService matching/binding.

Commit `a8c960bc7d26011c7e87e0791cb2e7621f0cd61e` captures unfiltered IODeviceTree and IOService evidence.

## Current wait
Workflow: Windows End-to-End Boot.
Exact head: `a8c960bc7d26011c7e87e0791cb2e7621f0cd61e`.
Run: `37068183031`.
State: in progress / WAIT_EXTERNAL_EVIDENCE.
Resume owner: Worker B.

## PP-RM resilience and publication
DEC-0018 adopted: transient OCB is nonterminal and self-heals through fresh runtime / alternate compliant path / Watchdog OCB_BACKOFF.

DEC-0019 adopted:
- `update_ref(force=false)` remains canonical publication of a prebuilt target commit;
- when repeated explicit OCB blocks that publication and the bounded change is exactly one existing text file with unambiguous refs/content, fresh-SHA-fenced `update_file` is an allowed equivalent high-level recovery path;
- the fallback creates a different commit SHA, which becomes the new authoritative head and must receive new exact-SHA CI evidence;
- the fallback is not authorized for ambiguous, multi-file, non-equivalent, or substantively restricted operations.

## Constraints
Do not stage SystemOS until guest-visible storage is evidenced.
Packages005–009 remain terminal/superseded and must not resume.
