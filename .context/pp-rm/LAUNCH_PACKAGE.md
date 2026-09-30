# PP-RM Launch Package — generation 17

Status: OWNER-AUTHORIZED — CONFIGURE AND ARM
Manager generation: 17
Package: `IOS-M1-CONTINUOUS-006`
Product start: `main@bcde5661eab70b6811a5f1fffe0552edaedf980a`

## Owner authority
Direct Owner instruction: convert PP-RM to v17, update capsules, and launch the cycle.

## Mission
Continue IOS-M1 from authoritative main.
First bounded unit: reconcile completed exact-head E2E run `36729602541`; inspect collected failure evidence; extract post-merge bash SignatureInfo plus AMFI/root-shell evidence versus pre-SHA256 baseline; then choose one smallest bounded diagnostic/fix and exact-SHA CI.

## Continuity objects
A=`6abac75982308191b786450088217776`
B=`6abac76297c8819182c048fcbc619ef0`
Mailbox=`6abac714ddb481919ab9cb13afc4f8f8`
Watchdog=`6abac73339dc8191ba6bf26104fc2aa9`
Trace=`6abac750fee081918af4522336615f29`

## Product mutation
Generation-16 native two-phase protocol is retained:
PREPARE may create immutable Git objects but never mutates product refs.
MUTATION_READY fresh executor publishes only the frozen target after authoritative reconciliation.
No second Scheduled Tasks read before update_ref.
No GitHub lock/fence ref.

## Watchdog v17
Watchdog schedule always contains:
`RRULE:FREQ=HOURLY`
plus a near-term DTSTART.

Runtime prefix:
1. update self with `is_enabled=true` only; capture returned updated_at;
2. update same task to DTSTART=updated_at+5m with `RRULE:FREQ=HOURLY`;
3. read Scheduled Tasks and execute Watchdog state machine.

If step 1 or 2 is lost, the previously stored hourly recurrence remains the backstop.
Watchdog prompt stays immutable.

## OCB
Explicit OSB only; maximum 3 exact-identical attempts; no attempt4; ambiguous mutable result requires reconciliation.

## Launch ordering
1. Configure A/B/Watchdog prompts for generation17/package006 while disabled.
2. Seed Mailbox and Trace disabled.
3. Arm Watchdog as recurring near +5m with hourly RRULE.
4. Final launch operation: arm initial Worker B about +30s.
