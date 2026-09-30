# Procedural memory

Updated: 2026-09-30 22:30 MSK

- PP-RM generation 17 supersedes generation 16 for new packages while retaining generation-16 product mutation semantics.
- Current authorized package is `IOS-M1-CONTINUOUS-006`.
- Package `IOS-M1-CONTINUOUS-005` is stranded/superseded and must not be resumed.
- Topology is exactly five tasks: Worker A, Worker B, Mailbox, Trace, Watchdog.
- A/B and Watchdog prompts are immutable during a package.
- Mailbox is authoritative for baton, frozen mutation descriptor and Watchdog observation state.
- Worker runtime uses one initial Scheduled Tasks read.
- READY means PREPARE; PREPARE may create immutable Git objects but cannot move mutable refs.
- Prepared mutable change is handed to a fresh MUTATION_READY runtime.
- Frozen descriptor: mutation_id, mutation_operation, mutation_baseline_main_sha, mutation_target_commit, mutation_force.
- Mutation executor cannot rebuild target and may publish only frozen target.
- Mutation reconciliation: main==target success; main==baseline same frozen attempt eligible; neither FAIL_STOP.
- Watchdog must always be configured as a recurring task with `RRULE:FREQ=HOURLY`.
- Hourly recurrence is continuity backstop; +5m sliding is a fast path.
- Watchdog runtime first self-touches with `is_enabled=true` only, preserving recurrence and obtaining a current updated_at; if alive, second update sets DTSTART=updated_at+5m while retaining hourly RRULE.
- Failure before/after the safe self-touch but before sliding must leave the persisted recurrence intact.
- Workers never rewrite Watchdog prompt.
- dispatch_retry is separate from activation_attempt.
- OCB is explicit OSB only, max three exact-identical attempts, no fourth.
- Product start for package006: `bcde5661eab70b6811a5f1fffe0552edaedf980a`.
- E2E run `36729602541` completed FAILURE at step11; failure evidence collection/upload succeeded.
