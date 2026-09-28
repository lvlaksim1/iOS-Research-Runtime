# Current blockers and open risks

## Immediate technical blocker
Current Windows E2E cannot start Darwin execution because `qemu-sptm-windows-gate` artifact is missing.

This is a work item inside `IOS-M1-CONTINUOUS-001`, not a Manager stop condition.

## Operational risks
- OCB is non-deterministic; use the unchanged three-attempt maximum only for consecutive explicit OSB.
- Mutation ambiguity requires authoritative state reconciliation.
- Register visibility may lag; stabilize with read-only rereads rather than mutation replay.
- Existing Mailbox/Pulse are stale from experiments; reseed before arm.
- Scheduled Task latency is variable; do not infer runtime death from timing alone.
- A/B must remain bounded per turn even though the package itself is continuous.

## Genuine stop conditions
- IOS-M1 objective achieved;
- required action exceeds Manager mandate or needs Owner approval;
- unresolved ambiguous side effect;
- PP-RM invariant failure that cannot be safely repaired from evidence;
- strategic fork requiring milestone/architecture/security-policy change rather than a tactical fix.
