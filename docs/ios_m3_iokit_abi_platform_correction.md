# iPhoneOS IOKit ABI probe: target-platform validation (GEN39)

Repository: `lvlaksim1/iOS-Research-Runtime`. Published baseline: `50fff7ab8fc33fa1324ea204416f7a773a191033`. This source-only correction depends on the independently verified but **unpublished** GEN38-A ABI-probe archive `iosm3c11-g0038-iphoneos-abi-prerequisite-04e35880d40f`, itself dependent on GEN37 and GEN35. GEN38-B's separate Mach-O build-gate correction is a sibling change and is not overwritten or republished by this package.

## Defect and bounded correction

GEN38-A's `_verify_macho()` accepted any thin arm64 `MH_EXECUTE` header. A macOS arm64 executable could therefore be reported as `COMPILE_LINK_PREREQUISITE_ONLY`, despite lacking iPhoneOS platform evidence. This is an invalid proof gate; it does **not** establish that an actual collector was compiled incorrectly (none has been compiled with an Apple iPhoneOS SDK).

The probe now passes `-target arm64-apple-ios` and the exact SDK sysroot in its syntax, object and linker commands. It checks Mach-O load commands and requires `LC_BUILD_VERSION` with iOS platform `2`, or the legacy `LC_VERSION_MIN_IPHONEOS`. Missing, conflicting, malformed and truncated platform commands fail closed. The result is still only compile/link metadata, never guest execution or storage proof.

## Observations and limits

The GEN38-A ZIP was discovered in the native Library listing with actual `file_id=file_0000000099b081f7929d41f4e7211789` and archive SHA-256 `c9d1742ccaf1eb2b0d688f63a35e9d86155ab2dfb67e5c4ac9d04a45c243d46c`. Its manifest, parent and all three file SHA-256 values were independently verified, although the prior live Mailbox had omitted this archive following the GEN38-A/GEN38-B failover. It must be preserved as a distinct verified pending result, not mistaken for GitHub publication or discarded. GEN38-B ZIP remains separate, with its own file ID and SHA.

The available host is Linux with `clang`, but without `xcrun` or an installed iPhoneOS SDK. Running the corrected probe on the **exact GEN35 C collector** returned `NOT_PROVEN`, stage `SDK`, reason `requires_macos`, exit code `2`, source SHA-256 `7ca706ef594df4d458fd471c3549c86f1ca449e21afa19bf28cfbb3b643c938d`. Synthetic host tests passed `16/16`, including rejection of a macOS arm64 executable, absent/truncated/conflicting commands, and acceptance of both iOS platform encodings. `py_compile` passed. These tests use generated mock Mach-O bytes; no Apple SDK compilation, IOKit link, signing, guest execution or Windows CI was performed.

The next real prerequisite is to execute the exact collector's syntax/object/link checks on a permitted macOS host with a real local iPhoneOS SDK and record SDK identity and compiler/linker outcomes. If `IOKit/IOKitLib.h` or `IOKit.framework` is unavailable for that SDK, stop at the corresponding stage; do not infer a guest PCIe/NVMe problem. Stage 1 remains unproven until actual PCIe/IOKit binding, guest NVMe, non-ramdisk `/dev/disk*`, APFS SystemOS/Preboot/Data, and system `launchd`/core userland are independently evidenced.
