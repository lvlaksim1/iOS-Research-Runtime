# Next actions

Updated: 2026-09-30 04:05 MSK

1. Configure the existing five PP-RM Scheduled Tasks for Manager generation 16 / package `IOS-M1-CONTINUOUS-005`.
2. Keep Worker A/B and Watchdog prompts immutable after configuration.
3. Seed Mailbox/Trace from authoritative `main@95e871e84099f10245e912659b2d964c1b3c1037`.
4. Start generation 1 in PREPARE mode, initial owner Worker B.
5. Arm unchanged Watchdog before the first worker; every Watchdog invocation FIRST self-rearms +5 minutes.
6. PREPARE the narrow post-merge `/bin/bash` CDHash/trust-membership diagnostic and test.
7. PREPARE runtime may create immutable blob/tree/commit objects but MUST NOT update `main`.
8. Publish frozen mutation descriptor as `MUTATION_READY` to a fresh successor runtime.
9. MUTATION runtime uses its first Scheduled Tasks read as the native ownership fence, reconciles main against baseline/target, and publishes only the frozen target with `force=false`.
10. Run exact-SHA CI and continue AMFI/CT diagnosis.
11. Preserve OCB3, fixed rapid A↔B cadence, dispatch/runtime separation and same-generation recovery for failed activations.
