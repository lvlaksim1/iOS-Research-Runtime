# Procedural memory

Updated: 2026-09-30 04:05 MSK

- PP-RM generation 16 supersedes generation 15 for new packages.
- Current authorized package is `IOS-M1-CONTINUOUS-005`.
- Topology remains exactly five tasks: Worker A, Worker B, Mailbox, Trace, Watchdog.
- A/B and Watchdog prompts are immutable during a package.
- Watchdog FIRST tool operation is always self-rearm same unchanged task +5 minutes.
- Mailbox is authoritative for baton, frozen mutation descriptor and Watchdog observation state.
- Worker runtime uses ONE initial Scheduled Tasks read; generation 16 does not require a second Scheduled Tasks read before mutable product publication.
- `state=READY` means PREPARE phase. PREPARE may create immutable Git objects but MUST NOT mutate mutable product refs.
- A prepared mutable change is handed to a fresh runtime as `state=MUTATION_READY`.
- Frozen mutation descriptor fields: mutation_id, mutation_operation, mutation_baseline_main_sha, mutation_target_commit, mutation_force.
- Mutation executor's FIRST Scheduled Tasks read is the native ownership fence.
- Mutation executor cannot change/rebuild target; it may publish only frozen target.
- Recovery of the same mutation preserves mutation descriptor exactly even when activation token/message/owner rotates.
- Mutation reconciliation: main==target => success; main==baseline => same frozen mutation may proceed/recover; main neither => FAIL_STOP.
- No GitHub lock/fence ref is used and no extra GitHub request exists solely for fencing.
- dispatch_retry is separate from activation_attempt.
- Scheduler non-delivery does not consume activation_attempt.
- ACKed stall still requires two Watchdog observations.
- OCB remains explicit-OSB only, max 3 exact-identical attempts, no fourth.
- Package 004 is terminal FAIL_STOP and must not be resumed.
- Product main at generation-16 adoption: `95e871e84099f10245e912659b2d964c1b3c1037`.
