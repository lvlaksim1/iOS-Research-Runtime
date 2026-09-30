# Latest handoff

Updated: 2026-09-30 22:30 MSK

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 17.
Product authority: `main@bcde5661eab70b6811a5f1fffe0552edaedf980a`.
Owner authority: direct instruction to convert PP-RM to v17, update capsules, and launch the cycle.

## Superseded package
`IOS-M1-CONTINUOUS-005` is stranded/superseded at runtime generation 262 and must not be resumed.
Observed control plane: owner A, READY, ACK=NONE; A/B/Watchdog disabled.
No ambiguous product ref side effect is indicated; authoritative main is `bcde5661...`.

## Generation 17 / package 006
Package: `IOS-M1-CONTINUOUS-006`.

Preserved:
- exactly five PP-RM tasks;
- immutable A/B prompts;
- immutable Watchdog prompt;
- generation-16 READY/PREPARE and MUTATION_READY two-phase mutation;
- frozen mutation descriptor;
- force=false publication;
- dispatch_retry separate from activation_attempt;
- same-generation recovery;
- OCB3.

Changed:
- Watchdog task is always recurring with `RRULE:FREQ=HOURLY`;
- recurrence is the persistent survival backstop;
- healthy Watchdog first performs a schedule-preserving self-touch, then slides the same recurring task by +5 minutes using the first update's returned timestamp;
- if runtime dies before sliding, the hourly recurrence survives;
- no Lifeboat, no sixth task, no extra slot, no GitHub continuity fence.

## Evidence
Isolated recurrence tests on 2026-09-30 showed:
- a recurring task remains enabled after a runtime that does not self-rearm;
- explicit recurring schedule shift executes and the next occurrence is delivered;
- a runtime that performed only the safe first self-touch did not erase recurrence.

## Product checkpoint
Exact-head E2E run `36729602541` on `bcde5661...` completed FAILURE at step 11; failure evidence collection and upload succeeded.
First package006 work: reconcile/extract that evidence and continue the AMFI/CT/root-shell diagnosis with one bounded unit.
