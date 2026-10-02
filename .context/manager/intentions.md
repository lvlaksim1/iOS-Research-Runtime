# Manager intentions and commitments

Manager generation: 25.

## Completed foundation
- IOS-M1: COMPLETED — recovery launchd + root shell.
- IOS-M2: COMPLETED — recovery/full-system storage boundary isolated.
- Storage capability evidence: IONVMeFamily, APFS, AppleEmbeddedPCIE and AppleT8140PCIe are present; source DeviceTree contains native apcie hierarchy.

## Active macro stage
### LARGE STAGE 1 — Full iOS System Boot
Status: ACTIVE / WAIT_EXTERNAL_EVIDENCE.
Active runtime package: `IOS-M3-CONTINUOUS-010`.
Current product: `main@a8c960bc7d26011c7e87e0791cb2e7621f0cd61e`.
Current evidence run: `37068183031`.

Current bounded objective:
capture unfiltered IODeviceTree/IOService registry state and determine why native Apple PCIe/NVMe code and DeviceTree descriptions are not yet producing a guest-visible disk.

When guest-visible storage is proven, continue automatically through SystemOS/Preboot/Data staging, APFS discovery/mounting, system launchd and core full-system userland.

## Runtime continuity commitment
DEC-0018 / schema10 applies:
- OCB3 exhausts one disposable Worker runtime only;
- first recovery rotates to a fresh partner runtime;
- repeated transient OCB enters nonterminal Watchdog-owned OCB_BACKOFF and later safe replan;
- successful progress resets OCB recovery state;
- only genuine strategy/authority/safety boundaries may require Owner intervention.

DEC-0019 publication recovery applies:
- `update_ref(force=false)` remains canonical for publishing a prebuilt target;
- after repeated explicit OCB, an existing single-file bounded change may be published through fresh-SHA-fenced `update_file` only when refs and intended content are unambiguous;
- the fallback-produced commit SHA replaces the prebuilt target as authoritative product head and receives fresh exact-SHA CI evidence;
- this is not a multi-file atomic-publication substitute and must not bypass substantive restrictions.

## Constraints
Do not stage large SystemOS assets until guest-visible storage transport is evidenced.
Do not infer AppleSEPManager as causal without evidence.
Packages005–009 must not resume.
