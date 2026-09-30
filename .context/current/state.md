# Current state

Updated: 2026-09-30 22:30 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 17
- product authority: `main`
- PP-RM version: generation 17 recurring-backstop Watchdog over generation-16 native two-phase mutation
- execution status: OWNER-AUTHORIZED / CONFIGURE AND LAUNCH
- active package: `IOS-M1-CONTINUOUS-006`

## Product
- live main: `bcde5661eab70b6811a5f1fffe0552edaedf980a`
- latest exact-head Windows E2E: run `36729602541`, completed FAILURE
- failing step: 11, `Run provisioning and Darwin root-shell proof`
- steps 1–10: SUCCESS
- failure evidence collection: SUCCESS
- end-to-end evidence upload: SUCCESS
- current product blocker remains recovery executable trust/signature/AMFI-CT path to verified root shell
- no ambiguous product ref mutation is currently known in flight

## Package 005 stop evidence
Package `IOS-M1-CONTINUOUS-005` progressed through runtime generation 262 and then stranded:
- Mailbox: generation 262, owner A, READY, activation_attempt=1, ACK=NONE
- Worker A/B disabled
- Watchdog disabled
- Watchdog one-shot schedule had no persisted successor
- product main remained `bcde5661...`

This package is superseded and MUST NOT be resumed.

## PP-RM generation 17
Generation 17 retains native two-phase mutation semantics and changes only continuity.

The Watchdog is always scheduled with `RRULE:FREQ=HOURLY` plus a near-term DTSTART.
A runtime failure before self-scheduling therefore cannot remove all future Watchdog occurrences.

Healthy Watchdog runtime:
1. schedule-preserving self-touch (`is_enabled=true` only), capture returned updated_at;
2. slide the same recurring Watchdog to updated_at+5m while retaining hourly RRULE;
3. read Scheduled Tasks and execute normal recovery logic.

If sliding is lost, hourly recurrence remains.
No extra task, no extra active slot, no GitHub continuity request.

Owner explicitly approved conversion to v17, capsule update and cycle launch.
