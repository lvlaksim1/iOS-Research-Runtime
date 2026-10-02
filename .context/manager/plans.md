# Manager plans

## Current planning state
Manager generation: 25.
Macro stage: LARGE STAGE 1 — Full iOS System Boot.
Execution: ACTIVE / WAIT_EXTERNAL_EVIDENCE.
Product authority: `main@a8c960bc7d26011c7e87e0791cb2e7621f0cd61e`.
PP-RM package: `IOS-M3-CONTINUOUS-010`.
PP-RM runtime schema: 10.

## Current evidence
Exact-SHA E2E `37063868899` on `a79bd0f87fafcecb76a9cc751e4fa9cfaa47b199` succeeded and proved:
- recovery XNU/launchd/root shell remain reproducible;
- `BOOT_PROOF_OK` and `IOS_M2_BOUNDARY_PROBE_OK` both complete;
- IONVMeFamily, AppleEmbeddedPCIE and AppleT8140PCIe are present in the kernel capability set;
- source DeviceTree contains native apcie/DART/IOMMU/range data;
- `/dev/disk*` remains absent;
- the filtered runtime IORegistry probe emitted no matching PCIe/NVMe provider lines.

This narrows the current boundary to runtime DeviceTree/IOService matching and PCIe/NVMe binding.

Current commit `a8c960bc7d26011c7e87e0791cb2e7621f0cd61e` removes the diagnostic grep filters to capture unfiltered IODeviceTree and IOService registry state.
Await exact-SHA Windows E2E run `37068183031`.

## After evidence
1. If the relevant PCIe provider exists under an unexpected name/class/path, identify the smallest missing matching property or child-device relationship.
2. If no corresponding live IOService provider exists, isolate why the native apcie DeviceTree description is not instantiating/matching AppleT8140PCIe/AppleEmbeddedPCIE.
3. If PCIe service binding exists but NVMe does not, isolate the next endpoint/device-model dependency.
4. If a guest disk appears, add explicit disk-node proof and proceed to SystemOS/APFS staging outside Git.
5. Keep all IOS-M* subdivisions internal; continue until Large Stage 1 acceptance or a genuine strategic boundary.

## PP-RM continuity and publication
DEC-0018 is authoritative for OCB runtime self-healing.
DEC-0019 is authoritative for the narrow single-file publication fallback.
Canonical publication remains prebuilt target + `update_ref(force=false)`.
For a repeated explicit OCB on an unambiguous existing single-file bounded publication, fresh-fetch the current file/blob SHA and use `update_file` only for the exact authorized content; record the returned new commit SHA, never conflate it with the prebuilt target, and consume new exact-SHA CI evidence.
A substantive no-compliant-path safety restriction remains a valid terminal governance boundary.
