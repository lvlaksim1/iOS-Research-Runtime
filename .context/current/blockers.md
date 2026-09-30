# Current blockers and open risks

Updated: 2026-09-30 23:39 MSK

## Product blocker
Verified recovery root shell is still not proven.

The strict rcodesign Windows gate on exact current main `4821fb9a9cd72dd40af2a518962f180fb4344fe7` completed SUCCESS as run `36771957949`. The immediate product task is to extract the actual primary-SHA256 evidence from that successful run/log/artifact and then continue the smallest exact-SHA E2E path.

## Runtime logic defect corrected by generation18
Package006 terminalized on missing `workflow_dispatch` capability even though the required exact-main workflow result already existed.

Generation18 corrects this by making workflow gates result-first and trigger-agnostic:
- existing qualifying exact-SHA SUCCESS satisfies the gate regardless of trigger event;
- existing queued/in-progress run is observed rather than duplicated;
- rerun-existing-run may be used when appropriate and authorized;
- new dispatch is attempted only when no usable exact-SHA run exists;
- OWNER_GATE for unavailable dispatch is valid only when a new run is actually necessary.

## Continuity residual risks
- Scheduled Task delivery can be delayed; DTSTART is not an SLA.
- Hourly recurrence is a recovery floor, not a five-minute guarantee.
- Scheduled Tasks expose no compare-and-swap primitive; already-running stale control-plane work cannot be cancelled.
- Frozen mutation descriptor must remain unchanged across recovery.
- If authoritative main is neither frozen baseline nor target, FAIL_STOP.

## OCB
Explicit OSB only; maximum three exact-identical attempts total; no fourth attempt.
Ambiguous mutable request requires authoritative reconciliation before replay.
