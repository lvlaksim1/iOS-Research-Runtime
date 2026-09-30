# Current blockers and open risks

Updated: 2026-09-30 23:51 MSK

## Product blocker
Verified recovery root shell remains unproven.

The immediate blocker is now the correctness of the rcodesign gate itself. Result-first reconciliation has shown that two successive gate implementations falsely accepted signatures whose actual primary CodeDirectory digest is SHA1 with SHA256 only in an alternate slot.

Generation4 owns a frozen parser-only correction `79393c0d...` that handles the quoted alternate-slot form emitted by rcodesign. No signer mutation is allowed until the gate truthfully distinguishes SHA256-primary from SHA1-primary+SHA256-alternate.

## Runtime status
PP-RM package007 is RUNNING. Current baton is generation4 / Worker A / MUTATION_READY.
Watchdog remains enabled with the generation17 recurring hourly backstop.

## Residual risks
- Scheduled Task delivery can be delayed; DTSTART is not an SLA.
- Hourly recurrence is a recovery floor, not a five-minute guarantee.
- Scheduled Tasks expose no CAS; already-running stale control-plane work cannot be cancelled.
- Frozen mutation descriptor must remain unchanged across recovery.
- If authoritative main is neither frozen baseline nor target, FAIL_STOP.
- Workflow SUCCESS alone is not sufficient evidence when the workflow assertion itself is defective; logs/artifacts must be reconciled against the actual acceptance condition.

## OCB
Explicit OSB only; maximum three exact-identical attempts; no fourth.
Ambiguous mutable result requires authoritative reconciliation before replay.
