# Current blockers and open risks

Updated: 2026-10-01 22:39 MSK

## Large Stage 1
Immediate technical boundary: XNU still has not registered a guest-visible disk.

Evidence already eliminates several earlier uncertainties:
- recovery boot and root shell work;
- IONVMeFamily exists in BootKC;
- APFS support exists;
- generic QEMU NVMe can be attached only after adding PCIe/GPEX plumbing;
- GPEX/ECAM/MMIO builds and does not break recovery boot;
- a root-level PCIe discovery node did not produce `/dev/disk*`.

Current exact experiment moves the discovery node under `arm-io`.
Await E2E run `36915159246` on `main@32dd17014113543862e756c7daa52822e2eec073`.

If still absent, next blockers must be isolated from direct evidence among DeviceTree properties/hierarchy, interrupt routing, PCI enumeration/driver binding, or NVMe device-model compatibility.

SystemOS extraction remains intentionally deferred.

## Runtime continuity risk
Legacy OCB3 terminalization was demonstrated at generation45.
DEC-0018 / schema10 fixes it: transient OCB is nonterminal and self-heals across disposable runtimes.
A genuine substantive safety restriction remains authoritative and must not be bypassed.
