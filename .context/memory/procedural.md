# Procedural memory

Updated: 2026-09-30 22:43 MSK

- PP-RM generation17 is active and RUNNING in package `IOS-M1-CONTINUOUS-006`.
- Generation17 supersedes generation16 continuity mechanics while retaining generation16 product mutation semantics.
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
- Watchdog must remain configured as recurring with `RRULE:FREQ=HOURLY`.
- Hourly recurrence is continuity backstop; +5m sliding is the fast path.
- Healthy Watchdog first self-touches `is_enabled=true` only, captures updated_at, then slides DTSTART to updated_at+5m while retaining hourly RRULE.
- Failure before/during sliding must leave the persisted recurrence intact.
- Workers never rewrite the Watchdog prompt.
- dispatch_retry is separate from activation_attempt.
- OCB is explicit OSB only, max three exact-identical attempts, no fourth.
- Product start/main at package006 launch: `bcde5661eab70b6811a5f1fffe0552edaedf980a`.
- Production launch proof includes generation1 B -> generation2 A -> generation3 B handoffs.
- E2E run `36729602541` completed FAILURE at step11; root shell remains unverified.
- Post-merge bash evidence showed SHA1 primary plus SHA256 alternate despite explicit `--digest sha256`.
- Reconciled upstream cause: later `SigningSettings::import_settings_from_macho` can override CLI digest selection and force SHA1 primary for absent/old target metadata.
- Before another E2E, prove SHA256 is actually primary after signing.
