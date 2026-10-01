# Manager intentions and commitments

## Completed

### IOS-M1
- status: COMPLETED
- verified recovery launchd + root shell

### IOS-M2 — Full iOS Boot Boundary
- status: COMPLETED
- authoritative product: `main@4542112c90bb0f84a9a904726c54a3480ba07947`
- evidence: Windows E2E run `36870111560`, job `110395408194`, SUCCESS
- boundary: recovery md0/devfs only; no System/Volumes, private/preboot or disk nodes
- package009: FINAL_COMPLETED

## Active

### IOS-M3 — Full System Storage / APFS Bring-up
- status: ACTIVE / WAIT_EXTERNAL_EVIDENCE
- owner authorization: direct Owner directive on 2026-10-01
- start baseline: `main@4542112c90bb0f84a9a904726c54a3480ba07947`
- current product: `main@951575209542d70d9f370049b3d17cde83ee64cf`
- objective: establish a guest-visible full-system storage path and progress toward mountable System/Preboot APFS volumes
- first diagnostic mutation: published
- exact evidence target: Windows End-to-End Boot on `951575209542d70d9f370049b3d17cde83ee64cf`
- required evidence: BootKC storage candidates for ANS/NVMe, VirtIO, embedded storage/NAND and APFS
- active runtime package: `IOS-M3-CONTINUOUS-010`

## Rule
Do not stage the large SystemOS image until a guest-visible transport is evidenced.

## Superseded runtime packages
Packages005–009 must not resume.
