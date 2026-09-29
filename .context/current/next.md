# Next actions

1. Seal Manager generation 15.
2. Reconfigure Worker A/B to package `IOS-M1-CONTINUOUS-004` while keeping immutable slot programs.
3. Reconfigure Mailbox schema with Watchdog state fields.
4. Reconfigure Watchdog as immutable and require +5 minute self-rearm as its FIRST tool operation.
5. Remove worker-side Watchdog prompt rewriting.
6. Initialize package `IOS-M1-CONTINUOUS-004` from `main@eaa98114031a37343e0d5184bd132830818a6b2f`.
7. Arm Watchdog before the first worker.
8. Start first production unit from the generation-19 factual checkpoint: add narrow source-recovery executable/signature inventory diagnostic and tests.
9. Continue exact-SHA CI and AMFI / CT launch-constraint work with no artificial stops.
10. Preserve fixed rapid A↔B cadence and fixed 5-minute Watchdog cadence.
