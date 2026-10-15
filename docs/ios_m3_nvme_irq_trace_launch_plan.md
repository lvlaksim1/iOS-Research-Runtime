# iOS M3 — safe QEMU NVMe IRQ trace launch plan (GEN43)

**Scope:** one independently useful diagnostic prerequisite. **Published application baseline:** `lvlaksim1/iOS-Research-Runtime@50fff7ab8fc33fa1324ea204416f7a773a191033`. **Pinned QEMU:** `jprx/qemu-sptm@2867d847d3471560e773120ee50c42dbcbb6d60b`. This file is not a runtime trace or full-system boot result.

## Why this plan exists

The current `QemuCommandBuilder.cs` (Git blob `023ef24eba4a3c96aa53caf0e69142864a308451`) launches the Darwin QEMU machine with `-D qemu-debug.log`, `-d ...`, and NVMe host probe arguments, **but does not enable NVMe IRQ trace events**. `QemuRuntime.cs` (blob `52be6cc53a445039d5cbc5b37085df84ff17f513`) already captures QEMU stderr separately in `BootEvidenceCapture` (blob `db3050fb9328a259413bc75bf3e1b7665d9b5399`). Its `boot-*.stderr.log` can therefore carry log-backend trace events without modifying guest DeviceTree, PCI topology or boot acceptance.

The pinned QEMU documentation `docs/devel/tracing.rst` (blob `f4557ee20e4b9111581e3e4d5287a59fd0f40a53`) states that the default trace backend is **log**, that it sends trace events to **stderr**, and that `-trace events=<file>` enables an explicit event list. The pinned `hw/nvme/trace-events` (blob `f97a6a11f3606434ad65b2f44710cd6d43527768`) contains `pci_nvme_irq_msix`, `pci_nvme_irq_pin`, `pci_nvme_irq_masked`. The actual compiled Windows QEMU binary's trace backend is **not verified** by this source check. `qemu-sptm-windows.yml` (blob `9613fbe02f74b29883354d0d9b16b10d625ba9d8`) does not explicitly select a trace backend, but the build artifact must still be checked.

## Safe preparation and consumption

`prepare_m3_nvme_irq_trace.py` is a **non-executing** host-side helper. It verifies an existing QEMU binary against an **independently supplied** SHA-256, enforces the exact pinned QEMU and product commit identities, writes exactly three trace event names, and emits a deterministic JSON plan with two separate argv elements: `-trace` and `events=<absolute-file>`. It does not run QEMU, change the guest or alter the main application. It rejects comma-containing paths (ambiguous in QEMU's key-value argument), conflicting pre-existing files, missing binaries, mismatched hashes and ambiguous paths. Exact repeated preparations reuse identical files without overwriting them.

Example invocation after staging the exact Windows QEMU artifact and independently establishing its SHA-256:

```text
python scripts/prepare_m3_nvme_irq_trace.py \
  --qemu-binary <staged-qemu-system-aarch64.exe> \
  --expected-binary-sha256 <independent-64-hex-sha256> \
  --qemu-source-commit 2867d847d3471560e773120ee50c42dbcbb6d60b \
  --product-main-commit 50fff7ab8fc33fa1324ea204416f7a773a191033 \
  --trace-events <absolute-log-dir>/ios-m3-nvme-irq-events.txt \
  --stderr-log <absolute-boot-stderr-path> \
  --output-plan <absolute-log-dir>/nvme-irq-trace-plan.json
```

**Integration prerequisite:** the caller must append the JSON `qemu_trace_arguments` to the **actual** QEMU argv as separate elements and preserve the actual stderr stream. The existing `QemuRuntime` currently does not consume this plan automatically. A subsequent permitted, reviewed integration step must implement this optional wiring and verify it in Windows Build/QEMU Gate before any guest E2E. Do not claim an emitted trace merely because this plan exists. When using the default log backend, the same real `boot-*.stderr.log` is passed as both `--trace-log` and `--stderr-log` to the GEN42 `scripts/inspect_m3_nvme_irq_runtime.py` analyzer; this is not an independent second observation.

The plan includes the analyzer command but does not execute it. The GEN42 analyzer itself only establishes **which QEMU NVMe IRQ code branch emitted trace text** when supplied authentic run evidence; it does not establish successful interrupt delivery to Apple AIC, guest PCIe/IOKit binding, a non-ramdisk `/dev/disk*`, APFS SystemOS/Preboot/Data mounts or system `launchd`. An `MSI-X is not supported by interrupt controller` warning is not automatically attributable to NVMe.

## Evidence ladder and next dependency

- **Static/source:** pinned QEMU event names and log-backend behavior read from exact source; current app command builder and stderr capture paths read at exact published SHA.
- **Local synthetic tests:** test the planner's fail-closed file and identity semantics only. A synthetic binary is not QEMU.
- **Windows Build / QEMU Gate:** NOT RUN for this unpublished helper; actual backend and argv support unverified.
- **Runtime integration:** NOT RUN; no authentic trace or guest state observed.
- **Full iOS Stage 1:** NOT PROVEN. The previous E2E failed at AppleEmbeddedPCIE missing `#ports`; no native `#ports` value has been inferred.

This change is independent of the explicitly safety-blocked GitHub `update_ref` for commit `49d5de208e7b797c1acb2e48cf3e0dff20ea0948`. No attempt to repeat or reroute that operation is authorized.
