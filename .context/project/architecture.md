# Project architecture

## DECISION — Product architecture

The product has four main layers:
1. Windows WPF GUI in `src/IOSResearchRuntime`;
2. provisioning services for pinned tools/resources and IPSW-derived material;
3. a Windows-packaged patched `qemu-sptm` runtime;
4. exact-SHA evidence automation through the Windows build/E2E workflows.

Product authority is `main`; durable Manager authority is `manager-state`.

## Execution architecture — PP-RM

PP-RM remains the bounded continuous-execution runtime. Manager decides direction and acceptance; A/B execute bounded units; Watchdog owns continuity and external-evidence wait.

## Verified boot/storage boundary

IOS-M1 proved recovery launchd + root shell.
IOS-M2 completed on `main@4542112c90bb0f84a9a904726c54a3480ba07947`, Windows E2E run `36870111560` / job `110395408194` SUCCESS.

The recovery guest exposes:
- `/dev/md0` mounted as read-only APFS root;
- devfs;
- no `/System/Volumes`;
- no `/private/preboot`;
- no `/dev/disk*`.

Therefore the current guest has no full-system block storage path.

## IOS-M3 architecture question

The application currently supplies to `-M darwin` only BootKC, DeviceTree, trustcache and recovery ramdisk.
The pinned qemu-sptm darwin machine itself creates CPU/AIC/UART/SEP placeholder/Apple registers but no PCI/virtio storage bus.

The same upstream tree contains Apple-compatible `vmapple-virtio-blk`, but that belongs to the separate `-M vmapple` machine and is not evidence of iPhone-kernel compatibility.

IOS-M3 must first classify the iPhone17,3 BootKC storage drivers, then implement the smallest compatible host-backed storage device. SystemOS staging follows only after guest-visible disk proof.
