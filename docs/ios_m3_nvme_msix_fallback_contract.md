# iOS M3: NVMe MSI-X initialization/fallback — pinned-source prerequisite

**Published product baseline:** `lvlaksim1/iOS-Research-Runtime@50fff7ab8fc33fa1324ea204416f7a773a191033`. **Pinned QEMU source:** `jprx/qemu-sptm@2867d847d3471560e773120ee50c42dbcbb6d60b`. This is source-only evidence, not an emulated guest observation.

## Newly isolated prerequisite

The QEMU NVMe controller has **two** interrupt routes. In pinned `hw/nvme/ctrl.c` (Git blob `4893cf7e7418d3cf8a5a27d7e458d700c6fcc7b8`), `nvme_irq_assert` calls `msix_notify` when MSI-X is enabled; otherwise it uses `nvme_irq_check`, which asserts/deasserts the PCI INTx pin. During `nvme_init_pci`, the MSI-X initialization result `-ENOTSUP` is deliberately downgraded to a warning, with initialization continuing. Thus, *successful NVMe device creation does not prove MSI-X availability or any working interrupt route*.

Pinned `hw/pci/msix.c` (blob `1b23eaf10079f9f7501aae25f7826020c49d2e25`) returns `-ENOTSUP` from `msix_init` when global `msi_nonbroken` is false. `msix_init_exclusive_bar` delegates to `msix_init`, so both BAR layouts use that guard. In the inspected `hw/arm/darwin.c` (blob `51d240b112907e9bd2ef4d9be836a1a04a865db5`), `init_aic` uses `alloc_zeroed("aic", ...)` and no IRQ delivery operation is visible *within that function*. No assignment to `msi_nonbroken` occurs in that **file**. This does **not** prove the runtime global flag is false: other initialization code, build options, and actual QEMU process state were not examined exhaustively.

The MSI-X send path, when enabled and unmasked, is `nvme_irq_assert` → `msix_notify` → `msi_send_message` → `pci_msi_trigger` → `address_space_stl_le(&dev->bus_master_as, msg.address, msg.data, ...)`. Verified pinned source blobs: `hw/pci/msi.c` `b9f5b45920b66f33e34a8e85cb560536abe0d416`; `hw/pci/pci.c` `d3191609e283eb456c65473eb2ee1bc7c90222b1`. This demonstrates a PCI bus-master memory write to a guest-configured MSI address, **not** an Apple AIC interrupt endpoint or delivered guest interrupt.

Generation 40 independently established that the applied GPEX patch (`runtime/qemu/patches/0006-darwin-gpex-root-bus.patch`, blob `2163f92f4266b6fd64dff4cdb8aef4b5442d2cb3`) configures `num-irqs=0` and no GPEX→AIC INTx wiring. If NVMe falls back to INTx, this missing route is a prerequisite gap; a modulo-by-zero in a later swizzle path is a *conditional source hazard*, not a demonstrated crash. Neither Apple `#ports`, MSI doorbell address, IRQ number nor native controller semantics can be inferred from these facts.

## Minimum next evidence (ordered)

1. On the **exact built QEMU SHA**, establish the runtime value of `msi_nonbroken`, NVMe PCI MSI-X capability presence, and whether `msix_init` returned `-ENOTSUP` (logs or a narrowly scoped diagnostic trace). Preserve QEMU build SHA and trace provenance.
2. Record the guest's PCIe/IOKit provider ancestry and NVMe PCI configuration, including whether the guest enables MSI-X, programs a vector table/address, or selects INTx. A source assertion alone is insufficient.
3. If MSI-X is used, trace the programmed MSI address/data through QEMU's bus-master write to a **verified** interrupt sink; if INTx is used, establish an actual GPEX→AIC route and prevent zero-IRQ swizzle before claiming delivery. Do not guess Apple hardware ABI.
4. Only after provider binding and interrupts are evidenced, pursue non-ramdisk `/dev/disk*`, APFS SystemOS/Preboot/Data, and system launchd/core userland. Recovery `md0` or recovery shell is not Stage 1 completion.

## Verification and limitations

`scripts/audit_m3_nvme_msix_fallback.py --qemu-root <pinned-source-checkout>` is a fail-closed full-file source contract checker. It verifies exact Git blob SHA1 for five pinned QEMU files before inspecting named functions. Tests use synthetic fixtures and exercise negative controls. **Full-file checker on a materialized pinned QEMU checkout: NOT RUN in this runtime.** QEMU compilation, Windows CI, iPhoneOS SDK, guest E2E, interrupt delivery and Stage 1: **NOT RUN / NOT PROVEN**. Previous Windows Build `38711142165` and QEMU Gate `38711142120` passed on `50fff7ab` only; previous E2E `38676276954` failed at AppleEmbeddedPCIE missing `#ports`.
