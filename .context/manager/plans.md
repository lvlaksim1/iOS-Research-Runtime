# Manager plans

## Current planning state
Manager generation: 23.
IOS-M1: COMPLETED.
IOS-M2: COMPLETED.
IOS-M3: ACTIVE / WAIT_EXTERNAL_EVIDENCE.
Product authority: `main@951575209542d70d9f370049b3d17cde83ee64cf`.
PP-RM package: `IOS-M3-CONTINUOUS-010`.

## IOS-M3 phase 1 — storage driver capability
Commit `951575209542d70d9f370049b3d17cde83ee64cf` uses the existing BootKC kext listing to emit bounded storage-capability diagnostics for:
- AppleANS;
- NVMe;
- VirtIO;
- embedded storage / NAND;
- APFS.

No QEMU device model or system image was added.

## Current action
Await exact-SHA Windows E2E for `951575209542d70d9f370049b3d17cde83ee64cf`.
When terminal evidence exists, classify which guest storage driver family is actually present.

## After evidence
1. If native ANS/NVMe drivers are present and VirtIO is absent, target a minimal native-compatible device model/DeviceTree path.
2. If a usable VirtIO block driver is present, evaluate the smallest way to expose an Apple-compatible virtio block transport to the darwin machine.
3. Build one host-backed block-device proof.
4. Require guest-visible disk-node evidence before SystemOS download.
5. Only then extract/stage SystemOS outside Git and proceed to APFS System/Preboot discovery.

## PP-RM
Package010 owns the external-evidence wait and bounded continuation. Never resume package009.
