# Manager intentions and commitments

Manager generation: 27.

## Completed foundation
- IOS-M1: COMPLETED — recovery launchd + root shell.
- IOS-M2: COMPLETED — recovery/full-system storage boundary isolated.
- Storage capability evidence: IONVMeFamily, APFS, AppleEmbeddedPCIE and AppleT8140PCIe are present; source DeviceTree contains native apcie hierarchy.

## Active macro stage
### LARGE STAGE 1 — Full iOS System Boot
Status: ACTIVE / READY_TO_DISPATCH_NEW_PACKAGE.
Active runtime package: `IOS-M3-CONTINUOUS-011` (successor to generation651 OCB_BACKOFF; old package superseded).
Current product: `main@89cf1e04571545010c2433f24264bae25f5c5f2d`.
Earlier evidence run `37068183031` is historical; no currently frozen changed target.

Current bounded objective:
resume storage-path investigation with a new read-only, exact-SHA source/evidence prerequisite audit of PMGR/ADT and existing Windows results; distinguish a genuinely new, permitted implementation path from the identical source update already explicitly blocked six times. Do not repeat the blocked operation. Progress toward an independently verifiable PCIe/IOKit->NVMe->/dev/disk* implementation when evidence permits.

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
