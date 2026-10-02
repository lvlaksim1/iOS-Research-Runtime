# Latest handoff

Updated: 2026-10-03 00:42 MSK

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 25.
Product authority: `main@a8c960bc7d26011c7e87e0791cb2e7621f0cd61e`.
Execution status: ACTIVE / LARGE STAGE 1 / WAIT_EXTERNAL_EVIDENCE.
Active package: `IOS-M3-CONTINUOUS-010`.

## Verified evidence
Exact-SHA Windows E2E `37063868899` on `a79bd0f87fafcecb76a9cc751e4fa9cfaa47b199` completed SUCCESS.
It proved `BOOT_PROOF_OK` and `IOS_M2_BOUNDARY_PROBE_OK`.
IONVMeFamily, AppleEmbeddedPCIE and AppleT8140PCIe are present; source DeviceTree contains native apcie/DART/IOMMU/range data; `/dev/disk*` remains absent.
Filtered runtime IORegistry returned no matching PCIe/NVMe provider lines.

## Current product action
Commit `a8c960bc7d26011c7e87e0791cb2e7621f0cd61e` captures unfiltered IODeviceTree and IOService registry output.
Exact-SHA Windows E2E run `37068183031` is in progress.

## Publication recovery rule
DEC-0019 is durable authority:
- canonical path: prebuilt target + `update_ref(force=false)`;
- narrow alternate path after repeated explicit OCB: for one existing UTF-8 file only, reconcile `main`, fetch current blob SHA, publish exact authorized content with `update_file`;
- the returned commit SHA, not the prebuilt target SHA, becomes authoritative and requires fresh exact-SHA CI evidence;
- never generalize this to ambiguous/multi-file publication or substantive safety restrictions.

## Next responsibility
Consume run `37068183031`, use unfiltered registry evidence to isolate the next smallest PCIe/NVMe binding dependency, and continue Large Stage 1 autonomously.

Packages005–009 must not resume.
