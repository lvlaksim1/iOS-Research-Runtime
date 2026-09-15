# Windows Mach-O signing

The initial implementation uses `rcodesign` from:

- Repository: `indygreg/apple-platform-rs`
- Release: `apple-codesign/0.29.0`
- Asset: `apple-codesign-0.29.0-x86_64-pc-windows-msvc.zip`

The CI gate downloads the upstream checksum sidecar, verifies the archive, then
uses the Windows executable to ad-hoc sign an iOS Mach-O fixture.

For the trust cache, the primary CodeDirectory SHA-256 is truncated to the first
20 bytes (40 hexadecimal characters), matching Apple's SHA-256 CDHash format
used by the `darwin-vm` TrustCacheModule1 builder.
