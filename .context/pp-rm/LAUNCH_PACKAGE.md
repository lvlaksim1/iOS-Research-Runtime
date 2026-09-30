# PP-RM Launch Package — generation 18

Status: OWNER-AUTHORIZED — CONFIGURE AND ARM
Manager generation: 18
Package: `IOS-M1-CONTINUOUS-007`
Product start: `main@4821fb9a9cd72dd40af2a518962f180fb4344fe7`

## Owner authority
Direct Owner instruction: correct the workflow-gate logic and continue PP-RM.

## Continuity objects
A=`6abac75982308191b786450088217776`
B=`6abac76297c8819182c048fcbc619ef0`
Mailbox=`6abac714ddb481919ab9cb13afc4f8f8`
Watchdog=`6abac73339dc8191ba6bf26104fc2aa9`
Trace=`6abac750fee081918af4522336615f29`

## Preserved product mutation
Generation16 native two-phase protocol remains:
PREPARE may create immutable Git objects but never mutates product refs.
Fresh MUTATION_READY executor publishes only the frozen target after authoritative reconciliation.
No second Scheduled Tasks read before update_ref.
No GitHub continuity fence/ref.

## Preserved Watchdog
Generation17 recurring-backstop semantics remain:
- Watchdog schedule contains near-term DTSTART + `RRULE:FREQ=HOURLY`
- first operation self-touches `is_enabled=true` only
- second operation slides same recurring task to returned updated_at+5m
- third operation reads Scheduled Tasks and executes recovery logic
- hourly recurrence survives a pre-slide runtime failure

## New generation18 workflow rule
Before any workflow start/dispatch:
1. search existing runs for the required workflow on the exact required product SHA;
2. consume qualifying SUCCESS regardless of event;
3. observe qualifying queued/in-progress run instead of duplicating it;
4. use authorized rerun-existing capability when appropriate;
5. attempt a new dispatch only when no usable exact-SHA run exists;
6. OWNER_GATE for unavailable dispatch only when a new run is actually required.

## Bootstrap evidence
- current main: `4821fb9a9cd72dd40af2a518962f180fb4344fe7`
- rcodesign Windows Gate run `36771957949`: SUCCESS, event `push`
- verify job: SUCCESS
- signed proof upload: SUCCESS
- Windows Build run `36771957738`: SUCCESS

## Initial mission
Initial Worker B must consume run `36771957949` as an already-satisfied exact-main gate, extract strict primary-SHA256 evidence from logs/artifacts, and continue one bounded product unit toward exact-SHA E2E/root-shell verification.

## OCB
Explicit OSB only; maximum three exact-identical attempts; no attempt4; ambiguous mutable result requires reconciliation.

## Supersession
Packages005 and006 are superseded/terminal and MUST NOT be resumed.

## Launch ordering
1. Publish generation18 capsule.
2. Configure A/B/Watchdog prompts for package007 while disabled.
3. Seed Mailbox and Trace disabled.
4. Arm Watchdog recurring near +5m with hourly RRULE.
5. Final launch operation: arm initial Worker B about +30s.
