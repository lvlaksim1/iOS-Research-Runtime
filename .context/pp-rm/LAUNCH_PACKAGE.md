# PP-RM Launch Package — generation 19

Status: PREPARED / LIVE-FIRST
Manager generation: 22
Package: `IOS-M3-CONTINUOUS-010`
Product baseline: `main@4542112c90bb0f84a9a904726c54a3480ba07947`
Previous package: `IOS-M2-CONTINUOUS-009` — FINAL_COMPLETED / MUST NOT RESUME

## Mission
IOS-M3 — Full System Storage / APFS Bring-up.

Establish a guest-visible full-system storage path under the proven Windows `-M darwin` boot flow, then progress toward System/Preboot APFS discovery.

## First acceptance gate
Determine the viable storage transport from exact evidence:
- storage-related drivers present in the iPhone17,3 BootKC;
- compatibility with the pinned qemu-sptm darwin machine;
- no speculative SystemOS download before a guest consumer exists.

## First bounded step
Instrument the existing `ipsw kernel kexts bootkc` validation to emit bounded storage-driver capability lines for ANS/NVMe/embedded storage, VirtIO block, APFS and related candidates.

Publish the smallest diagnostic change to `main`, consume exact-SHA Windows E2E, then choose the transport.

## Execution ownership
The direct Owner-facing runtime owns the first bounded step.
Workers A/B and Watchdog remain unarmed while the live carrier performs that same work.
If execution reaches external-evidence wait, initialize package010 Mailbox/Trace and activate the Watchdog using retained generation16–19 semantics.

## Supersession
Packages005–009 MUST NOT resume.
