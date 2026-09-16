# qemu-sptm upstream

The Windows runtime layer is initially pinned to:

- Repository: `jprx/qemu-sptm`
- Commit: `2867d847d3471560e773120ee50c42dbcbb6d60b`
- Upstream base: QEMU 11.1.0 era
- Target: `aarch64-softmmu`
- Machine: `darwin`

This repository does not vendor Apple firmware.

## Windows port gate

The first QEMU milestone is considered complete when CI can:

1. Build `qemu-system-aarch64.exe` on `windows-latest` with MSYS2/MINGW64.
2. Execute the binary on the same runner.
3. Verify that `-M help` lists `darwin`.
4. Publish the Windows binary and its required runtime DLLs as an artifact.

Only after this gate passes will the binary be bundled into the desktop application.


## Local compatibility patches

- `0001-win32-portability.patch`: Windows/MSYS2 portability only.
- `0002-fileset-entry-offset.patch`: parse `LC_FILESET_ENTRY.entry_id` through
  its Mach-O `lc_str` offset instead of assuming the string immediately follows
  `struct fileset_entry_command`. On lookup failure QEMU prints the fileset
  entries it actually parsed, which is retained in E2E boot evidence.


- `0003-win64-mach-o-abi.patch`: keeps Apple Mach-O `lc_str` on its on-disk
  32-bit-offset ABI for Win64/LLP64 hosts. Without this, `__LP64__` is absent
  under MinGW64, the obsolete pointer union member is enabled, and
  `fileset_entry_command` becomes 40 bytes instead of 32. A compile-time
  assertion prevents packaging a QEMU runtime with the wrong layout.


- `0004-early-boot-diagnostics.patch`: records the SPTM loader entrypoint,
  reset-time `init_pc/init_x0`, current EL, and the first four instruction
  words read back from guest RAM. The desktop boot command also enables QEMU's
  short ARM interrupt/exception log (`-d int`) while early Windows boot is
  being validated.

- `0005-win64-sptm-l2-mask.patch`: keeps the SPTM 36-bit L2 index mask
  64-bit on Windows. QEMU's `BIT(n)` expands to `1UL << n`; under the
  Win64 LLP64 ABI `unsigned long` is only 32-bit, so `BIT(36)` overflowed
  and `STRIP_L2_PT_INDEX()` collapsed `boot_args.virtBase` to zero.
  The patch uses `BIT_ULL(36)`, preserving the upstream layout and preventing
  SPTM from translating into low unmapped guest addresses after enabling EL2
  translation.
