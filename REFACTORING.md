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

## Next

1. Build and validate `qemu-sptm` for Windows x64.
2. Add tool manifest with pinned versions and SHA-256.
3. Implement Windows-native IPSW download/extraction.
4. Replace the macOS-only ramdisk preparation path.
5. Generate trust cache on Windows.
6. Boot a real prepared modern iOS bundle on Windows and archive the boot log.

## Explicitly deferred

- SpringBoard
- graphics/framebuffer
- touch input
- app installation
- Apple Account
- Family Sharing
- Screen Time
