#!/usr/bin/env python3
"""Fail-closed static contract for the pinned M3 NVMe MSI-X/INTx prerequisite.

This tool does not claim that the guest has bound an IOKit provider, that an
interrupt was delivered, or that an Apple AIC MSI address/ABI is known.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Mapping

PINNED_QEMU_COMMIT = "2867d847d3471560e773120ee50c42dbcbb6d60b"
PINNED_BLOBS = {
    "hw/arm/darwin.c": "51d240b112907e9bd2ef4d9be836a1a04a865db5",
    "hw/nvme/ctrl.c": "4893cf7e7418d3cf8a5a27d7e458d700c6fcc7b8",
    "hw/pci/msix.c": "1b23eaf10079f9f7501aae25f7826020c49d2e25",
    "hw/pci/msi.c": "b9f5b45920b66f33e34a8e85cb560536abe0d416",
    "hw/pci/pci.c": "d3191609e283eb456c65473eb2ee1bc7c90222b1",
}

class ContractError(ValueError):
    """A source prerequisite changed or cannot be established."""


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _skip_lexeme(src: str, i: int) -> int:
    """Advance past a C comment or string/character literal if one begins here."""
    if src.startswith("//", i):
        j = src.find("\n", i + 2)
        return len(src) if j == -1 else j
    if src.startswith("/*", i):
        j = src.find("*/", i + 2)
        if j == -1:
            raise ContractError("unterminated C comment")
        return j + 2
    if src[i] in ('"', "'"):
        quote = src[i]
        j = i + 1
        while j < len(src):
            if src[j] == "\\":
                j += 2
            elif src[j] == quote:
                return j + 1
            else:
                j += 1
        raise ContractError("unterminated C string")
    return i


def _matching(src: str, start: int, left: str, right: str) -> int:
    depth = 0
    i = start
    while i < len(src):
        j = _skip_lexeme(src, i)
        if j != i:
            i = j
            continue
        if src[i] == left:
            depth += 1
        elif src[i] == right:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ContractError("unbalanced C delimiters")


def c_function(src: str, name: str) -> str:
    """Extract one ordinary C function body; reject ambiguous/missing bodies."""
    candidates = []
    for match in re.finditer(r"\b" + re.escape(name) + r"\s*\(", src):
        open_paren = src.find("(", match.start())
        close_paren = _matching(src, open_paren, "(", ")")
        i = close_paren + 1
        while i < len(src) and src[i].isspace():
            i += 1
        if i >= len(src) or src[i] != "{":
            continue
        end = _matching(src, i, "{", "}")
        candidates.append(src[i:end + 1])
    if len(candidates) != 1:
        raise ContractError(f"function {name}: expected one definition, found {len(candidates)}")
    return candidates[0]


def require(body: str, pattern: str, label: str) -> None:
    if not re.search(pattern, body, re.DOTALL):
        raise ContractError("missing source contract: " + label)


def audit_texts(texts: Mapping[str, str]) -> dict:
    missing = sorted(set(PINNED_BLOBS) - set(texts))
    if missing:
        raise ContractError("missing source inputs: " + ", ".join(missing))

    ctrl = texts["hw/nvme/ctrl.c"]
    msix = texts["hw/pci/msix.c"]
    msi = texts["hw/pci/msi.c"]
    pci = texts["hw/pci/pci.c"]
    darwin = texts["hw/arm/darwin.c"]

    nvme_init = c_function(ctrl, "nvme_init_pci")
    require(nvme_init, r"\bmsix_init\s*\(", "NVMe initializes MSI-X")
    require(nvme_init, r"\bmsix_init_exclusive_bar\s*\(", "NVMe exclusive BAR MSI-X")
    require(nvme_init, r"if\s*\(\s*ret\s*==\s*-ENOTSUP\s*\)\s*\{[^{}]*warn_report_err\s*\(\s*\*errp\s*\)\s*;[^{}]*\*errp\s*=\s*NULL\s*;",
            "NVMe continues with warning after MSI-X ENOTSUP")
    require(nvme_init, r"else\s+if\s*\(\s*ret\s*<\s*0\s*\)\s*\{[^{}]*return\s+false\s*;",
            "NVMe propagates non-ENOTSUP MSI-X error")

    irq = c_function(ctrl, "nvme_irq_assert")
    require(irq, r"if\s*\(\s*msix_enabled\s*\(\s*pci\s*\)\s*\)\s*\{[^{}]*msix_notify\s*\(",
            "NVMe MSI-X IRQ branch")
    require(irq, r"else\s*\{[^{}]*nvme_irq_check\s*\(", "NVMe INTx fallback IRQ branch")

    init = c_function(msix, "msix_init")
    require(init, r"if\s*\(\s*!\s*msi_nonbroken\s*\)\s*\{[^{}]*return\s+-ENOTSUP\s*;",
            "MSI-X initialization guard")
    exclusive = c_function(msix, "msix_init_exclusive_bar")
    require(exclusive, r"\bmsix_init\s*\(", "exclusive MSI-X BAR delegates to guard")
    notify = c_function(msix, "msix_notify")
    require(notify, r"\bmsi_send_message\s*\(", "MSI-X message dispatch")

    send = c_function(msi, "msi_send_message")
    require(send, r"dev\s*->\s*msi_trigger\s*\(\s*dev\s*,\s*msg\s*\)", "MSI trigger callback")
    trigger = c_function(pci, "pci_msi_trigger")
    require(trigger, r"address_space_stl_le\s*\(\s*&\s*dev\s*->\s*bus_master_as\s*,\s*msg\.address\s*,\s*msg\.data",
            "MSI writes guest-programmed address via PCI bus-master address space")

    aic = c_function(darwin, "init_aic")
    require(aic, r"alloc_zeroed\s*\(\s*\"aic\"", "Darwin AIC register placeholder")
    if re.search(r"\b(?:qemu_set_irq|sysbus_connect_irq|msi_nonbroken)\s*\(?", aic):
        raise ContractError("AIC initializer has changed: inspect interrupt delivery again")
    if re.search(r"\bmsi_nonbroken\s*=", darwin):
        raise ContractError("Darwin MSI capability assignment changed: inspect exact semantics")

    return {
        "proof_level": "STATIC_SOURCE_CONTRACT_ONLY",
        "pinned_qemu_commit": PINNED_QEMU_COMMIT,
        "contract": {
            "msix_init_requires_msi_nonbroken": True,
            "nvme_enotsup_continues_without_msix": True,
            "nvme_interrupt_branches": ["MSIX", "INTx"],
            "msix_dispatch_chain": ["nvme_irq_assert", "msix_notify", "msi_send_message", "pci_msi_trigger", "address_space_stl_le"],
            "darwin_aic_initializer": "zeroed_register_placeholder_no_delivery_observed_in_function",
            "darwin_file_msi_nonbroken_assignment": "NOT_FOUND_IN_INSPECTED_FILE",
        },
        "runtime_msi_nonbroken": "UNKNOWN",
        "guest_msix_enabled": "UNKNOWN",
        "guest_interrupt_delivered": "NOT_PROVEN",
        "guest_nvme_bound": "NOT_PROVEN",
        "required_next_evidence": "built-QEMU runtime MSI-X capability/ENOTSUP and guest provider/IRQ route before any AIC mapping change",
    }


def audit_directory(root: Path) -> dict:
    texts = {}
    hashes = {}
    for rel, expected in PINNED_BLOBS.items():
        path = root / rel
        if not path.is_file():
            raise ContractError("source file missing: " + rel)
        raw = path.read_bytes()
        actual = git_blob_sha(raw)
        if actual != expected:
            raise ContractError(f"Git blob mismatch {rel}: expected {expected}, got {actual}")
        texts[rel] = raw.decode("utf-8")
        hashes[rel] = actual
    report = audit_texts(texts)
    report["verified_git_blobs"] = hashes
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu-root", type=Path, required=True, help="Exact pinned QEMU checkout; no network calls")
    args = parser.parse_args()
    try:
        result = audit_directory(args.qemu_root)
    except (ContractError, UnicodeDecodeError, OSError) as exc:
        print(json.dumps({"status": "BLOCKED_SOURCE_CONTRACT", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "PASS_STATIC_ONLY", **result}, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
