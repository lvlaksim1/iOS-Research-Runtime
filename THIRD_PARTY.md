# Third-party components

## qemu-sptm

Source: `https://github.com/jprx/qemu-sptm`

The project is a QEMU fork. Distribution of QEMU-derived binaries must continue
to comply with the licenses carried by the upstream source tree. We keep the
exact source commit pinned and do not remove upstream license notices.

## darwin-vm compatibility data

Source: `https://github.com/jprx/darwin-vm`

The DeviceTree fixup behavior is reimplemented natively in C# from the public
`dt_fixup.py` algorithm. The small `nvram.bin` template is tracked with its
upstream provenance so the Windows provisioning path can reproduce the
`darwin-vm` boot environment without requiring Python or macOS.

## Apple firmware

Apple IPSW/firmware is not redistributed in this repository or in application
artifacts. Provisioning obtains required firmware from Apple-controlled download
endpoints at runtime.

## Provisioning tools

- `blacktop/ipsw` — IPSW/IMG4 extraction.
- `deploymenttheory/go-apfs-v2` — cross-platform APFS/DMG manipulation.

Each distributed tool is version-pinned and verified by SHA-256 before use.
