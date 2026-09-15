# Third-party components

## qemu-sptm

Source: `https://github.com/jprx/qemu-sptm`

The project is a QEMU fork. Distribution of QEMU-derived binaries must continue
to comply with the licenses carried by the upstream source tree. We keep the
exact source commit pinned and do not remove upstream license notices.

## Apple firmware

Apple IPSW/firmware is not redistributed in this repository or in application
artifacts. Provisioning will obtain required firmware from Apple-controlled
download endpoints at runtime.

## Planned tooling

Windows-native provisioning is expected to use independently versioned tools or
libraries for IPSW extraction, APFS image manipulation and ad-hoc Mach-O code
signing. Each component will be pinned and documented before it is bundled.
