# Manager plans

## Current planning state

Manager generation: 22.
IOS-M1 status: COMPLETED.
IOS-M2 status: COMPLETED.
IOS-M3 status: ACTIVE.
Product authority: `main@4542112c90bb0f84a9a904726c54a3480ba07947`.
PP-RM successor: `IOS-M3-CONTINUOUS-010`.

## IOS-M2 result

Exact-SHA Windows E2E run `36870111560` / job `110395408194` succeeded and completed the boundary probe.
The guest sees recovery `/dev/md0` and devfs only. Full-system disk nodes and System/Preboot paths are absent.

## IOS-M3 strategy — Full System Storage / APFS Bring-up

### Phase 1 — storage driver capability evidence
Use the BootKC kext listing already generated during provisioning.
Persist bounded diagnostic lines for storage-related kernel components, including ANS/NVMe/embedded-storage, VirtIO block, APFS and related candidates.
This requires no extra IPSW payload download.

### Phase 2 — choose transport
Reconcile the BootKC evidence with the pinned `qemu-sptm` machine model.
Known architecture fact: `-M darwin` currently creates no PCI/virtio storage bus, while upstream `vmapple-virtio-blk` belongs to the separate `-M vmapple` machine.
Choose the smallest transport compatible with drivers actually present in the iPhone kernel.

### Phase 3 — storage-device proof
Implement the minimum qemu-sptm/local DeviceTree changes needed for one host-backed raw image to appear as a guest block device.
Acceptance: `/dev/disk*` or the native equivalent is reproducibly visible from the recovery root shell.

### Phase 4 — system image material
Only after transport proof, extract the iPhone17,3 SystemOS DMG with pinned `ipsw` using remote `--dmg sys --device iPhone17,3` semantics and stage it outside the repository.
Do not store Apple firmware in Git.

### Phase 5 — APFS bring-up
Attach the staged image through the proven transport and obtain reproducible APFS container/volume discovery for System/Preboot.
Then address required boot arguments, trust/security, or volume-group semantics from evidence.

## Immediate action
Publish the storage-capability logging mutation to `main`; consume exact-SHA Windows E2E; then decide the transport.

## PP-RM
Package010 is clean successor state. It may be activated when the current live carrier enters external-evidence wait. Never resume package009.

## OCB
Explicit safety/safety-check block only; maximum three exact-identical attempts; no fourth.
