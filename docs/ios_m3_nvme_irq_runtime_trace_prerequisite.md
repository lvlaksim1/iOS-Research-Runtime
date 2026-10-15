# iOS M3 — NVMe IRQ runtime trace prerequisite (source-backed, not E2E)

**Published application baseline:** `lvlaksim1/iOS-Research-Runtime@50fff7ab8fc33fa1324ea204416f7a773a191033`. **Pinned QEMU:** `jprx/qemu-sptm@2867d847d3471560e773120ee50c42dbcbb6d60b`.

## Source-backed trace points

The pinned `hw/nvme/ctrl.c` Git blob `4893cf7e7418d3cf8a5a27d7e458d700c6fcc7b8` emits `trace_pci_nvme_irq_msix(vector)` only in the `msix_enabled(pci)` branch of `nvme_irq_assert`, and `trace_pci_nvme_irq_pin()` in its INTx branch. It also emits `trace_pci_nvme_irq_masked()` when the completion queue has IRQ disabled. The pinned `hw/nvme/trace-events` blob `f97a6a11f3606434ad65b2f44710cd6d43527768` defines exact text: `raising MSI-X IRQ vector %u`, `pulsing IRQ pin`, `IRQ is masked`.

The pinned `hw/pci/msix.c` blob `1b23eaf10079f9f7501aae25f7826020c49d2e25` emits `MSI-X is not supported by interrupt controller` when `msi_nonbroken` is false and returns `-ENOTSUP`. In `nvme_init_pci`, `-ENOTSUP` is downgraded to a warning and device initialization continues. A warning from a mixed-device QEMU process cannot by itself be attributed to NVMe.

Pinned QEMU tracing documentation `docs/devel/tracing.rst` blob `f4557ee20e4b9111581e3e4d5287a59fd0f40a53` describes `--trace events=<file>`, log backend format `thread@timestamp:event ...`, and `info trace-events`. Trace backend choice is a build-time configuration; **verify that the actual executable uses the log backend**. The supplied `trace-events` file should contain these exact lines:

```text
pci_nvme_irq_msix
pci_nvme_irq_pin
pci_nvme_irq_masked
```

Capture a *real* run with that events file and separate QEMU trace/stderr logs, retaining the exact executable, its SHA-256, command line, build provenance, and raw guest observations. Do not upload large binaries or secrets. Example analysis (no guest launch or network access by this script):

```text
python scripts/inspect_m3_nvme_irq_runtime.py \
  --qemu-binary <actual-qemu-executable> \
  --expected-binary-sha256 <sha256-from-independent-build-evidence> \
  --trace-log <qemu-log-backend-text> \
  --stderr-log <qemu-stderr-text> \
  --trace-events <exact-enabled-event-file> \
  --qemu-source-commit 2867d847d3471560e773120ee50c42dbcbb6d60b \
  --product-main-commit 50fff7ab8fc33fa1324ea204416f7a773a191033 \
  --output <analysis.json>
```

Exit codes: `0` = at least one syntactically valid NVMe IRQ trace event; `2` = no valid event, not a failure of NVMe and not a boot acceptance; `3` = invalid/missing/mismatched evidence. The script verifies binary SHA, trace config and input SHA, rejects malformed event-like lines, reports branch counts, and **never** asserts AIC delivery, guest PCIe/IOKit binding, non-ramdisk disk, APFS mount or system launchd.

## Evidence ladder and unresolved dependency

Synthetic unit tests validate only parser behavior. Full pinned-source QEMU build, Windows integration, real guest trace, `msi_nonbroken` value, MSI-X initialization return value, guest PCI configuration, actual MSI doorbell and Apple AIC sink remain **NOT PROVEN**. The earliest target-invalidating evidence would be a genuine INTx branch with no GPEX-to-AIC route or a verified MSI-X write with no sink; correct the smallest source dependency before E2E. Do not guess native Apple `#ports` or treat recovery `md0` as system boot. This diagnostic is a **distinct read-only runtime prerequisite**, not the previously safety-blocked ADT source mutation.
