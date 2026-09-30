# Current blockers and open risks

Updated: 2026-09-30 22:30 MSK

## Product blocker
Exact-head E2E run `36729602541` on `bcde5661...` failed at the provisioning / Darwin root-shell proof step. Failure evidence was collected and uploaded. Next work is evidence extraction and the smallest bounded diagnostic/fix toward verified recovery root shell.

## Runtime blocker addressed by generation 17
Generation 16 package 005 could strand if the current Watchdog runtime ended before successfully creating its one-shot +5 minute successor. Final observed package005 state had Mailbox generation262 READY/ACK=NONE and A/B/Watchdog disabled.

Generation 17 removes this single continuity dependency by storing an hourly recurrence in the Watchdog task itself.

## Generation-17 residual risks
- Scheduled Task execution can be delayed; DTSTART is not an SLA.
- Hourly recurrence is a recovery backstop, not a guarantee of a five-minute recovery after a runtime dies before sliding.
- A stale already-running control-plane runtime still cannot be cancelled by CAS because Scheduled Tasks expose no compare-and-swap primitive.
- Fencing cannot cancel an external request already in flight.
- Mutation recovery is safe only while the frozen descriptor remains unchanged.
- If authoritative main is neither frozen baseline nor target, FAIL_STOP.
- A Worker that must restore an unexpectedly disabled Watchdog must preserve the immutable Watchdog prompt and recurring-backstop semantics.

## OCB
OCB remains explicit OSB only, maximum three exact-identical attempts, no fourth request.
No GitHub lock/fence is added by generation 17.
