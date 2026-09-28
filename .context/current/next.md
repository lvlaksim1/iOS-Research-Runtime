# Next actions

Canonical launch recipe: `.context/pp-rm/LAUNCH_PACKAGE.md`.

1. On explicit Owner launch command, verify external active Scheduled Tasks <= 3.
2. Create exactly five canonical PP-RM objects; leave all disabled.
3. Patch Worker A/B prompts with exact IDs; keep Mailbox/Pulse/Trace disabled.
4. Initialize registers to canonical INIT state.
5. Run `IOS-PP-RM-PILOT-001`: A1 -> B2 -> A3 -> FINAL.
6. During pilot, perform bounded read-only GitHub requests and record OCB telemetry.
7. For explicit OSB, one exact identical retry is desired but not mandatory; record retry or skip reason.
8. After pilot FINAL, do not arm production work. Return to Manager.
9. Manager verifies admission criteria and analyzes Scheduler <-> GitHub passability/OCB results.
10. If needed, adjust OCB policy and seal a new generation.
11. Only after Manager production admission seed and arm `IOS-M1-R1`.
12. Preserve `main` as product authority and `manager-state` as Manager authority.
