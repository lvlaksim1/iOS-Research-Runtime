# Latest handoff

Updated: 2026-10-01 17:09 MSK

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 22.
Product authority: `main@4542112c90bb0f84a9a904726c54a3480ba07947`.
Execution status: ACTIVE / IOS-M3.
Successor package: `IOS-M3-CONTINUOUS-010`.

## Completed milestone
IOS-M2 is FINAL_COMPLETED.
Exact-SHA Windows E2E run `36870111560`, job `110395408194`, conclusion SUCCESS, proved:
- recovery root shell still works;
- IOS-M2 boundary probe completes;
- only recovery md0/devfs are visible;
- System/Volumes, private/preboot and disk nodes are absent.

## Active responsibility
IOS-M3 must establish a full-system storage path.

Immediate bounded action:
1. instrument the existing BootKC kext validation to emit storage-driver capability evidence;
2. publish to `main`;
3. consume exact-SHA Windows E2E;
4. choose native storage emulation versus any evidenced VirtIO path;
5. do not download SystemOS until a guest-visible transport is proven.

## Architecture evidence
The pinned qemu-sptm working machine is `darwin`. The upstream Apple VirtIO block device belongs to the separate `vmapple` machine and cannot be assumed usable on the iPhone path.

Packages005–009 must not resume.
