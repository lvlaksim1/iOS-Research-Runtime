# Current blockers and open risks

Updated: 2026-09-30 04:05 MSK

## Product blocker
Exact-SHA E2E still fails before verified recovery root shell.
Current investigation is narrowed to post-merge recovery `/bin/bash` signature/CDHash/trust-membership provenance.

## Runtime blocker resolved by generation 16
Generation 15 package 004 failed because the worker protocol required a second Scheduled Tasks read immediately before mutable GitHub publication.
That read was not reliably available in Scheduled Runtime, causing repeated evidence-only turns and eventual `CONFIRMED_RUNTIME_STALLS_EXHAUSTED`.

Generation 16 removes that normal-path dependency by separating PREPARE from MUTATION execution.

## Generation-16 residual risks
- Scheduled Task delivery itself remains non-real-time and is not absolutely guaranteed.
- A runtime can still fail before its first tool operation.
- Native Scheduled Task register updates do not provide a compare-and-swap primitive; stale control-plane writes remain a residual risk and must be rejected by package/generation/token/owner validation on fresh runtimes.
- Fencing cannot cancel an external request already in flight.
- Mutation recovery is safe only while mutation_id, baseline and target remain frozen.
- If authoritative main is neither frozen baseline nor frozen target, PP-RM must FAIL_STOP.
- Watchdog cadence remains fixed requested +5 minutes and intentionally non-adaptive.

## OCB
OCB remains explicit OSB only, maximum three exact-identical attempts, no fourth request.
No additional GitHub lock/fence request is introduced by generation 16.
