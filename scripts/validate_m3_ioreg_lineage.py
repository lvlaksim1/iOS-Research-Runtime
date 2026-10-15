#!/usr/bin/env python3
"""Validate bounded IOService-plane parent-ID evidence, without claiming guest boot.

The input is JSONL from scripts/ios_m3_ioreg_lineage.c (GEN35). This checks
internal structure and an explicitly requested ancestor chain. It does NOT
authenticate that the input came from a guest or prove IOKit driver matching,
NVMe, APFS, or full iOS boot. Never infer an ancestor from class/name/order.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ID = re.compile(r"0x[0-9a-f]{16}\Z")
MAX_BYTES = 4 * 1024 * 1024
MAX_ENTRIES = 4096


class EvidenceError(ValueError):
    pass


def _unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise EvidenceError("duplicate_json_key:" + key)
        out[key] = value
    return out


def _identifier(value):
    return isinstance(value, str) and ID.fullmatch(value) is not None


def inspect(raw: bytes, child_id: str, ancestor_id: str) -> dict:
    digest = hashlib.sha256(raw).hexdigest()
    base = {"input_sha256": digest, "status": "UNPROVEN", "full_system_boot_accepted": False,
            "guest_origin_authenticated": False, "driver_binding_proven": False}
    try:
        if not raw or len(raw) > MAX_BYTES:
            raise EvidenceError("empty_or_oversized_input")
        if not _identifier(child_id) or not _identifier(ancestor_id) or child_id == ancestor_id:
            raise EvidenceError("invalid_or_identical_requested_ids")
        if not raw.endswith(b"\n"):
            raise EvidenceError("missing_terminal_newline")
        lines = raw.decode("utf-8", errors="strict").splitlines()
        if not lines or len(lines) > MAX_ENTRIES + 2:
            raise EvidenceError("invalid_record_count")
        entries = {}
        summary = None
        errors = 0
        for index, line in enumerate(lines):
            if not line or len(line) > 8192:
                raise EvidenceError("invalid_line")
            obj = json.loads(line, object_pairs_hook=_unique_pairs)
            if not isinstance(obj, dict):
                raise EvidenceError("non_object_record")
            kind = obj.get("kind")
            if kind == "entry":
                if summary is not None:
                    raise EvidenceError("entry_after_summary")
                if set(obj) != {"kind", "plane", "id", "parent_id", "parent_status", "class", "name"}:
                    raise EvidenceError("invalid_entry_fields")
                eid, pid, ps = obj["id"], obj["parent_id"], obj["parent_status"]
                if obj["plane"] != "IOService" or not _identifier(eid):
                    raise EvidenceError("invalid_entry_identity")
                if eid in entries:
                    raise EvidenceError("duplicate_registry_id")
                if type(ps) is not int or (pid is not None and not _identifier(pid)):
                    raise EvidenceError("invalid_parent_fields")
                if (ps == 0) != (pid is not None) or eid == pid:
                    raise EvidenceError("inconsistent_parent_status")
                if not isinstance(obj["class"], str) or not isinstance(obj["name"], str):
                    raise EvidenceError("invalid_class_or_name")
                entries[eid] = obj
            elif kind == "entry_error":
                if summary is not None:
                    raise EvidenceError("error_after_summary")
                errors += 1
            elif kind == "summary":
                if summary is not None or index != len(lines) - 1:
                    raise EvidenceError("summary_not_last_or_duplicate")
                summary = obj
            else:
                raise EvidenceError("unexpected_record_kind")
        if summary is None or set(summary) != {"kind", "plane", "entries", "errors", "truncated", "full_system_boot_accepted"}:
            raise EvidenceError("missing_or_invalid_summary")
        if summary["plane"] != "IOService" or type(summary["entries"]) is not int or type(summary["errors"]) is not int:
            raise EvidenceError("invalid_summary_types")
        if type(summary["truncated"]) is not bool or summary["full_system_boot_accepted"] is not False:
            raise EvidenceError("invalid_summary_flags")
        if summary["truncated"] or summary["entries"] != len(entries) + errors or summary["errors"] != errors or errors:
            raise EvidenceError("incomplete_or_inconsistent_capture")
        if len(entries) > MAX_ENTRIES:
            raise EvidenceError("entry_cap_exceeded")
        if child_id not in entries or ancestor_id not in entries:
            raise EvidenceError("requested_id_not_observed")
        path = [child_id]
        seen = {child_id}
        while path[-1] != ancestor_id:
            current = entries[path[-1]]
            if current["parent_status"] != 0:
                raise EvidenceError("parent_lookup_not_successful")
            parent = current["parent_id"]
            if parent not in entries:
                raise EvidenceError("parent_not_in_capture")
            if parent in seen:
                raise EvidenceError("parent_cycle")
            seen.add(parent)
            path.append(parent)
        return {**base, "status": "STRUCTURALLY_CONSISTENT_CHAIN_ONLY", "chain_ids_child_to_ancestor": path,
                "entries_observed": len(entries), "limitations": [
                    "JSONL can be synthetic or altered; origin is not authenticated",
                    "Parent IDs establish only a reported IOService-plane relation",
                    "Class names and parent chain do not prove driver binding or full boot"]}
    except (EvidenceError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {**base, "reason": str(exc)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("jsonl", type=Path)
    p.add_argument("--child-id", required=True)
    p.add_argument("--ancestor-id", required=True)
    args = p.parse_args()
    try:
        raw = args.jsonl.read_bytes()
    except OSError as exc:
        print(json.dumps({"status": "UNPROVEN", "reason": "read_error:" + str(exc),
                          "full_system_boot_accepted": False}))
        return 2
    result = inspect(raw, args.child_id, args.ancestor_id)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "STRUCTURALLY_CONSISTENT_CHAIN_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
