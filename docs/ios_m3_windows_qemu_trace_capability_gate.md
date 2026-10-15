# iOS M3 — Windows QEMU compiled trace capability gate

Package `IOS-M3-CONTINUOUS-011`; published baseline `50fff7ab8fc33fa1324ea204416f7a773a191033`; pinned QEMU fork `jprx/qemu-sptm` commit `2867d847d3471560e773120ee50c42dbcbb6d60b`.

## Why this gate is needed

The prior static audit (GEN46, Library change `iosm3c11-g0046-qemu-trace-backend-audit-d7d795f5cf3b`) showed that the pinned source defaults to a log trace backend, but the published Windows workflow can restore cached `build.ninja` and skip reconfiguration. Static Meson defaults do not prove capabilities of the **actual built Windows executable**.

At the pinned QEMU commit, `trace/control.c` (Git blob `49f0a4c5cda767c9b0749a5b14d1cc1dacecaa65`) defines `trace_enable_events()`: `-trace help` lists registered trace events via `trace_list_events(stdout)` and exits 0. `meson.build` (Git blob `49a5baf5b52fd257001b81d4212a129a0315cd11`) generates `CONFIG_TRACE_LOG` from `trace_backends` in `config-host.h`. The Windows workflow (Git blob `9613fbe02f74b29883354d0d9b16b10d625ba9d8`) currently verifies `-M help`, not `-trace help`.

## Operation (after Windows QEMU build, before packaging)

```powershell
python scripts/check_m3_windows_qemu_trace_capability.py --build-root qemu-sptm/build --binary qemu-sptm/build/qemu-system-aarch64.exe --output qemu-proof/trace-capability.json
if ($LASTEXITCODE -ne 0) { throw 'Compiled QEMU trace capability gate failed' }
```

The script must be present in the checkout and is **not** wired into the published workflow yet. It reads the Meson build's `meson-info/intro-buildoptions.json` and generated `config-host.h`, computes the exact binary SHA-256, executes that binary's `-trace help` and `-M help` with timeouts, and requires exact registered `pci_nvme_irq_msix`, `pci_nvme_irq_pin`, `pci_nvme_irq_masked` names plus a Darwin machine. It rejects missing evidence, wrong build directory, nonzero exits, excessive output, missing log backend, and optional expected-binary-SHA mismatch. The output contains an exact binary SHA-256 for later packaging correlation.

## Proof boundary

Passing means **compiled catalog and configuration capability for that particular binary SHA-256**, not proof of an actual NVMe interrupt, AIC/MSI-X delivery, Apple PCIe provider binding, non-ramdisk `/dev/disk*`, APFS SystemOS/Preboot/Data, or system launchd. `-trace help` lists names regardless of whether an event fires; `CONFIG_TRACE_LOG` and Meson introspection indicate configuration but do not demonstrate runtime delivery. A separate bounded opt-in trace capture is required before guest integration. The script does not start a guest, modify QEMU, change ADT `#ports`, or publish to GitHub. All local tests use synthetic subprocess results; no Windows executable was run in this work unit.

## Ordered acceptance

1. Run local syntax/tests (synthetic only); publish the script and its tests through a separately authorized normal GitHub change when possible.
2. Execute the gate in the **same** Windows build job against the exact compiled QEMU artifact; retain `trace-capability.json` and the executable SHA-256.
3. Correlate the packaged executable's SHA-256 and perform bounded opt-in trace event capture, then address PCIe/IOKit provider mapping and guest storage prerequisites in order.
4. Do not advance to guest E2E until earlier prerequisites and build/test evidence on the actual published SHA are satisfied.
