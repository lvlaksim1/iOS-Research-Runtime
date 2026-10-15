#!/usr/bin/env python3
"""Offline, fail-closed static audit of a pinned QEMU trace build prerequisite.

This does not inspect a compiled QEMU executable, run a guest, or certify MSI-X.
Inputs must be externally pinned and byte-verified before interpreting results.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EVENTS = ("pci_nvme_irq_msix", "pci_nvme_irq_pin", "pci_nvme_irq_masked")


def analyze(workflow: str, options: str, meson: str, nvme_events: str) -> dict:
    default = re.search(
        r"option\(\s*['\"]trace_backends['\"]\s*,\s*type:\s*['\"]array['\"]\s*,\s*value:\s*\[\s*['\"]log['\"]\s*\]",
        options, re.S,
    ) is not None
    wired = bool(re.search(r"CONFIG_TRACE_['\"]?\s*\+\s*k\.to_upper\(\)", meson)) and bool(
        re.search(r"get_option\(['\"]trace_backends['\"]\)", meson)
    )
    event_names = {name: bool(re.search(r"(?m)^" + re.escape(name) + r"\s*\(", nvme_events)) for name in EVENTS}
    # A cached build.ninja bypasses configure in the pinned Windows workflow.
    cached_configure_skip = bool(re.search(r"if\s+\[\s*!\s+-f\s+build\.ninja\s*\]", workflow))
    restores_cache = "actions/cache/restore@" in workflow
    restore_prefix = "restore-keys:" in workflow
    # Explicit backend configuration is distinct from the Meson default.
    explicit_backend = bool(re.search(r"(?:--trace-backends|trace_backends\s*=|-Dtrace_backends)", workflow))
    runtime_probe = bool(re.search(r"qemu-system-aarch64(?:\.exe)?[^\n]*-trace\s+help", workflow))
    runtime_trace_invocation = bool(re.search(r"qemu-system-aarch64(?:\.exe)?[^\n]*-trace\s+events=", workflow))
    reasons = []
    if not default: reasons.append("PINNED_MESON_DEFAULT_LOG_NOT_CONFIRMED")
    if not wired: reasons.append("PINNED_MESON_TRACE_CONFIG_WIRING_NOT_CONFIRMED")
    if not all(event_names.values()): reasons.append("NVME_IRQ_EVENTS_NOT_ALL_DECLARED")
    if cached_configure_skip and restores_cache:
        reasons.append("CACHED_BUILD_NINJA_CAN_BYPASS_RECONFIGURE")
    if restore_prefix: reasons.append("CACHE_PREFIX_RESTORE_CAN_REUSE_PRIOR_CONFIGURATION")
    if not runtime_probe: reasons.append("NO_WINDOWS_BINARY_TRACE_HELP_PROBE")
    if not runtime_trace_invocation: reasons.append("NO_WINDOWS_BINARY_TRACE_EVENTS_PROBE")
    return {
        "audit_schema": "ios-m3-qemu-trace-static-v1",
        "pinned_meson_default_log": default,
        "meson_trace_backend_wiring": wired,
        "nvme_irq_event_declarations": event_names,
        "workflow_explicit_backend_selection": explicit_backend,
        "workflow_cache_restore": restores_cache,
        "workflow_prefix_restore": restore_prefix,
        "workflow_cached_ninja_skips_configure": cached_configure_skip,
        "workflow_runtime_trace_help_probe": runtime_probe,
        "workflow_runtime_trace_events_probe": runtime_trace_invocation,
        "unresolved": reasons,
        "compiled_windows_trace_backend": "UNKNOWN",
        "actual_qemu_irq_events": "NOT_OBSERVED",
        "full_ios_system_boot": "NOT_PROVEN",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("workflow", "meson-options", "meson-build", "nvme-events"):
        parser.add_argument("--" + key, type=Path, required=True)
    args = parser.parse_args(argv)
    result = analyze(args.workflow.read_text(encoding="utf-8"),
                     args.meson_options.read_text(encoding="utf-8"),
                     args.meson_build.read_text(encoding="utf-8"),
                     args.nvme_events.read_text(encoding="utf-8"))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if (result["pinned_meson_default_log"] and
                 result["meson_trace_backend_wiring"] and
                 all(result["nvme_irq_event_declarations"].values())) else 2


if __name__ == "__main__":
    raise SystemExit(main())
