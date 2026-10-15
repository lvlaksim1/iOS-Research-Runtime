#!/usr/bin/env python3
"""Non-deploying iPhoneOS IOKit collector ABI prerequisite probe.

A successful result proves only that an exact source compiles and links against
an identified local iPhoneOS SDK. It proves no guest execution or device binding.
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
from typing import Callable

MAX_SOURCE_BYTES = 256 * 1024
MACHO_ARM64_CPU = 0x0100000C
MACHO_EXECUTE = 2
LC_BUILD_VERSION = 0x32
LC_VERSION_MIN_MACOSX = 0x24
LC_VERSION_MIN_IPHONEOS = 0x25
LC_VERSION_MIN_TVOS = 0x2F
LC_VERSION_MIN_WATCHOS = 0x30
PLATFORM_IOS = 2
MAX_LOAD_COMMANDS = 4096
LEGACY_PLATFORMS = {LC_VERSION_MIN_MACOSX, LC_VERSION_MIN_IPHONEOS,
                    LC_VERSION_MIN_TVOS, LC_VERSION_MIN_WATCHOS}


class ProbeFailure(Exception):
    def __init__(self, stage: str, reason: str):
        self.stage, self.reason = stage, reason
        super().__init__(f"{stage}:{reason}")


def _run(cmd: list[str], *, stage: str) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=90, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProbeFailure(stage, type(exc).__name__) from exc
    if p.returncode:
        # Do not persist stderr: local paths and other environmental data may
        # be embedded. The stage/exit code are sufficient for first triage.
        raise ProbeFailure(stage, f"exit_{p.returncode}")
    return p.stdout.strip()


def _verify_macho(path: Path) -> None:
    """Require thin arm64 MH_EXECUTE with explicit iPhoneOS platform evidence.

    A Mach-O arm64 header alone is also valid for macOS. Parse bounded load
    commands and fail closed on missing, conflicting or truncated platform data.
    This verifies binary *metadata*, not SDK ABI, signature or guest execution.
    """
    if not path.is_file():
        raise ProbeFailure("MACHO_VERIFY", "linker_no_output")
    data = path.read_bytes()
    if len(data) < 32 or data[:4] != b"\xcf\xfa\xed\xfe":
        raise ProbeFailure("MACHO_VERIFY", "not_thin_macho64")
    cpu, _, kind, ncmds, sizeofcmds, _, _ = struct.unpack_from("<IIIIIII", data, 4)
    if cpu != MACHO_ARM64_CPU or kind != MACHO_EXECUTE:
        raise ProbeFailure("MACHO_VERIFY", "wrong_cpu_or_filetype")
    if ncmds == 0 or ncmds > MAX_LOAD_COMMANDS or sizeofcmds > len(data) - 32:
        raise ProbeFailure("MACHO_VERIFY", "invalid_load_commands")
    offset, end = 32, 32 + sizeofcmds
    build_platform, legacy_platform = None, None
    for _ in range(ncmds):
        if offset + 8 > end:
            raise ProbeFailure("MACHO_VERIFY", "invalid_load_commands")
        command, size = struct.unpack_from("<II", data, offset)
        if size < 8 or size % 8 or offset + size > end:
            raise ProbeFailure("MACHO_VERIFY", "invalid_load_commands")
        if command == LC_BUILD_VERSION:
            if size < 24:
                raise ProbeFailure("MACHO_VERIFY", "invalid_build_version")
            current = struct.unpack_from("<I", data, offset + 8)[0]
            if build_platform is not None and build_platform != current:
                raise ProbeFailure("MACHO_VERIFY", "conflicting_platforms")
            build_platform = current
        elif command in LEGACY_PLATFORMS:
            if size != 16:
                raise ProbeFailure("MACHO_VERIFY", "invalid_legacy_version")
            if legacy_platform is not None and legacy_platform != command:
                raise ProbeFailure("MACHO_VERIFY", "conflicting_platforms")
            legacy_platform = command
        offset += size
    if offset != end:
        raise ProbeFailure("MACHO_VERIFY", "invalid_load_commands")
    if build_platform is not None:
        if build_platform != PLATFORM_IOS or (legacy_platform is not None and
                                              legacy_platform != LC_VERSION_MIN_IPHONEOS):
            raise ProbeFailure("MACHO_VERIFY", "not_iphoneos_platform")
    elif legacy_platform != LC_VERSION_MIN_IPHONEOS:
        raise ProbeFailure("MACHO_VERIFY", "not_iphoneos_platform")


def probe(source: Path, *, host_system: str | None = None,
          which: Callable[[str], str | None] = shutil.which,
          run: Callable[..., str] = _run) -> dict:
    result = {
        "status": "NOT_PROVEN", "stage": "PREREQUISITE", "sdk": "iphoneos",
        "architecture": "arm64", "required_macho_platform": "iphoneos", "source_sha256": None,
        "sdk_identity_verified": False, "header_declarations_verified": False,
        "object_compiled": False, "iokit_linked": False,
        "guest_execution_proven": False, "driver_binding_proven": False,
        "full_system_boot_accepted": False,
    }
    try:
        if not source.is_file() or not (0 < source.stat().st_size <= MAX_SOURCE_BYTES):
            raise ProbeFailure("SOURCE", "missing_or_invalid_size")
        raw = source.read_bytes()
        result["source_sha256"] = hashlib.sha256(raw).hexdigest()
        if b"IORegistryEntryGetParentEntry" not in raw or b"IORegistryCreateIterator" not in raw:
            raise ProbeFailure("SOURCE", "not_expected_ioreg_collector")
        if (host_system or platform.system()) != "Darwin":
            raise ProbeFailure("SDK", "requires_macos")
        xcrun = which("xcrun")
        if not xcrun:
            raise ProbeFailure("SDK", "xcrun_missing")
        sdk = run([xcrun, "--sdk", "iphoneos", "--show-sdk-path"], stage="SDK")
        version = run([xcrun, "--sdk", "iphoneos", "--show-sdk-version"], stage="SDK")
        if not sdk or not Path(sdk).is_dir() or not version:
            raise ProbeFailure("SDK", "missing_sdk_path_or_version")
        compiler = run([xcrun, "--sdk", "iphoneos", "--find", "clang"], stage="SDK")
        if not compiler or not Path(compiler).is_file():
            raise ProbeFailure("SDK", "compiler_not_found")
        result["sdk_version"] = version
        result["sdk_identity_verified"] = True
        base = [xcrun, "--sdk", "iphoneos", "clang", "-target", "arm64-apple-ios",
                "-arch", "arm64", "-isysroot", sdk, "-Wall", "-Wextra", "-Werror"]
        run(base + ["-fsyntax-only", str(source)], stage="HEADER_DECLARATIONS")
        result["header_declarations_verified"] = True
        with tempfile.TemporaryDirectory(prefix="iosm3-abi-") as d:
            obj, binary = Path(d) / "probe.o", Path(d) / "probe"
            run(base + ["-c", str(source), "-o", str(obj)], stage="OBJECT_COMPILE")
            if not obj.is_file():
                raise ProbeFailure("OBJECT_COMPILE", "compiler_no_object")
            result["object_compiled"] = True
            run(base + [str(obj), "-framework", "IOKit", "-o", str(binary)],
                stage="IOKIT_LINK")
            _verify_macho(binary)
            result["iokit_linked"] = True
        result["status"] = "COMPILE_LINK_PREREQUISITE_ONLY"
        result["stage"] = "DONE"
    except ProbeFailure as exc:
        result["stage"] = exc.stage
        result["reason"] = exc.reason
    except OSError as exc:
        result["stage"] = "SOURCE_OR_SDK_IO"
        result["reason"] = type(exc).__name__
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    r = probe(args.source)
    print(json.dumps(r, sort_keys=True))
    return 0 if r["status"] == "COMPILE_LINK_PREREQUISITE_ONLY" else 2


if __name__ == "__main__":
    sys.exit(main())
