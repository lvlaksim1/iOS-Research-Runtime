# iPhoneOS SDK IOKit ABI prerequisite — isolated source probe

Project `lvlaksim1/iOS-Research-Runtime`; baseline `main` SHA `50fff7ab8fc33fa1324ea204416f7a773a191033`. This change depends on the unpublished GEN35 collector (`iosm3c11-g0035-ioreg-parent-lineage-20794261160b`) and the GEN37 build gate (`iosm3c11-g0037-iphoneos-build-gate-05b5c8b895a7`). It is an independent **diagnostic prerequisite**, not a modification of the Apple device tree or QEMU hardware model.

## Actual environment and remaining unknowns

The GEN38 runtime was Linux with a host `clang` but no `xcrun`/iPhoneOS SDK; a real target compile was **not** possible. The pinned upstream `Siguza/iokit-utils@df1d6b5172a19950edac74b8a05a28c12b34bba9` demonstrates its own iOS build recipe, not availability of the same headers/link symbols for this collector. The project Windows workflow only consumes an existing `ioprint` binary, and does not build the new collector.

## Distinct stage-level evidence

Run on a permitted macOS machine with an installed local iPhoneOS SDK:

`python3 scripts/probe_ios_m3_iokit_abi.py --source scripts/ios_m3_ioreg_lineage.c`

The script is read-only with respect to the repository. It uses a temporary directory, no network, no signing, no guest staging. It requires `xcrun --sdk iphoneos`, records the SDK version and exact source SHA-256, then tests in order: (1) compiler syntax/declarations for the actual collector and iPhoneOS SDK, (2) arm64 object compilation, (3) IOKit framework linking, (4) thin Mach-O arm64 executable header. Distinct failure stages prevent a missing SDK header from being misreported as a guest NVMe failure. No executable is retained. No stderr with potentially sensitive local paths is archived.

`COMPILE_LINK_PREREQUISITE_ONLY` establishes **only** compile/link feasibility for that SDK. It does not prove runtime IOKit access, codesigning, entitlements, IOService parent-child relations, PCIe/NVMe provider binding, non-ramdisk disks, APFS SystemOS+Preboot+Data or system launchd. The host synthetic tests exercise failure classification, not Apple SDK ABI.

**Proof ladder:** exact source SHA + local synthetic tests -> real iPhoneOS SDK compile/link -> permitted guest deployment/invocation (separate decision) -> real IORegistry evidence -> PCIe/NVMe and storage runtime proofs -> full Stage1. Earlier failure invalidates later steps for that target. Never infer the Apple `#ports` ABI from the synthetic GPEX configuration.
