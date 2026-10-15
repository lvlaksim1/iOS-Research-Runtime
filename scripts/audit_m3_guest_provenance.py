#!/usr/bin/env python3
"""Read-only audit of the integration harness's guest proof provenance.

This tool reports whether existing *source code* gates Stage 1. It cannot
validate a boot, a device tree, IOService attachment, or a runtime trace.
"""
import argparse
import hashlib
import json
from pathlib import Path


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def inspect(program: str, workflow: str) -> dict:
    p = program
    w = workflow
    checks = {
        "root_shell_proof_callback": 'line.StartsWith("[proof] Диагностика завершена;"' in p,
        "root_shell_proof_awaited": "await proofCompleted.Task.WaitAsync" in p,
        "boot_progress_accepts_recovery_shell": 'line.StartsWith("bash-", StringComparison.Ordinal)' in p,
        "provider_probe_uses_shell_echo_markers": '"echo __IOS_M3_PROVIDER_PROBE_BEGIN__"' in p and '"echo __IOS_M3_PROVIDER_PROBE_END__"' in p,
        "provider_probe_completed_by_marker": '"__IOS_M3_PROVIDER_PROBE_END__"' in p and "providerProbeCompleted.TrySetResult()" in p,
        "provider_probe_timeout_nonfatal": "read-only provider probe did not reach its terminal marker; continuing existing proof path" in p,
        "guest_ioprint_digest_only_expected_echo": "echo __IOS_M3_IOPRINT_SHA256_EXPECTED_" in p,
        "guest_ioprint_class_text_probe": "/usr/local/bin/ioprint -p IOService 2>&1 | grep -E -i -C 6" in p,
        "host_ioprint_digest_filter": "SHA256.HashData(stream)" in p,
        "workflow_root_shell_named_step": "Run provisioning and Darwin root-shell proof" in w,
        "workflow_success_from_harness_exit": "End-to-end integration harness failed with exit code" in w,
    }
    positions = {
        "root_proof_wait": p.find("await proofCompleted.Task.WaitAsync"),
        "provider_probe_start": p.find("IOS-M3 read-only provider probe start"),
        "boot_proof_ok": p.find('Console.WriteLine("BOOT_PROOF_OK")'),
        "boundary_probe_wait": p.find("await boundaryProbeCompleted.Task.WaitAsync"),
    }
    ordered = all(x >= 0 for x in positions.values()) and (
        positions["root_proof_wait"] < positions["provider_probe_start"]
        < positions["boot_proof_ok"] < positions["boundary_probe_wait"]
    )
    checks["root_shell_then_boot_proof_before_storage_boundary_completion"] = ordered
    known = all(checks.values())
    return {
        "schema": "m3-guest-provenance-audit-v1",
        "source_contract_recognized": known,
        "checks": checks,
        "observed_order": positions,
        "interpretation": {
            "harness_success_proves_stage1": False,
            "guest_iokit_provider_binding_proven": False,
            "guest_nvme_device_proven": False,
            "non_ramdisk_disk_proven": False,
            "apfs_system_preboot_data_proven": False,
            "system_launchd_proven": False,
            "reason": "Root-shell completion and marker/class-text probes are not verified IOService attachment or system-volume evidence." if known else "Source contract changed or incomplete; audit fails closed.",
        },
        "required_next_evidence": "Capture actual guest IOService parent/child registry entries with instance identity and PCIe/NVMe provider attachment; separately verify non-ramdisk /dev/disk, APFS volume roles and system launchd. Do not infer from echoed markers.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--program-blob", required=True)
    parser.add_argument("--workflow-blob", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    program = args.program.read_bytes()
    workflow = args.workflow.read_bytes()
    actual = {"program": git_blob_sha(program), "workflow": git_blob_sha(workflow)}
    expected = {"program": args.program_blob, "workflow": args.workflow_blob}
    matching = actual == expected
    result = inspect(program.decode("utf-8"), workflow.decode("utf-8")) if matching else {
        "schema": "m3-guest-provenance-audit-v1", "source_contract_recognized": False,
        "interpretation": {"harness_success_proves_stage1": False, "reason": "Source blob mismatch: audit fails closed."},
    }
    result["source_blobs"] = actual
    result["expected_source_blobs"] = expected
    result["source_blobs_match"] = matching
    result["audit_status"] = "SOURCE_ONLY_RECOGNIZED_NOT_STAGE1" if matching and result["source_contract_recognized"] else "SOURCE_INVALID_OR_CHANGED"
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["audit_status"] == "SOURCE_ONLY_RECOGNIZED_NOT_STAGE1" else 2


if __name__ == "__main__":
    raise SystemExit(main())
