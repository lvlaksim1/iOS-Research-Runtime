# PP-RM Launch Package — generation 17

Status: RUNNING
Manager generation: 17
Package: `IOS-M1-CONTINUOUS-006`
Product start: `main@bcde5661eab70b6811a5f1fffe0552edaedf980a`

## Owner authority
Direct Owner instruction: convert PP-RM to v17, update capsules, and launch the cycle.

## Continuity objects
A=`6abac75982308191b786450088217776`
B=`6abac76297c8819182c048fcbc619ef0`
Mailbox=`6abac714ddb481919ab9cb13afc4f8f8`
Watchdog=`6abac73339dc8191ba6bf26104fc2aa9`
Trace=`6abac750fee081918af4522336615f29`

## Product mutation
Generation16 native two-phase protocol is retained:
PREPARE may create immutable Git objects but never mutates product refs.
MUTATION_READY fresh executor publishes only the frozen target after authoritative reconciliation.
No second Scheduled Tasks read before update_ref.
No GitHub lock/fence ref.

## Watchdog v17
Watchdog schedule contains:
`RRULE:FREQ=HOURLY`
plus a near-term DTSTART.

Runtime prefix:
1. update self with `is_enabled=true` only; capture returned updated_at;
2. update same task to DTSTART=updated_at+5m with `RRULE:FREQ=HOURLY`;
3. read Scheduled Tasks and execute Watchdog state machine.

If sliding is lost, the already-persisted hourly recurrence remains the backstop.
Watchdog prompt stays immutable.

## Production launch evidence
Launch is complete and package006 is active:
- generation1 Worker B accepted and ACKed bootstrap READY
- generation1 reconciled E2E run `36729602541`, extracted signature/AMFI evidence and handed off
- generation2 Worker A accepted and ACKed the baton
- generation2 identified `rcodesign import_settings_from_macho` as the mechanism overriding explicit SHA256 selection and handed off
- latest observed baton: generation3 Worker B, READY, activation_attempt=1
- Watchdog is enabled with recurring hourly schedule
- no ambiguous product mutation is in flight

## Current mission
Generation3 designs the smallest bounded correction that keeps SHA256 as the primary post-sign CodeDirectory digest. Prefer an upstream-supported mechanism. Prepare a target only after direct post-sign evidence proves SHA256 primary, then publish through MUTATION_READY and run exact-SHA CI/E2E.

## OCB
Explicit OSB only; maximum 3 exact-identical attempts; no attempt4; ambiguous mutable result requires reconciliation.

## Supersession
Package `IOS-M1-CONTINUOUS-005` is superseded and MUST NOT be resumed.
