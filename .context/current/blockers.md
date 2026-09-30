# Current blockers and open risks

Updated: 2026-09-30 22:43 MSK

## Product blocker
The current blocker is no longer merely “SHA256 diagnostic pending”. Package006 generation2 identified why the intended SHA256-primary diagnostic did not materialize.

Observed behavior:
- repo signer requests `--digest sha256`
- `rcodesign` later calls `SigningSettings::import_settings_from_macho`
- that import step can force SHA1 primary and add SHA256 as an alternate for absent/old target metadata
- the resulting post-merge `/bin/bash` therefore still has SHA1 primary
- AMFI/CT rejection persists and root shell is not verified

Next blocker-resolution unit: determine the smallest supported override/correction that preserves explicit SHA256 as primary after signing, prove it on post-sign metadata, then run exact-SHA CI/E2E.

## Runtime blocker addressed by generation 17
Package005 stranded when its one-shot Watchdog had no persisted successor. Generation17 stores an hourly recurrence in the Watchdog task itself, so a runtime failure before successful sliding no longer deletes all future Watchdog opportunities.

## Generation-17 residual risks
- Scheduled Task execution can be delayed; DTSTART is not an SLA.
- Hourly recurrence is a recovery backstop, not a guarantee of five-minute recovery after a pre-slide Watchdog failure.
- Scheduled Tasks provide no compare-and-swap primitive; stale already-running control-plane work remains a residual risk.
- Fencing cannot cancel an external request already in flight.
- Mutation recovery is safe only while the frozen descriptor remains unchanged.
- If authoritative main is neither frozen baseline nor frozen target, FAIL_STOP.
- Workers restoring an unexpectedly disabled Watchdog must preserve the immutable prompt and recurring-backstop semantics.

## OCB
OCB remains explicit OSB only, maximum three exact-identical attempts, no fourth request.
No GitHub lock/fence is added by generation17.
