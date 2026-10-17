#!/usr/bin/env python3
"""Fail-closed Mach-O architecture/platform preflight for the pinned iOS ioprint.

This is a static binary-format check, not a proof that ioprint executes in a guest.
The accepted slice must be 64-bit little-endian arm64 MH_EXECUTE and explicitly
advertise iOS through LC_BUILD_VERSION or LC_VERSION_MIN_IPHONEOS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

CPU_TYPE_ARM64 = 0x0100000C
MH_EXECUTE = 2
LC_VERSION_MIN_IPHONEOS = 0x25
LC_BUILD_VERSION = 0x32
LC_VERSION_MIN_OTHER = {0x24, 0x2F, 0x30}
PLATFORM_IOS = 2
MAX_BINARY_BYTES = 64 * 1024 * 1024
MAX_FAT_ARCHES = 32
MAX_FAT_ALIGN_EXPONENT = 26  # 2**26 is the maximum allowed input size.
MAX_LOAD_COMMANDS = 4096


class MachOValidationError(ValueError):
    """Malformed, ambiguous, or incompatible Mach-O input."""


def _thin64(data: bytes) -> dict[str, object]:
    if len(data) < 32 or data[:4] != b"\xcf\xfa\xed\xfe":
        raise MachOValidationError("expected little-endian 64-bit Mach-O")
    _, cpu, subtype, filetype, ncmds, sizeofcmds, _, _ = struct.unpack_from(
        "<IiiIIIII", data
    )
    if cpu != CPU_TYPE_ARM64:
        raise MachOValidationError("Mach-O CPU is not arm64")
    if filetype != MH_EXECUTE:
        raise MachOValidationError("Mach-O file type is not MH_EXECUTE")
    if not 0 < ncmds <= MAX_LOAD_COMMANDS:
        raise MachOValidationError("invalid load command count")
    if sizeofcmds < 8 * ncmds or sizeofcmds > len(data) - 32:
        raise MachOValidationError("invalid load command region")

    end = 32 + sizeofcmds
    pos = 32
    evidence: list[str] = []
    build_version_count = 0
    min_version_count = 0
    for _ in range(ncmds):
        if pos + 8 > end:
            raise MachOValidationError("load command header out of bounds")
        cmd, cmdsize = struct.unpack_from("<II", data, pos)
        if cmdsize < 8 or cmdsize % 8 or pos + cmdsize > end:
            raise MachOValidationError("invalid load command size")
        if cmd == LC_BUILD_VERSION:
            build_version_count += 1
            if cmdsize < 24:
                raise MachOValidationError("truncated LC_BUILD_VERSION")
            platform = struct.unpack_from("<I", data, pos + 8)[0]
            ntools = struct.unpack_from("<I", data, pos + 20)[0]
            if ntools > (cmdsize - 24) // 8:
                raise MachOValidationError("truncated LC_BUILD_VERSION tools")
            if platform != PLATFORM_IOS:
                raise MachOValidationError("LC_BUILD_VERSION platform is not iOS")
            evidence.append("LC_BUILD_VERSION(platform=2)")
        elif cmd == LC_VERSION_MIN_IPHONEOS:
            min_version_count += 1
            if cmdsize < 16:
                raise MachOValidationError("truncated LC_VERSION_MIN_IPHONEOS")
            evidence.append("LC_VERSION_MIN_IPHONEOS")
        elif cmd in LC_VERSION_MIN_OTHER:
            raise MachOValidationError("non-iOS LC_VERSION_MIN command")
        pos += cmdsize
    if pos != end:
        raise MachOValidationError("load command region length mismatch")
    if build_version_count > 1 or min_version_count > 1:
        raise MachOValidationError("ambiguous duplicate platform commands")
    if not evidence:
        raise MachOValidationError("missing explicit iOS platform load command")
    return {
        "cpu_type": "arm64",
        "cpu_subtype": subtype & 0x00FFFFFF,
        "file_type": "MH_EXECUTE",
        "platform": "iOS",
        "platform_evidence": evidence,
    }


def validate_macho(data: bytes) -> dict[str, object]:
    """Return a verified format summary; reject malformed/ambiguous inputs."""
    if len(data) > MAX_BINARY_BYTES:
        raise MachOValidationError("binary exceeds size limit")
    if data[:4] == b"\xcf\xfa\xed\xfe":
        result = _thin64(data)
        result["container"] = "thin64"
    elif data[:4] in (b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca",
                       b"\xca\xfe\xba\xbf", b"\xbf\xba\xfe\xca"):
        magic = data[:4]
        endian = ">" if magic in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf") else "<"
        fat64 = magic in (b"\xca\xfe\xba\xbf", b"\xbf\xba\xfe\xca")
        entry_size = 32 if fat64 else 20
        if len(data) < 8:
            raise MachOValidationError("truncated FAT header")
        count = struct.unpack_from(endian + "I", data, 4)[0]
        if not 0 < count <= MAX_FAT_ARCHES or 8 + count * entry_size > len(data):
            raise MachOValidationError("invalid FAT architecture table")
        slices: list[tuple[int, int, int, int]] = []
        ranges: list[tuple[int, int]] = []
        for i in range(count):
            start = 8 + i * entry_size
            if fat64:
                cpu, subtype, offset, size, align, reserved = struct.unpack_from(
                    endian + "iiQQII", data, start
                )
                if reserved != 0:
                    raise MachOValidationError("nonzero FAT64 reserved field")
            else:
                cpu, subtype, offset, size, align = struct.unpack_from(
                    endian + "iiIII", data, start
                )
            if align > MAX_FAT_ALIGN_EXPONENT:
                raise MachOValidationError("FAT alignment exponent out of bounds")
            if offset % (1 << align):
                raise MachOValidationError("misaligned FAT slice offset")
            if not size or offset < 8 + count * entry_size or offset + size > len(data):
                raise MachOValidationError("invalid FAT slice bounds")
            ranges.append((offset, offset + size))
            if cpu == CPU_TYPE_ARM64:
                slices.append((cpu, subtype, offset, size))
        ordered = sorted(ranges)
        if any(ordered[i][1] > ordered[i + 1][0] for i in range(len(ordered) - 1)):
            raise MachOValidationError("overlapping FAT slices")
        if len(slices) != 1:
            raise MachOValidationError("FAT must contain exactly one arm64 slice")
        _, subtype, offset, size = slices[0]
        result = _thin64(data[offset:offset + size])
        if result["cpu_subtype"] != (subtype & 0x00FFFFFF):
            raise MachOValidationError("FAT table and arm64 slice subtype mismatch")
        result["container"] = "fat64" if fat64 else "fat32"
    else:
        raise MachOValidationError("unrecognized Mach-O magic")
    result["file_size_bytes"] = len(data)
    result["sha256"] = hashlib.sha256(data).hexdigest()
    result["scope"] = "static-format-only; guest execution not verified"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.input.stat().st_size > MAX_BINARY_BYTES:
            raise MachOValidationError("binary exceeds size limit")
        result = validate_macho(args.input.read_bytes())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("MACHO_IOS_ARM64_STATIC_GATE_PASS")
        return 0
    except (MachOValidationError, OSError) as exc:
        print(f"MACHO_IOS_ARM64_STATIC_GATE_FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
