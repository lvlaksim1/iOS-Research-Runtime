# Manager beliefs

- Persistent Project Manager `ios-research-runtime-project-manager` remains commitment owner; product authority is `main`, Manager authority is `manager-state`.
- IOS-M1 is complete with verified recovery `launchd` plus verified root shell on Windows.
- IOS-M2 is complete on authoritative product `main@4542112c90bb0f84a9a904726c54a3480ba07947`.
- Exact-SHA Windows End-to-End Boot run `36870111560`, job `110395408194`, completed SUCCESS and produced `IOS_M2_BOUNDARY_PROBE_OK`.
- IOS-M2 evidence reproducibly isolates the first full-system boundary: recovery root is `/dev/md0` read-only APFS plus devfs; `/System/Volumes`, `/private/preboot`, and `/dev/disk*` are absent; `launchctl` is absent from the injected recovery userspace.
- Repeated `AppleSEPManager` endpoint timeouts remain observed but are not causally assigned as the first blocker.
- The Owner explicitly authorized continued development on 2026-10-01.
- IOS-M3 — Full System Storage / APFS Bring-up — is now the active product commitment.
- Current `-M darwin` command line supplies BootKC, DeviceTree, trustcache and recovery ramdisk only; it supplies no system disk.
- Upstream `qemu-sptm` contains `vmapple-virtio-blk`, but that device is wired to the separate `-M vmapple` machine, while the working iOS path uses `-M darwin` with an iPhone DeviceTree and no PCI/virtio storage bus.
- Therefore the first IOS-M3 step is capability discovery from the actual iPhone17,3 BootKC before choosing a storage emulation path: identify native ANS/NVMe/storage drivers and whether any VirtIO block driver exists.
- Do not download or attach the large SystemOS image to ordinary E2E until a guest-visible storage transport is evidenced.
- Package009 is terminal `FINAL_COMPLETED`. Packages005–009 must not resume.
- Fresh successor package is `IOS-M3-CONTINUOUS-010`.
- PP-RM generation19 runtime semantics remain authoritative: generation16 two-phase mutation, generation17 recurring Watchdog, generation18 result-first evidence, generation19 `WAIT_EXTERNAL_EVIDENCE`, OCB3.
