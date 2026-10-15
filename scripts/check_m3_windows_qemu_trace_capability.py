#!/usr/bin/env python3
"""Fail-closed, binary-specific QEMU trace catalog gate; never boots a guest.

Run against the *built* Windows QEMU executable in its Meson build directory.
Passing this gate establishes catalog/configuration capability only, not IRQ
emission, PCIe provider binding, NVMe discovery, APFS, or iOS system boot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

EVENTS = ("pci_nvme_irq_msix", "pci_nvme_irq_pin", "pci_nvme_irq_masked")
MAX_CAPTURE_BYTES = 262144


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_backend_config(build_root: Path) -> tuple[bool, bool, list[str]]:
    """Require both Meson introspection and the generated host header."""
    reasons: list[str] = []
    options_path = build_root / "meson-info" / "intro-buildoptions.json"
    header_path = build_root / "config-host.h"
    try:
        options = json.loads(options_path.read_text(encoding="utf-8"))
        if not isinstance(options, list):
            raise ValueError("build options must be an array")
        matches = [x for x in options if isinstance(x, dict)
                   and x.get("name") == "trace_backends"]
        value = matches[0].get("value") if len(matches) == 1 else None
        meson_log = (isinstance(value, list) and "log" in value
                     and all(isinstance(x, str) for x in value))
        if not meson_log:
            reasons.append("MESON_LOG_BACKEND_NOT_VERIFIED")
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        meson_log = False
        reasons.append("MESON_BUILD_OPTIONS_UNREADABLE")
    try:
        header = header_path.read_text(encoding="utf-8")
        host_log = bool(re.search(r"(?m)^\s*#define\s+CONFIG_TRACE_LOG\s+1\s*$", header))
        if not host_log:
            reasons.append("CONFIG_TRACE_LOG_NOT_DEFINED")
    except (OSError, UnicodeError):
        host_log = False
        reasons.append("CONFIG_HOST_HEADER_UNREADABLE")
    return bool(meson_log), host_log, reasons


def parse_trace_catalog(output: str) -> dict[str, bool]:
    # Pinned QEMU trace/control.c prints one registered name per line.
    names = {line.strip() for line in output.splitlines()
             if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", line.strip())}
    return {name: name in names for name in EVENTS}


def parse_darwin_machine(output: str) -> bool:
    return re.search(r"(?m)^\s*darwin(?:\s|$)", output) is not None


def run_gate(build_root: Path, binary: Path, expected_sha256: str | None = None,
             runner: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> dict:
    reasons: list[str] = []
    build_root = build_root.resolve()
    binary = binary.resolve()
    result: dict = {
        "schema": "ios-m3-windows-qemu-trace-capability-v1",
        "binary_path": str(binary),
        "binary_sha256": None,
        "binary_sha256_matches_expected": None,
        "meson_log_backend": False,
        "config_host_log_backend": False,
        "darwin_machine_in_binary": False,
        "registered_nvme_irq_trace_events": {name: False for name in EVENTS},
        "catalog_capability": "NOT_VERIFIED",
        "runtime_irq_emission": "NOT_OBSERVED",
        "guest_nvme_disk": "NOT_OBSERVED",
        "full_ios_system_boot": "NOT_PROVEN",
        "reasons": reasons,
    }
    if binary.parent != build_root or not binary.is_file():
        reasons.append("BINARY_NOT_IN_BUILD_ROOT")
        return result
    try:
        digest = sha256_file(binary)
        result["binary_sha256"] = digest
    except OSError:
        reasons.append("BINARY_UNREADABLE")
        return result
    if expected_sha256 is not None:
        expected = expected_sha256.lower()
        matches = bool(re.fullmatch(r"[0-9a-f]{64}", expected)) and digest == expected
        result["binary_sha256_matches_expected"] = matches
        if not matches:
            reasons.append("BINARY_SHA256_MISMATCH")
    meson, header, backend_reasons = read_backend_config(build_root)
    result["meson_log_backend"] = meson
    result["config_host_log_backend"] = header
    reasons.extend(backend_reasons)
    for argv, key in (([str(binary), "-trace", "help"], "trace"),
                      ([str(binary), "-M", "help"], "machine")):
        try:
            proc = runner(argv, capture_output=True, timeout=20, check=False)
            out = proc.stdout or b""
            err = proc.stderr or b""
            if isinstance(out, str):
                out = out.encode("utf-8", "replace")
            if isinstance(err, str):
                err = err.encode("utf-8", "replace")
            if proc.returncode != 0:
                reasons.append(f"{key.upper()}_COMMAND_EXIT_{proc.returncode}")
                continue
            if len(out) + len(err) > MAX_CAPTURE_BYTES:
                reasons.append(f"{key.upper()}_OUTPUT_TOO_LARGE")
                continue
            decoded = (out + b"\n" + err).decode("utf-8", "replace")
            if key == "trace":
                result["registered_nvme_irq_trace_events"] = parse_trace_catalog(decoded)
                if not all(result["registered_nvme_irq_trace_events"].values()):
                    reasons.append("NVME_IRQ_TRACE_EVENTS_MISSING")
            else:
                result["darwin_machine_in_binary"] = parse_darwin_machine(decoded)
                if not result["darwin_machine_in_binary"]:
                    reasons.append("DARWIN_MACHINE_NOT_LISTED")
        except (OSError, subprocess.TimeoutExpired) as exc:
            reasons.append(f"{key.upper()}_COMMAND_UNAVAILABLE_{type(exc).__name__}")
    if not reasons:
        result["catalog_capability"] = "VERIFIED_FOR_THIS_BINARY_SHA256"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-root", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--expected-binary-sha256", default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    report = run_gate(args.build_root, args.binary, args.expected_binary_sha256)
    serialized = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized)
    return 0 if report["catalog_capability"] == "VERIFIED_FOR_THIS_BINARY_SHA256" else 2


if __name__ == "__main__":
    raise SystemExit(main())
