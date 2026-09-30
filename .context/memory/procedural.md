# Procedural memory

Updated: 2026-09-30 23:39 MSK

- PP-RM generation18 supersedes generation17 for new packages while retaining generation17 Watchdog continuity and generation16 product mutation semantics.
- Current authorized package is `IOS-M1-CONTINUOUS-007`.
- Package005 is stranded/superseded and must not resume.
- Package006 is terminal `FAIL_STOP_OWNER_GATE` and must not resume.
- Topology is exactly five tasks: Worker A, Worker B, Mailbox, Trace, Watchdog.
- A/B and Watchdog prompts are immutable during an active package.
- Mailbox is authoritative for baton, frozen mutation descriptor and Watchdog observation state.
- READY means PREPARE; PREPARE may create immutable Git objects but cannot move mutable refs.
- Prepared mutable change is handed to a fresh MUTATION_READY runtime.
- Mutation reconciliation: main==target success; main==baseline same frozen attempt eligible; neither FAIL_STOP.
- Watchdog remains recurring with `RRULE:FREQ=HOURLY`; +5m sliding is the fast path.
- Workflow gates are result-first.
- Always search existing exact-SHA workflow runs before considering dispatch.
- A qualifying exact-SHA SUCCESS satisfies the gate regardless of trigger event unless trigger semantics are explicitly part of the test.
- Observe queued/in-progress qualifying runs instead of duplicating them.
- Use authorized rerun-existing capability where appropriate before requiring start-new-workflow.
- Missing dispatch capability is an OWNER_GATE only when no usable exact-SHA run exists and a new run is truly required.
- Exact-main `rcodesign Windows Gate` run `36771957949` on `4821fb9a...` is SUCCESS.
- Exact-main Windows Build `36771957738` is SUCCESS.
- Package007 first work is to extract strict primary-SHA256 evidence from the successful gate, then continue exact-SHA E2E/root-shell work.
- dispatch_retry is separate from activation_attempt.
- OCB is explicit OSB only, max three exact-identical attempts, no fourth.
