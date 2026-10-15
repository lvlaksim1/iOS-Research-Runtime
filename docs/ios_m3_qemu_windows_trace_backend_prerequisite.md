# iOS M3 — Windows QEMU trace backend: static evidence prerequisite

Scope: `IOS-M3-CONTINUOUS-011`, baseline `50fff7ab8fc33fa1324ea204416f7a773a191033`, pinned QEMU `2867d847d3471560e773120ee50c42dbcbb6d60b`.

## Verified pinned source facts

- `meson_options.txt` Git blob `a07cb47d35e9b83636182c1b38f2f8ad84facabb`: default `trace_backends=['log']`.
- `meson.build` blob `49a5baf5b52fd257001b81d4212a129a0315cd11`: `CONFIG_TRACE_<BACKEND>` is generated from Meson option; tracetool receives the same backend list.
- `scripts/tracetool/backend/log.py` blob `9e3e5046f5f66f72079a0241b511d2f5f9fd33b0`: log backend checks `qemu_loglevel_mask(LOG_TRACE)` and calls `qemu_log`.
- `util/log.c` blob `7cffbc1bf89c34b60bddc357914af39ec6bbb34d`: `CONFIG_TRACE_LOG` adds `LOG_TRACE` when logging is configured.
- `hw/nvme/trace-events` blob `f97a6a11f3606434ad65b2f44710cd6d43527768`: declares `pci_nvme_irq_msix`, `pci_nvme_irq_pin`, `pci_nvme_irq_masked`.
- Published `.github/workflows/qemu-sptm-windows.yml` blob `9613fbe02f74b29883354d0d9b16b10d625ba9d8`: invokes `configure` without explicit trace backend override, **but only when `build.ninja` does not exist**; restores a cache with prefix restore keys; tests `-M help` but **does not test `-trace help` or execute a trace event**.

## Consequence

The pinned source **defaults to log tracing on a clean Meson configure**. This is **not** proof that the cached Windows artifact was configured with the log backend, that the trace event names are present in the compiled executable, that event output reaches stderr, or that NVMe/PCIe interrupt delivery works. A cached `build.ninja` may prevent reconfiguration, so the workflow must produce an artifact-specific runtime trace capability observation before accepting the trace path. The existing Windows Build and QEMU Gate successes apply only to published baseline SHA and do not establish full-system boot.

## Audit tool

`python scripts/audit_m3_qemu_trace_backend.py --workflow <verified workflow> --meson-options <verified QEMU meson_options.txt> --meson-build <verified QEMU meson.build> --nvme-events <verified QEMU hw/nvme/trace-events>`

The tool is offline and intentionally emits `compiled_windows_trace_backend=UNKNOWN`, `actual_qemu_irq_events=NOT_OBSERVED`, and `full_ios_system_boot=NOT_PROVEN`. The caller must verify **full source file bytes and Git blobs** separately. The tool checks static prerequisites only and exits 2 if any of the default-log, Meson wiring, or NVMe event declarations is missing. Its tests use synthetic fixtures; no Windows binary, dotnet8 build, QEMU guest, APFS mount, or system launchd execution has been performed.

## Smallest next evidence gate

Use the **actual packaged Windows QEMU binary** and its exact SHA to capture `-trace help` output for all three NVMe events, confirm the configured trace backend from build configuration/provenance, and perform an explicitly opt-in runtime event-capture test with bounded logs. Do not infer native Apple `#ports`, bypass a blocked GitHub mutation, or launch guest E2E before static/compile and build prerequisites pass.
