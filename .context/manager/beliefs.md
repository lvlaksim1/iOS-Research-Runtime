# Manager beliefs

- Persistent Project Manager `ios-research-runtime-project-manager` remains commitment owner; product authority is `main`, Manager authority is `manager-state`.
- Owner-facing work is organized into four large stages; IOS-M* labels are internal checkpoints and do not create routine Owner gates.
- LARGE STAGE 1 — Full iOS System Boot — is active.
- IOS-M1 and IOS-M2 are complete.
- Recovery XNU/launchd/root shell remains reproducible.
- BootKC evidence for iPhone17,3 contains IONVMeFamily, APFS, AppleEmbeddedPCIE and AppleT8140PCIe; a usable VirtIO storage path is absent.
- Source DeviceTree evidence contains native `apcie` hierarchy, DART/IOMMU relationships and PCIe ranges.
- Exact-SHA E2E `37063868899` on `a79bd0f87fafcecb76a9cc751e4fa9cfaa47b199` succeeded with both `BOOT_PROOF_OK` and `IOS_M2_BOUNDARY_PROBE_OK`, while `/dev/disk*` remained absent.
- The filtered runtime IORegistry probe on that green run produced no matching PCIe/NVMe provider lines, narrowing the immediate boundary to runtime IOService matching/binding rather than missing BootKC PCIe/NVMe code.
- Current product authority is `main@a8c960bc7d26011c7e87e0791cb2e7621f0cd61e`, which captures unfiltered IODeviceTree and IOService registry evidence.
- Current correct runtime state is WAIT_EXTERNAL_EVIDENCE for Windows E2E run `37068183031` on that exact head.
- SystemOS staging remains deferred until guest-visible block transport is evidenced.
- Package009 is terminal FINAL_COMPLETED. Package010 is active. Packages005–009 must not resume.
- PP-RM runtime schema 10 and DEC-0018 are authoritative: OCB3 exhausts a disposable Worker runtime, not the package. Transient OCB self-heals through fresh-runtime failover / alternate compliant path / Watchdog OCB_BACKOFF.
- DEC-0019 is authoritative for publication recovery: `update_ref(force=false)` remains canonical, while `update_file` is a narrow alternate compliant path for an unambiguous existing single-file bounded change after repeated explicit OCB; the returned new commit SHA becomes authoritative and requires new exact-SHA evidence.
- PP-RM must never bypass a substantive safety restriction; only a genuine no-compliant-path safety boundary may become OWNER_GATE.
