# Next actions

Updated: 2026-09-30 22:30 MSK

1. Publish Manager generation 17 capsule and DEC-0015 atomically to `manager-state`.
2. Configure existing five PP-RM tasks for package `IOS-M1-CONTINUOUS-006` while A/B/Watchdog are disabled.
3. Keep Worker A/B and Watchdog prompts immutable after configuration.
4. Seed Mailbox/Trace from authoritative `main@bcde5661eab70b6811a5f1fffe0552edaedf980a`.
5. Arm Watchdog as recurring: near-term DTSTART plus `RRULE:FREQ=HOURLY`.
6. Final launch operation: arm initial Worker B about +30 seconds.
7. Initial Worker reconciles completed E2E run `36729602541`, extracts failure evidence and records the smallest bounded next product unit.
8. Preserve generation-16 PREPARE/MUTATION_READY protocol, frozen-target recovery, OCB3 and dispatch/runtime separation.
9. Watchdog fast path uses safe self-touch then +5 minute recurring slide; hourly recurrence remains the independent backstop.
10. Do not resume package 005.
