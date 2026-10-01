# Manager beliefs

- Persistent Project Manager `ios-research-runtime-project-manager` remains commitment owner; product authority is `main`, Manager authority is `manager-state`.
- IOS-M1 and IOS-M2 are complete.
- IOS-M2 completed on `main@4542112c90bb0f84a9a904726c54a3480ba07947`, E2E run `36870111560` / job `110395408194` SUCCESS.
- IOS-M2 proved that recovery has only md0/devfs and no guest-visible full-system disk, System/Volumes or private/preboot.
- IOS-M3 — Full System Storage / APFS Bring-up — is active.
- Current product authority is `main@951575209542d70d9f370049b3d17cde83ee64cf`.
- Commit `951575209542d70d9f370049b3d17cde83ee64cf` adds bounded BootKC storage-capability evidence without changing QEMU or downloading SystemOS.
- The probe classifies ANS, NVMe, VirtIO, embedded-storage/NAND and APFS candidates from the already-generated `ipsw kernel kexts` listing.
- Current correct state is `WAIT_EXTERNAL_EVIDENCE` for Windows E2E on exact head `951575209542d70d9f370049b3d17cde83ee64cf`.
- Upstream qemu-sptm Apple VirtIO block belongs to `-M vmapple`; it must not be assumed compatible with the working iPhone `-M darwin` path without BootKC evidence.
- Do not download/stage SystemOS in ordinary E2E until a guest-visible storage transport is evidenced.
- Package009 is terminal FINAL_COMPLETED. Package010 `IOS-M3-CONTINUOUS-010` is active.
- Packages005–009 must not resume.
- PP-RM generation16–19 runtime semantics and OCB3 remain authoritative.
