# Manager intentions and commitments

## Completed

### IOS-M1 — first Windows boot milestone
- status: COMPLETED
- objective: verified recovery `launchd` plus verified root shell on Windows
- authoritative product: `main@95caa93fc8fd0db827491e679628efa40612b55c`
- evidence: Windows E2E run `36844422600`, job `110311023233`

### IOS-M2 — Full iOS Boot Boundary
- status: COMPLETED
- authoritative product: `main@4542112c90bb0f84a9a904726c54a3480ba07947`
- evidence: Windows E2E run `36870111560`, job `110395408194`, conclusion SUCCESS
- verified boundary: recovery root `/dev/md0` read-only APFS plus devfs; no `/System/Volumes`; no `/private/preboot`; no `/dev/disk*`; no `launchctl` utility in recovery userspace
- acceptance: first concrete full-iOS system-userland boundary reproducibly isolated

### IOS-PP-RM package009
- status: FINAL_COMPLETED
- terminal runtime generation: 7

## Active

### IOS-M3 — Full System Storage / APFS Bring-up
- status: ACTIVE
- owner authorization: direct Owner directive on 2026-10-01 to continue development
- start baseline: `main@4542112c90bb0f84a9a904726c54a3480ba07947`
- objective: make the full-system storage path visible to the iOS guest and progress toward mountable System/Preboot APFS volumes
- first acceptance gate: determine the viable guest storage transport from the actual iPhone17,3 BootKC and current qemu-sptm machine model
- first bounded mutation: persist storage-driver capability evidence from the already executed `ipsw kernel kexts bootkc` output
- candidate classes: native ANS/NVMe/embedded-storage drivers versus VirtIO block support
- rule: do not add a SystemOS DMG to normal E2E before the guest transport is evidenced
- successor package: `IOS-M3-CONTINUOUS-010`

## Superseded runtime packages
Packages005,006,007,008 and completed package009 must not resume.

## OCB
Explicit safety/safety-check block only; max three exact-identical attempts; no automatic fourth; reconcile ambiguous mutable side effects before replay.
