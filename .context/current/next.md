# Next actions

Updated: 2026-09-29 22:57 MSK

1. Do nothing operational until the Owner explicitly commands a PP-RM launch.
2. Keep generation-15 PP-RM architecture as the durable accepted construction.
3. Keep package `IOS-M1-CONTINUOUS-004` stopped; do not resume it.
4. On a future explicit launch instruction, configure a clean package `IOS-M1-CONTINUOUS-005` from `main@eaa98114031a37343e0d5184bd132830818a6b2f`.
5. Re-seed Mailbox/Trace cleanly for package 005 and configure immutable A/B and immutable Watchdog prompts.
6. Arm Watchdog before the first worker; Watchdog then self-rearms +5 minutes as the first operation of every invocation.
7. Resume product work from the generation-19 factual checkpoint: narrow source-recovery executable/signature/xattr inventory diagnostic and tests, then exact-SHA CI.
8. Preserve fixed rapid A↔B cadence, fixed 5-minute Watchdog cadence, fencing, dispatch/runtime separation and OCB3.
