# PP-RM Launch Package — generation 19

Status: RUNNING / WAIT_EXTERNAL_EVIDENCE
Manager generation: 23
Package: `IOS-M3-CONTINUOUS-010`
Product start: `main@4542112c90bb0f84a9a904726c54a3480ba07947`
Current product: `main@951575209542d70d9f370049b3d17cde83ee64cf`
Previous package: `IOS-M2-CONTINUOUS-009` — FINAL_COMPLETED / MUST NOT RESUME

## Mission
IOS-M3 — Full System Storage / APFS Bring-up.

Establish a guest-visible full-system storage path under the proven Windows `-M darwin` boot flow, then progress toward System/Preboot APFS discovery.

## Current bounded step — published
Commit `951575209542d70d9f370049b3d17cde83ee64cf` adds bounded storage-driver capability diagnostics from the existing BootKC kext listing:
- AppleANS;
- NVMe;
- VirtIO;
- embedded storage / NAND;
- APFS.

No SystemOS download or QEMU device-model mutation is included.

## Current wait
Expected workflow: `.github/workflows/windows-e2e.yml`.
Expected exact head: `951575209542d70d9f370049b3d17cde83ee64cf`.
Mailbox state: `WAIT_EXTERNAL_EVIDENCE`.
Resume owner after terminal evidence: Worker A.
Watchdog is read-only while waiting.

## After evidence
Choose the smallest guest-compatible storage transport; then prove one host-backed image appears as a guest disk before staging SystemOS.

## Supersession
Packages005–009 MUST NOT resume.
