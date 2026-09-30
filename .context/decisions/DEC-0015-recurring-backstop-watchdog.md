# DEC-0015 — Recurring-backstop Watchdog

Date: 2026-09-30
Status: ACCEPTED
Authority: direct Owner instruction
Manager generation: 17
Package: `IOS-M1-CONTINUOUS-006`

## Problem
Package 005 could permanently strand when both the current Worker and the one-shot Watchdog path failed before a future Watchdog occurrence had been persisted.

Observed final package005 control-plane state:
- generation 262;
- owner A;
- state READY;
- ACK=NONE;
- Worker A/B disabled;
- Watchdog disabled;
- product main remained unambiguous at `bcde5661...`.

Adding a Lifeboat task would consume another Scheduled Task slot and was rejected as unnecessarily expensive and inelegant.

## Decision
Keep exactly the same five PP-RM objects and make the existing Watchdog a persistent recurring task.

Every armed Watchdog schedule contains a near-term DTSTART and:
`RRULE:FREQ=HOURLY`.

The recurrence is persisted by the scheduler before the runtime executes. Therefore a runtime failure before its first useful operation does not erase all future Watchdog opportunities.

Healthy runtime uses a safe sliding prefix:
1. update the same Watchdog with `is_enabled=true` only, leaving schedule/prompt/title untouched and capturing returned updated_at;
2. compute updated_at+5m;
3. update the same Watchdog to the computed DTSTART while retaining `RRULE:FREQ=HOURLY`;
4. read Scheduled Tasks and run the ordinary Watchdog state machine.

If step 2/3 is lost, the already-existing hourly recurrence survives. Five-minute cadence is an optimization; hourly recurrence is the recovery floor.

## Validation
Isolated tests established:
- recurring schedule survives a completed runtime with no self-rearm;
- a recurring schedule can be moved and its successor is delivered;
- a probe runtime that reached only the safe first self-touch left the recurring schedule enabled, demonstrating graceful degradation when the next update is lost.

## Consequences
- No Lifeboat.
- No sixth task.
- No additional active slot.
- No GitHub lock/fence request.
- Generation-16 two-phase product mutation remains unchanged.
- Package005 is superseded and never resumed.
- Package006 starts from authoritative `main@bcde5661...`.
