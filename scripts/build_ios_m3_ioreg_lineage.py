#!/usr/bin/env python3
"""Build gate for the source-only IOService lineage collector (never a boot proof).

This script does not download SDKs, stage files into a guest, sign binaries,
launch QEMU or claim that a compiled executable runs in iOS. A successful
local build establishes only a Mach-O arm64 executable for an explicit SDK.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
import tempfile

ARM64_CPU_TYPE = 0x0100000C
MH_EXECUTE = 2
MH_MAGIC_64_LE = b"\xcf\xfa\xed\xfe"
MAX_SOURCE_BYTES = 256 * 1024
LC_BUILD_VERSION = 0x32
LC_VERSION_MIN_MACOSX = 0x24
LC_VERSION_MIN_IPHONEOS = 0x25
LC_VERSION_MIN_TVOS = 0x2F
LC_VERSION_MIN_WATCHOS = 0x30
LEGACY_PLATFORM_COMMANDS = {LC_VERSION_MIN_MACOSX, LC_VERSION_MIN_IPHONEOS,
                            LC_VERSION_MIN_TVOS, LC_VERSION_MIN_WATCHOS}
PLATFORM_IOS = 2
MAX_LOAD_COMMANDS = 4096


class BuildGateError(RuntimeError):
    pass


def _run(command: list[str], *, timeout: int = 120) -> str:
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BuildGateError(f"tool_unavailable_or_timeout:{type(exc).__name__}") from exc
    if proc.returncode:
        raise BuildGateError(f"tool_failed:exit={proc.returncode}:command={Path(command[0]).name}")
    return proc.stdout.strip()


def _macho_arm64_executable(path: Path) -> None:
    """Require a thin arm64 MH_EXECUTE *for iOS*, not a macOS arm64 binary.

    Mach-O CPU type alone cannot distinguish an iOS target from macOS.
    Accept either LC_BUILD_VERSION/PLATFORM_IOS (2), or the legacy
    LC_VERSION_MIN_IPHONEOS command used by some valid iOS compiler targets.
    Fail closed for missing, conflicting, truncated or malformed commands.
    """
    data = path.read_bytes()
    if len(data) < 32 or data[:4] != MH_MAGIC_64_LE:
        raise BuildGateError("output_not_thin_macho64")
    cpu_type, _, file_type, ncmds, sizeofcmds, _, _ = struct.unpack_from("<IIIIIII", data, 4)
    if cpu_type != ARM64_CPU_TYPE or file_type != MH_EXECUTE:
        raise BuildGateError("output_wrong_arch_or_filetype")
    if ncmds == 0 or ncmds > MAX_LOAD_COMMANDS or sizeofcmds > len(data) - 32:
        raise BuildGateError("output_invalid_load_commands")
    offset = 32
    end = 32 + sizeofcmds
    platform = None
    legacy_platform = None
    for _ in range(ncmds):
        if offset + 8 > end:
            raise BuildGateError("output_invalid_load_commands")
        cmd, cmdsize = struct.unpack_from("<II", data, offset)
        if cmdsize < 8 or cmdsize % 8 != 0 or offset + cmdsize > end:
            raise BuildGateError("output_invalid_load_commands")
        if cmd == LC_BUILD_VERSION:
            if cmdsize < 24:
                raise BuildGateError("output_invalid_build_version")
            current = struct.unpack_from("<I", data, offset + 8)[0]
            if platform is not None and platform != current:
                raise BuildGateError("output_conflicting_platforms")
            platform = current
        if cmd in LEGACY_PLATFORM_COMMANDS:
            if cmdsize != 16:
                raise BuildGateError("output_invalid_legacy_version")
            if legacy_platform is not None and legacy_platform != cmd:
                raise BuildGateError("output_conflicting_platforms")
            legacy_platform = cmd
        offset += cmdsize
    if offset != end:
        raise BuildGateError("output_invalid_load_commands")
    if platform is not None:
        if platform != PLATFORM_IOS or (legacy_platform is not None and legacy_platform != LC_VERSION_MIN_IPHONEOS):
            raise BuildGateError("output_not_iphoneos_platform")
    elif legacy_platform != LC_VERSION_MIN_IPHONEOS:
        raise BuildGateError("output_not_iphoneos_platform")


def build(source: Path, output: Path, *, dry_run: bool = False, host_system: str | None = None) -> dict:
    source = source.resolve(strict=True)
    if not source.is_file() or not (0 < source.stat().st_size <= MAX_SOURCE_BYTES):
        raise BuildGateError("invalid_source")
    raw = source.read_bytes()
    if b"IOS_M3_HOST_TEST" not in raw or b"IORegistryEntryGetParentEntry" not in raw:
        raise BuildGateError("not_expected_collector_source")
    source_sha = hashlib.sha256(raw).hexdigest()
    if output.exists() or output.is_symlink():
        raise BuildGateError("output_already_exists_no_overwrite")
    if source == output.resolve():
        raise BuildGateError("source_equals_output")
    plan = {
        "source_sha256": source_sha,
        "sdk": "iphoneos",
        "architecture": "arm64",
        "compiler": "xcrun -sdk iphoneos clang -target arm64-apple-ios",
        "required_macho_platform": "PLATFORM_IOS(2) or LC_VERSION_MIN_IPHONEOS",
        "link_framework": "IOKit",
        "status": "NOT_COMPILED",
        "guest_execution_proven": False,
        "driver_binding_proven": False,
        "full_system_boot_accepted": False,
    }
    if dry_run:
        return plan
    if (host_system or platform.system()) != "Darwin":
        raise BuildGateError("requires_macos_xcode_iphoneos_sdk")
    xcrun = shutil.which("xcrun")
    if not xcrun:
        raise BuildGateError("xcrun_not_available")
    sdk_path = Path(_run([xcrun, "-sdk", "iphoneos", "--show-sdk-path"]))
    if not sdk_path.is_dir():
        raise BuildGateError("iphoneos_sdk_missing")
    clang_path = Path(_run([xcrun, "-sdk", "iphoneos", "--find", "clang"]))
    if not clang_path.is_file():
        raise BuildGateError("iphoneos_clang_missing")
    # The iOS SDK may not expose IOKitLib.h or IOKit.framework. Let the
    # compiler/linker fail; do not silently use a macOS SDK or fake headers.
    if not output.parent.is_dir():
        raise BuildGateError("output_parent_missing")
    with tempfile.TemporaryDirectory(dir=output.parent, prefix="iosm3-ioreg-") as tmp:
        candidate = Path(tmp) / "lineage"
        _run([xcrun, "-sdk", "iphoneos", "clang", "-target", "arm64-apple-ios", "-arch", "arm64",
              "-isysroot", str(sdk_path), "-O2", "-Wall", "-Wextra", "-Werror", "-framework", "IOKit",
              "-o", str(candidate), str(source)])
        if not candidate.is_file():
            raise BuildGateError("compiler_no_output")
        _macho_arm64_executable(candidate)
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        # The output is intentionally unsigned and unstaged. Signing and
        # guest compatibility require separate explicit evidence.
        os.replace(candidate, output)
    return {**plan, "status": "COMPILED_MACHO_ARM64_UNSIGNED_UNSTAGED",
            "binary_sha256": digest, "sdk_path": str(sdk_path),
            "guest_execution_proven": False, "driver_binding_proven": False,
            "full_system_boot_accepted": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = build(args.source, args.output, dry_run=args.dry_run)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (BuildGateError, OSError) as exc:
        print(json.dumps({"status": "NOT_COMPILED", "reason": str(exc),
                          "guest_execution_proven": False,
                          "driver_binding_proven": False,
                          "full_system_boot_accepted": False}, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
