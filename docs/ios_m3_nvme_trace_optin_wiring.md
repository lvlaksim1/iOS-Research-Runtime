# iOS M3 — opt-in NVMe IRQ trace wiring (GEN44)

**Product baseline:** `lvlaksim1/iOS-Research-Runtime@50fff7ab8fc33fa1324ea204416f7a773a191033`.
**Pinned QEMU:** `jprx/qemu-sptm@2867d847d3471560e773120ee50c42dbcbb6d60b`.
**Unpublished dependency:** `iosm3c11-g0043-trace-launch-plan-707e2510c745` (GEN43), itself dependent on GEN42. This is a prepared source change, **not a GitHub commit or runtime acceptance**.

## Source-backed gap

The published `src/IOSResearchRuntime/Services/QemuCommandBuilder.cs` Git blob `023ef24eba4a3c96aa53caf0e69142864a308451` does not pass `-trace`. `QemuRuntime.cs` Git blob `52be6cc53a445039d5cbc5b37085df84ff17f513` already captures QEMU stderr separately through `BootEvidenceCapture`; no runtime stream change is needed for the pinned QEMU *documented* log trace backend. The actual Windows QEMU build's trace backend is **not yet verified**.

## Bounded implementation

`QemuCommandBuilder.BuildArguments()` appends the result of `QemuNvmeTraceOptIn.GetArguments(_layout)` once. **Default:** absent `IOS_M3_NVME_IRQ_TRACE_PLAN` environment variable returns an empty list; the baseline QEMU arguments, PCIe/NVMe devices, firmware, boot parameters and output streams are unchanged. The new helper does not execute QEMU.

**Opt-in:** set `IOS_M3_NVME_IRQ_TRACE_PLAN` to the absolute path of the GEN43 `prepare_m3_nvme_irq_trace.py` JSON plan, with the plan and event file located under the runtime log directory. The helper verifies:

1. The plan is a regular, non-reparse file under the log directory, at most 64 KiB; paths are absolute and reject comma, equals sign and control characters.
2. Plan schema, pinned QEMU source commit, exact published product commit and expected `log` backend match.
3. Planned QEMU executable equals the runtime's executable; its current bytes are independently SHA-256 checked against the plan and its length is bounded to 1 GiB.
4. The event file is a regular, non-reparse file under the log directory and contains **exactly** `pci_nvme_irq_msix`, `pci_nvme_irq_pin`, `pci_nvme_irq_masked` in that order with final newline; SHA-256 is independently checked.
5. The plan contains exactly `qemu_trace_arguments = ["-trace", "events=<canonical absolute event file>"]`. Arguments are appended as separate `ProcessStartInfo.ArgumentList` entries, not a shell string.

Invalid opt-in fails before `process.Start()`, rather than silently running an untraced guest. There is no change to Apple DeviceTree, AIC, GPEX `num-irqs`, PCI topology, guest disk contents, or boot acceptance.

## Verification and limits

Static/source checks compare the modified command builder with the exact original Git blob and require only the one opt-in insertion. Python source-contract tests also check plan compatibility using a **synthetic fake binary**, not real QEMU. This verifies the shape of the prepared change but **does not compile C#** or demonstrate the Windows binary's trace backend. A real Windows .NET 8 build, QEMU Gate and then a controlled runtime capture must be performed against the exact resulting published SHA before guest E2E.

If the runtime emits authentic trace lines, analyze the same `boot-*.stderr.log` through the GEN42 analyzer, with a real binary hash and boot evidence. A trace event shows an NVMe IRQ code path only; it **does not prove** Apple AIC delivery, PCIe/IOKit binding, non-ramdisk `/dev/disk*`, APFS SystemOS/Preboot/Data mounts, system launchd, or full Stage 1.

**Safety:** no retry of the explicitly blocked `update_ref` for `49d5de208e7b797c1acb2e48cf3e0dff20ea0948`; no forced Git refs, release, heavy binaries, or manager-state modification. This package is stored separately as pending source until an independently permitted publication path exists.
