# Current state

Updated: 2026-10-01 17:09 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 22
- product authority: `main@4542112c90bb0f84a9a904726c54a3480ba07947`
- execution status: ACTIVE / IOS-M3
- active milestone: `IOS-M3 — Full System Storage / APFS Bring-up`
- successor package: `IOS-M3-CONTINUOUS-010`

## Completed foundation
IOS-M1 is complete.
IOS-M2 is complete on exact-SHA Windows E2E run `36870111560`, job `110395408194`, conclusion SUCCESS.

Verified IOS-M2 boundary:
- root mount: `/dev/md0` read-only APFS;
- devfs present;
- `/System/Volumes` absent;
- `/private/preboot` absent;
- `/dev/disk*` absent;
- recovery userspace has no `launchctl` executable.

This proves the current runtime has no guest-visible full-system storage path.

## IOS-M3 current technical state
The application currently passes only BootKC, DeviceTree, trustcache and recovery ramdisk to `-M darwin`.
The pinned qemu-sptm source contains Apple-compatible `vmapple-virtio-blk`, but that is attached to the separate vmapple machine. The working darwin machine creates no equivalent storage transport.

## Immediate execution
Add diagnostic classification of the actual iPhone17,3 BootKC storage drivers using the existing `ipsw kernel kexts` output. Then run exact-SHA Windows E2E and select the next device-model mutation from evidence.

Do not stage/download SystemOS in ordinary E2E until guest storage transport is proven.

Packages005–009 must not resume.
