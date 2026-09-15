# Architecture

## Boundary

iOS Research Runtime is a Windows desktop application. It owns lifecycle,
provisioning, diagnostics and presentation. The QEMU fork and Apple firmware are
runtime inputs, not application logic.

```text
WPF UI
  |
  v
RuntimeCoordinator
  |--------------------------|
  v                          v
FirmwareBundleValidator   QemuRuntime
  |                          |
  v                          v
Local runtime bundle      qemu-sptm.exe
                             |
                             v
                         -M darwin
                             |
                    SPTM / TXM / XNU
```

## Runtime locations

Application binaries are installed with the program. Large mutable runtime data
is stored below:

```text
%LOCALAPPDATA%\iOSResearchRuntime\
  firmware\
  logs\
  cache\
```

The QEMU executable is expected at:

```text
<application>\tools\qemu-sptm\qemu-system-aarch64.exe
```

## Firmware contract

Milestone 1 accepts a prepared firmware directory containing:

- `bootkc`
- `dtree`
- `ramdisk.tc`
- `ramdisk.dmg`
- optionally the pair `sptm` + `txm`

The next milestone will create this bundle on Windows directly from an Apple
IPSW.

## Design rules

- GUI-only operation for the end user.
- No required Python, Go, Rust, MSYS2, WSL, macOS or Xcode installation.
- External tools are isolated behind services and will be bundled/versioned.
- Apple firmware is never committed to this repository.
- Runtime state transitions are explicit and observable.
- A failed boot must leave enough log evidence to diagnose the exact stage.
