# IOS-M3 IOService collector: build and invocation prerequisites (source-only)

Baseline `lvlaksim1/iOS-Research-Runtime@50fff7ab8fc33fa1324ea204416f7a773a191033`. Parent unpublished Library change: `iosm3c11-g0035-ioreg-parent-lineage-20794261160b`. This document does not authorize guest installation, change the ADT, or establish Stage 1 boot.

## Verified source contracts

- The exact pinned `Siguza/iokit-utils@df1d6b5172a19950edac74b8a05a28c12b34bba9` `Makefile` (blob `dee524d40b5868750d98aac948d7421f24d98d05`) uses `xcrun -sdk iphoneos clang`, `-arch armv7 -arch arm64`, `-framework IOKit -framework CoreFoundation -framework Security`, and ad-hoc codesigning for its *own* iOS utilities. This is evidence of an upstream build recipe, **not** proof that our collector compiles with the available SDK.
- Published `.github/workflows/windows-e2e.yml` (blob `aa5cc0e01e1e30d7db9046eb89d4781f645f6de8`) runs on Windows and downloads the pinned **prebuilt** iOS `ioprint` binary. It does not compile a new iOS C diagnostic. `Program.cs` (blob `1b0071cf1378d8006d4c0cfeb5c2634a117119a3`) stages only the hash-verified `ioprint` into a recovery sysroot; it does **not** stage `ios_m3_ioreg_lineage`.
- GEN35 collector `scripts/ios_m3_ioreg_lineage.c` includes `<IOKit/IOKitLib.h>` and calls `IORegistryCreateIterator`, `IOIteratorNext`, `IORegistryEntryGetRegistryEntryID`, `IORegistryEntryGetName`, `IOObjectGetClass`, `IORegistryEntryGetParentEntry`, `IOObjectRelease` on the `IOService` plane. Its host-mocked compilation does not validate the real iPhoneOS SDK declarations, linker symbols, entitlement restrictions or runtime behavior.

## New bounded build dependency

`python scripts/build_ios_m3_ioreg_lineage.py --source scripts/ios_m3_ioreg_lineage.c --output <new-output-path> --dry-run` produces a **NOT_COMPILED** plan on any host. Without `--dry-run`, the script requires macOS, a locally installed `xcrun` and `iphoneos` SDK, invokes only the explicit arm64/IOKit compiler/linker, verifies a thin Mach-O arm64 executable, and never overwrites an existing output. It performs no network requests, codesigning, installation, QEMU execution, or GitHub publication. A successful result is only `COMPILED_MACHO_ARM64_UNSIGNED_UNSTAGED`.

**Unknown:** availability of iPhoneOS SDK IOKitLib.h, public/private framework linkability, target OS support for the specific IORegistry APIs, executable signing/entitlements, guest execution and provenance of captured JSONL. None of these are established by a Linux host-mocked test. No real iOS compile or guest E2E was run in this change.

## Required next evidence

First, run the build gate on a permitted macOS+iPhoneOS SDK runner, capture SDK identity, compiler/linker result and output SHA for the exact source. If it fails, resolve the smallest source/API dependency before any guest test. Only after separately justified signing/staging and a controlled guest invocation can the GEN36 offline validator assess actual captured parent-ID relations. Parent-ID relations still do not prove NVMe driver binding, non-ramdisk disk enumeration, APFS mounting or system launchd.
