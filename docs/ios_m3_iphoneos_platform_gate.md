# iOS M3: Mach-O platform provenance prerequisite (GEN38, source-only)

Baseline `lvlaksim1/iOS-Research-Runtime@50fff7ab8fc33fa1324ea204416f7a773a191033`. This unpublished change depends on `iosm3c11-g0037-iphoneos-build-gate-05b5c8b895a7` (which depends on GEN35 collector). It **does not** alter ADT, QEMU, guest storage, signing or published Git refs.

## Reproducible observation

The earlier GEN37 build gate checked only the Mach-O magic, CPU type ARM64 and file type MH_EXECUTE. Those properties also describe a macOS arm64 executable, so they cannot establish the `iphoneos` platform. A synthetic macOS Mach-O previously passed this insufficient check. This is a target-invalidating deficiency for the proposed evidence of an iOS binary, **not** proof that any actual previously built artifact was wrong (none was built).

This GEN38 revision adds an explicit `-target arm64-apple-ios` and `-isysroot <resolved iphoneos SDK>` compiler invocation, and parses the bounded Mach-O load-command table. It accepts an arm64 executable only if either `LC_BUILD_VERSION` (`0x32`) identifies `PLATFORM_IOS` (`2`) or the legacy `LC_VERSION_MIN_IPHONEOS` (`0x25`) identifies iOS; malformed/truncated or conflicting commands fail closed. A macOS arm64 executable is rejected, as are binaries with no platform evidence. The output remains unsigned and unstaged.

On the available **Linux** host, a separate trivial source (`int main(void){return 0;}`) was compiled to a Mach-O *object* with local `clang -target arm64-apple-ios -c`, and the object carried `LC_VERSION_MIN_IPHONEOS` (`0x25`). The same source compiled with `-target arm64-apple-ios12.0 -c` carried `LC_BUILD_VERSION` (`0x32`) with platform `2`. This observation explains why the gate must recognize both encodings. The trivial objects were discarded; they are not collector builds, not executable images, and not part of the archive.

## Local verification and outstanding evidence

The updated Python build-gate tests passed **16/16**, including positive iOS platform cases and negative macOS/missing/truncated command cases. `python -m py_compile` passed for the two Python files. Dry-run of the exact GEN35 C collector reported `NOT_COMPILED`. No macOS/iPhoneOS SDK is installed in this Linux runtime; actual `IOKit/IOKitLib.h` declarations, linking, target compatibility, signing, guest invocation and guest output remain **NOT VERIFIED**.

The next permitted dependency is a real macOS+iPhoneOS SDK compilation of the **exact** GEN35 collector through this gate, recording SDK identity, linker result, Mach-O platform and binary SHA. Do not attempt guest E2E or claim PCIe/NVMe binding, non-ramdisk `/dev/disk*`, APFS SystemOS/Preboot/Data or system launchd based on these host-only tests.
