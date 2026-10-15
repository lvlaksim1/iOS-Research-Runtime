# iOS M3 — PCIe/NVMe interrupt-delivery prerequisite (source-only)

**Evidence baseline:** published `lvlaksim1/iOS-Research-Runtime` `50fff7ab8fc33fa1324ea204416f7a773a191033`; pinned `jprx/qemu-sptm` `2867d847d3471560e773120ee50c42dbcbb6d60b`. This document is a source investigation, not guest runtime evidence or a proposed Apple `#ports` value.

## Verified source facts

| Source | Exact Git blob | Finding |
|---|---|---|
| `jprx/qemu-sptm/hw/arm/darwin.c` | `51d240b112907e9bd2ef4d9be836a1a04a865db5` | `init_aic()` allocates zeroed AIC MMIO and writes reported IRQ count; its comment calls the implementation bare-bones and says it ignores register reads/writes. No IRQ delivery call occurs in this function. |
| `jprx/qemu-sptm/hw/pci-host/gpex.c` | `e66784ce516e60a98db2ae3ddd6ed4b6ddd14599` | GPEX registers root bus `pcie.0`, exposes `num_irqs` sysbus IRQs, and INTx swizzle uses modulo `bus->nirq`. |
| `runtime/qemu/patches/0006-darwin-gpex-root-bus.patch` | `2163f92f4266b6fd64dff4cdb8aef4b5442d2cb3` | Adds GPEX host but sets `num-irqs` to **0** and does not connect GPEX IRQs to AIC. This patch is applied to pinned QEMU; upstream `darwin.c` alone has no GPEX. |
| `src/IOSResearchRuntime/Services/AppleDeviceTreePatcher.cs` | `eb3d6168e370ba91c609fc25c2709e3ba0dc2676` | Synthetic `apcie,t8140` node advertises `msi-parent-controller=32` and `#msi-vectors=96`; advertisement alone cannot establish QEMU interrupt delivery or Apple controller compatibility. |
| `src/IOSResearchRuntime/Services/QemuCommandBuilder.cs` | `023ef24eba4a3c96aa53caf0e69142864a308451` | Requests `pcie-root-port` on `pcie.0` and `nvme` behind it, with an empty raw probe image. This establishes host command intent, not IOKit binding. |

**New dependency:** before expecting an operational NVMe-backed SystemOS disk, establish the guest PCIe controller's interrupt delivery contract, including the actual AIC/MSI mapping and whether the emulated controller requires an INTx route. The current inspected GPEX patch has zero INTx outputs and the pinned AIC is a register stub. The `% bus->nirq` path is a *potential* zero-divisor hazard **if** that INTx path executes, not proof of a runtime crash. MSI-X behavior and Apple IOKit compatibility remain unproven; do not infer they fail or work solely from the static audit.

**Smallest next engineering dependency:** first capture exact guest PCIe provider/port ancestry and ECAM NVMe identity on an actually built, hash-verified QEMU head; then determine which Apple AIC/MSI endpoint and delivery semantics the bound driver uses. Only after the ABI is evidenced should a minimal AIC/GPEX routing implementation be specified. Do not guess `#ports`, invent an MSI doorbell address, or change PCI semantics merely to pass tests.

## Test ladder and limitations

`audit_m3_storage_irq_path.py` verifies **exact Git blob IDs** for five source inputs, inspects narrowly defined source regions, and emits a fail-closed JSON report. Unit tests use synthetic excerpts. A successful source audit is not a QEMU build, a Windows CI result, an iPhoneOS SDK compilation, an NVMe driver binding, an APFS mount, or Stage 1 acceptance. The existing Windows Build `38711142165` and QEMU Gate `38711142120` succeeded only on published `50fff7ab`; previous E2E `38676276954` failed at missing AppleEmbeddedPCIE `#ports`. No later E2E is claimed here.

**Proof required for full Stage 1:** actual PCIe/IOKit provider → guest NVMe → non-ramdisk `/dev/disk*` → APFS SystemOS/Preboot/Data mounts → system launchd/core userland. Recovery `md0`, recovery root shell and recovery `launchd` do not satisfy it.
