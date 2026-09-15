# Refactoring / engineering log

## 0.1.0 foundation

Initial architecture:

- Native Windows WPF application on .NET 8.
- Explicit runtime state model.
- Firmware bundle validation.
- QEMU process lifecycle service.
- `-M darwin` command construction for prepared firmware.
- Serial/stdout/stderr capture into the GUI.
- Windows commit-triggered build workflow.
- Pinned Windows provisioning tools with SHA-256 verification.
- Remote IPSW extraction for BootKC, SPTM, TXM, DeviceTree and recovery ramdisk.
- Native C# port of the `darwin-vm` DeviceTree fixup path.
- Native C# TrustCacheModule1 builder compatible with `darwin-vm/build_tc.py`.
- Windows CI unit tests for deterministic binary helpers.

## Next

1. Complete and validate the pinned `qemu-sptm` Windows x64 build gate.
2. Bundle the proven QEMU binary plus required MinGW runtime DLLs.
3. Implement metadata-preserving recovery ramdisk mutation on Windows.
4. Add ad-hoc Mach-O signing and CDHash extraction for injected iOS CLI tools.
5. Generate `ramdisk.tc` from the signed files.
6. Boot a real prepared modern iOS bundle on Windows and archive the boot log.

## Explicitly deferred

- SpringBoard
- graphics/framebuffer
- touch input
- app installation
- Apple Account
- Family Sharing
- Screen Time
